"""Message Router Service - Routes messages to appropriate services."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from typing import Optional, Dict, Any
import re
import asyncio
from datetime import datetime

from backend.shared.models import (
    SMSMessage, ProcessedMessage, MessageType, MessagePriority,
    LLMRequest, LLMResponse, RAGQuery, ServiceHealth
)
from backend.shared.config import settings
from backend.shared.logging import setup_logger

logger = setup_logger("message-router")


class MessageRouter:
    """Routes messages to appropriate processing services."""
    
    def __init__(self):
        self.llm_service_url = f"http://localhost:{settings.llm_inference_port}"
        self.rag_service_url = f"http://localhost:{settings.rag_service_port}"
        self.privacy_service_url = f"http://localhost:{settings.privacy_filter_port}"
        self.sms_gateway_url = f"http://localhost:{settings.sms_gateway_port}"
        
        # Processing statistics
        self.stats = {
            "total_messages": 0,
            "emergency_messages": 0,
            "query_messages": 0,
            "command_messages": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "rag_queries": 0,
            "llm_queries": 0
        }
        
        # Emergency keywords
        self.emergency_keywords = ["emergency", "help", "urgent", "911", "danger", "fire", "medical"]
        
        # Response templates
        self.response_templates = {
            "emergency": "Emergency alert received. Help is being dispatched. Stay calm.",
            "command": "Command processing not yet implemented.",
            "error": "Sorry, I encountered an error. Please try again.",
            "offline": "System is currently offline. Please try again later.",
            "rate_limited": "Too many requests. Please wait a moment before trying again."
        }
    
    def classify_message(self, message: SMSMessage) -> ProcessedMessage:
        """Classify message type and determine routing."""
        content_lower = message.content.lower()
        
        # Use parsing information from SMS gateway if available
        parsed_info = message.metadata.get('parsed', {}) if message.metadata else {}
        
        # Determine message type from parsed info or fallback to simple classification
        if parsed_info:
            intent = parsed_info.get('intent', 'unknown')
            category = parsed_info.get('category', 'general')
            priority = parsed_info.get('priority', 'normal')
            requires_rag = parsed_info.get('requires_rag', False)
            requires_llm = parsed_info.get('requires_llm', True)
            
            # Map intent to message type
            if intent == 'emergency':
                message_type = MessageType.EMERGENCY
                priority_level = MessagePriority.EMERGENCY
                requires_llm = False
            elif intent == 'command':
                message_type = MessageType.COMMAND
                priority_level = MessagePriority.HIGH
                requires_llm = False
            elif intent == 'greeting':
                message_type = MessageType.TEMPLATE
                priority_level = MessagePriority.LOW
            else:
                message_type = MessageType.QUERY
                priority_level = getattr(MessagePriority, priority.upper(), MessagePriority.NORMAL)
            
            # Extract entities for additional context
            entities = parsed_info.get('entities', {})
            
            return ProcessedMessage(
                original_message=message,
                message_type=message_type,
                intent=intent,
                entities=entities,
                requires_rag=requires_rag,
                requires_llm=requires_llm,
                priority=priority_level
            )
        
        # Fallback to simple classification if no parsed info
        # Check for emergency
        is_emergency = any(keyword in content_lower for keyword in self.emergency_keywords)
        if is_emergency:
            return ProcessedMessage(
                original_message=message,
                message_type=MessageType.EMERGENCY,
                priority=MessagePriority.EMERGENCY,
                requires_llm=False
            )
        
        # Check for commands (starts with /)
        if content_lower.startswith("/"):
            return ProcessedMessage(
                original_message=message,
                message_type=MessageType.COMMAND,
                priority=MessagePriority.HIGH,
                requires_llm=False
            )
        
        # Check if query likely needs RAG (contains questions)
        question_words = ["what", "where", "when", "who", "why", "how", "?"]
        needs_rag = any(word in content_lower for word in question_words)
        
        # Default to query with LLM
        return ProcessedMessage(
            original_message=message,
            message_type=MessageType.QUERY,
            priority=MessagePriority.NORMAL,
            requires_rag=needs_rag,
            requires_llm=True
        )
    
    async def route_to_llm(self, processed: ProcessedMessage, context: Optional[str] = None) -> str:
        """Route message to LLM service."""
        try:
            llm_request = LLMRequest(
                prompt=processed.original_message.content,
                context=context,
                max_length=160
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.llm_service_url}/inference",
                    json=llm_request.model_dump(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    llm_response = LLMResponse(**response.json())
                    return llm_response.response
                else:
                    logger.error(f"LLM service error: {response.status_code}")
                    return "I'm having trouble processing your request right now. Please try again later."
        except Exception as e:
            logger.error(f"Error calling LLM service: {e}")
            return "Service temporarily unavailable. Please try again."
    
    async def route_to_rag(self, query: str) -> Optional[str]:
        """Route query to RAG service for context retrieval."""
        try:
            rag_query = RAGQuery(query=query, top_k=3)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_service_url}/search",
                    json=rag_query.model_dump(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    rag_result = response.json()
                    # Combine documents into context
                    documents = rag_result.get("documents", [])
                    if documents:
                        return " ".join(documents[:2])  # Use top 2 results
                return None
        except Exception as e:
            logger.error(f"Error calling RAG service: {e}")
            return None
    
    async def send_response(self, original_message: SMSMessage, response_text: str) -> None:
        """Send response back via SMS gateway."""
        try:
            # Truncate to SMS limit
            if len(response_text) > 160:
                response_text = response_text[:157] + "..."
            
            response_message = SMSMessage(
                sender=original_message.receiver,  # System number
                receiver=original_message.sender,  # Original sender
                content=response_text
            )
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.sms_gateway_url}/sms/send",
                    json=response_message.model_dump(mode='json'),
                    timeout=10.0
                )
                
            logger.info(f"Response sent to {response_message.receiver}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    async def process_message(self, message: SMSMessage) -> dict:
        """Main message processing pipeline."""
        start_time = datetime.utcnow()
        
        try:
            # Update statistics
            self.stats["total_messages"] += 1
            
            # Classify message
            processed = self.classify_message(message)
            logger.info(f"Message classified as: {processed.message_type} (priority: {processed.priority})")
            
            # Update type-specific statistics
            if processed.message_type == MessageType.EMERGENCY:
                self.stats["emergency_messages"] += 1
            elif processed.message_type == MessageType.QUERY:
                self.stats["query_messages"] += 1
            elif processed.message_type == MessageType.COMMAND:
                self.stats["command_messages"] += 1
            
            # Handle different message types
            if processed.message_type == MessageType.EMERGENCY:
                response = await self._handle_emergency(message, processed)
                await self.send_response(message, response)
                self.stats["successful_responses"] += 1
                return {"status": "emergency_handled", "response": response}
            
            elif processed.message_type == MessageType.COMMAND:
                response = await self._handle_command(message, processed)
                await self.send_response(message, response)
                self.stats["successful_responses"] += 1
                return {"status": "command_handled", "response": response}
            
            elif processed.message_type == MessageType.TEMPLATE:
                response = await self._handle_template(message, processed)
                await self.send_response(message, response)
                self.stats["successful_responses"] += 1
                return {"status": "template_handled", "response": response}
            
            else:
                # Get RAG context if needed
                context = None
                if processed.requires_rag:
                    self.stats["rag_queries"] += 1
                    context = await self.route_to_rag(message.content)
                    logger.info(f"RAG context retrieved: {bool(context)}")
                
                # Get LLM response
                if processed.requires_llm:
                    self.stats["llm_queries"] += 1
                    response = await self.route_to_llm(processed, context)
                    await self.send_response(message, response)
                    self.stats["successful_responses"] += 1
                    
                    processing_time = (datetime.utcnow() - start_time).total_seconds()
                    return {
                        "status": "processed", 
                        "response": response,
                        "processing_time": processing_time,
                        "used_rag": bool(context),
                        "intent": processed.intent
                    }
                
                return {"status": "no_action", "message": "No processing required"}
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats["failed_responses"] += 1
            error_response = self.response_templates["error"]
            await self.send_response(message, error_response)
            return {"status": "error", "error": str(e)}
    
    async def _handle_emergency(self, message: SMSMessage, processed: ProcessedMessage) -> str:
        """Handle emergency messages."""
        # Log emergency details
        logger.critical(f"EMERGENCY MESSAGE from {message.sender}: {message.content}")
        
        # Could trigger external emergency systems here
        # For now, return standard emergency response
        
        # Check if it's a medical emergency
        if any(word in message.content.lower() for word in ["medical", "hospital", "ambulance", "heart", "stroke"]):
            return "Medical emergency received. Emergency services are being notified. Stay with the person if safe to do so."
        
        # Check if it's a fire emergency
        elif any(word in message.content.lower() for word in ["fire", "smoke", "burning"]):
            return "Fire emergency received. Fire department is being notified. Evacuate immediately if safe to do so."
        
        # Generic emergency response
        return self.response_templates["emergency"]
    
    async def _handle_command(self, message: SMSMessage, processed: ProcessedMessage) -> str:
        """Handle command messages."""
        command = message.content.lower().strip()
        
        # Parse command
        if command.startswith("/help"):
            return "Available commands: /help, /status, /weather, /news. More coming soon!"
        elif command.startswith("/status"):
            return f"System status: Healthy. Processed {self.stats['total_messages']} messages today."
        elif command.startswith("/weather"):
            return "Weather service not yet available. Try asking 'What's the weather?' instead."
        elif command.startswith("/news"):
            return "News service not yet available. Try asking 'What's the latest news?' instead."
        else:
            return self.response_templates["command"]
    
    async def _handle_template(self, message: SMSMessage, processed: ProcessedMessage) -> str:
        """Handle template messages like greetings."""
        if processed.intent == "greeting":
            # Simple greeting responses
            greeting_responses = [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Good day! I'm here to assist you.",
                "Hello! Ask me anything you need help with."
            ]
            import random
            return random.choice(greeting_responses)
        
        return "Thank you for your message. How can I assist you?"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.stats,
            "uptime": "Service running",
            "last_updated": datetime.utcnow().isoformat()
        }


# Global router instance
message_router = MessageRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("Message Router Service starting up...")
    yield
    logger.info("Message Router Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="EVY Message Router Service",
    description="Routes messages to appropriate processing services",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint."""
    stats = message_router.get_statistics()
    return ServiceHealth(
        service_name="message-router",
        status="healthy",
        version="1.0.0",
        details={
            "statistics": stats,
            "services": {
                "llm_service": message_router.llm_service_url,
                "rag_service": message_router.rag_service_url,
                "privacy_service": message_router.privacy_service_url,
                "sms_gateway": message_router.sms_gateway_url
            }
        }
    )


@app.post("/route")
async def route_message(message: SMSMessage):
    """Route an incoming message."""
    result = await message_router.process_message(message)
    return result


@app.post("/classify")
async def classify_message(message: SMSMessage):
    """Classify a message without processing."""
    processed = message_router.classify_message(message)
    return processed


@app.get("/statistics")
async def get_statistics():
    """Get processing statistics."""
    return message_router.get_statistics()


@app.get("/services/status")
async def get_services_status():
    """Check status of connected services."""
    service_status = {}
    
    async with httpx.AsyncClient() as client:
        # Check LLM service
        try:
            response = await client.get(f"{message_router.llm_service_url}/health", timeout=5.0)
            service_status["llm_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
            }
        except Exception as e:
            service_status["llm_service"] = {"status": "unreachable", "error": str(e)}
        
        # Check RAG service
        try:
            response = await client.get(f"{message_router.rag_service_url}/health", timeout=5.0)
            service_status["rag_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
            }
        except Exception as e:
            service_status["rag_service"] = {"status": "unreachable", "error": str(e)}
        
        # Check SMS Gateway
        try:
            response = await client.get(f"{message_router.sms_gateway_url}/health", timeout=5.0)
            service_status["sms_gateway"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
            }
        except Exception as e:
            service_status["sms_gateway"] = {"status": "unreachable", "error": str(e)}
    
    return service_status


@app.post("/test/emergency")
async def test_emergency_flow():
    """Test emergency message processing."""
    test_message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="EMERGENCY! Fire in building!",
        priority=MessagePriority.EMERGENCY
    )
    
    result = await message_router.process_message(test_message)
    return {"test_result": result}


@app.post("/test/query")
async def test_query_flow():
    """Test query message processing."""
    test_message = SMSMessage(
        sender="+1234567890",
        receiver="+0987654321",
        content="What's the weather like today?",
        priority=MessagePriority.NORMAL
    )
    
    result = await message_router.process_message(test_message)
    return {"test_result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.message_router_port,
        log_level="info"
    )


