"""End-to-End Message Flow Integration

Integrates Rust services (SMS Gateway, Compression, Router) with Python services
(LLM, RAG) to create a complete message processing pipeline.
"""

import asyncio
import httpx
from typing import Dict, Optional, Any
from datetime import datetime
import logging

from backend.shared.models import SMSMessage, MessagePriority
from backend.shared.integration.rust_services import RustServicesManager
from backend.shared.integration.service_discovery import get_service_registry

logger = logging.getLogger(__name__)


class MessageFlowPipeline:
    """End-to-end message processing pipeline"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rust_services = RustServicesManager(self.config.get('rust_services', {}))
        self.service_registry = get_service_registry()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the message flow pipeline"""
        try:
            # Initialize Rust services
            rust_ok = await self.rust_services.initialize()
            
            # Initialize service discovery
            await initialize_service_discovery(self.config)
            
            self._initialized = rust_ok
            logger.info(f"Message Flow Pipeline initialized: Rust={rust_ok}")
            return self._initialized
        except Exception as e:
            logger.error(f"Failed to initialize Message Flow Pipeline: {e}")
            return False
    
    async def process_message(self, message: SMSMessage) -> Dict[str, Any]:
        """Process a message through the complete pipeline"""
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Route message (Rust Message Router)
            route_result = await self.rust_services.router_service.route(
                sender=message.sender,
                content=message.content
            )
            
            logger.info(f"Message routed to: {route_result['service_type']}")
            
            # Step 2: Classify message (Rust Message Router)
            classification = await self.rust_services.router_service.classify(message.content)
            
            # Step 3: Handle emergency messages immediately
            if classification['intent'] == 'Emergency':
                return await self._handle_emergency(message, classification)
            
            # Step 4: Get RAG context if needed
            context = None
            if route_result.get('requires_rag', False):
                context = await self._get_rag_context(message.content)
            
            # Step 5: Get LLM response if needed
            response_text = None
            if route_result.get('requires_llm', False):
                response_text = await self._get_llm_response(
                    message.content,
                    context=context
                )
            else:
                # Use template response for commands/greetings
                response_text = await self._get_template_response(classification)
            
            # Step 6: Compress response (Rust Compression Engine)
            if response_text:
                compressed = await self.rust_services.compression_service.compress(
                    response_text,
                    target_length=160  # SMS limit
                )
            else:
                compressed = "Sorry, I couldn't process your request."
            
            # Step 7: Send response (Rust SMS Gateway)
            message_id = await self.rust_services.sms_service.send_sms(
                phone_number=message.sender,
                content=compressed,
                priority=self._map_priority(classification.get('priority', 'Normal'))
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'message_id': message_id,
                'processing_time': processing_time,
                'route': route_result,
                'classification': classification,
                'compressed_length': len(compressed),
                'original_length': len(response_text) if response_text else 0,
            }
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Try to send error response
            try:
                await self.rust_services.sms_service.send_sms(
                    phone_number=message.sender,
                    content="Sorry, I encountered an error. Please try again.",
                    priority=1
                )
            except:
                pass
            
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': processing_time,
            }
    
    async def _handle_emergency(
        self,
        message: SMSMessage,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle emergency messages"""
        logger.critical(f"EMERGENCY MESSAGE from {message.sender}: {message.content}")
        
        # Emergency response template
        emergency_responses = {
            'medical': "Medical emergency received. Emergency services notified. Stay with person if safe.",
            'fire': "Fire emergency received. Fire department notified. Evacuate immediately if safe.",
            'general': "Emergency alert received. Help is being dispatched. Stay calm.",
        }
        
        content_lower = message.content.lower()
        if any(word in content_lower for word in ['medical', 'hospital', 'ambulance', 'heart', 'stroke']):
            response_text = emergency_responses['medical']
        elif any(word in content_lower for word in ['fire', 'smoke', 'burning']):
            response_text = emergency_responses['fire']
        else:
            response_text = emergency_responses['general']
        
        # Send emergency response immediately (no compression for emergencies)
        message_id = await self.rust_services.sms_service.send_sms(
            phone_number=message.sender,
            content=response_text,
            priority=3  # Emergency priority
        )
        
        return {
            'status': 'emergency_handled',
            'message_id': message_id,
            'response': response_text,
            'priority': 'Emergency',
        }
    
    async def _get_rag_context(self, query: str) -> Optional[str]:
        """Get RAG context for query"""
        try:
            rag_service = self.service_registry.get_service('rag_service')
            if not rag_service or rag_service.status.value != 'healthy':
                logger.warning("RAG service not available")
                return None
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{rag_service.url}/search",
                    json={'query': query, 'top_k': 3},
                )
                
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get('documents', [])
                    if documents:
                        return " ".join(documents[:2])  # Use top 2 results
            
            return None
        except Exception as e:
            logger.error(f"RAG context retrieval failed: {e}")
            return None
    
    async def _get_llm_response(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> str:
        """Get LLM response"""
        try:
            llm_service = self.service_registry.get_service('llm_service')
            if not llm_service or llm_service.status.value != 'healthy':
                logger.warning("LLM service not available")
                return "Service temporarily unavailable. Please try again later."
            
            request_data = {
                'prompt': prompt,
                'max_length': 160,
            }
            if context:
                request_data['context'] = context
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{llm_service.url}/inference",
                    json=request_data,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', 'No response generated')
            
            return "I couldn't generate a response. Please try again."
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            return "Service error. Please try again later."
    
    async def _get_template_response(self, classification: Dict[str, Any]) -> str:
        """Get template response for non-LLM intents"""
        intent = classification.get('intent', 'Unknown')
        
        templates = {
            'Greeting': [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Good day! I'm here to assist you.",
            ],
            'Command': "Command processing not yet fully implemented.",
            'Unknown': "I'm not sure how to help with that. Can you rephrase?",
        }
        
        if intent == 'Greeting':
            import random
            return random.choice(templates['Greeting'])
        
        return templates.get(intent, templates['Unknown'])
    
    def _map_priority(self, priority_str: str) -> int:
        """Map priority string to integer"""
        priority_map = {
            'Low': 0,
            'Normal': 1,
            'High': 2,
            'Emergency': 3,
        }
        return priority_map.get(priority_str, 1)
    
    async def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics from the pipeline"""
        rust_stats = await self.rust_services.get_all_stats()
        service_stats = self.service_registry.get_service_stats()
        
        return {
            'rust_services': rust_stats,
            'service_discovery': service_stats,
            'initialized': self._initialized,
        }

