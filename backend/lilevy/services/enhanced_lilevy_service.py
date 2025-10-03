"""Enhanced lilEVY Service with LoRa Radio Integration."""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.shared.models import LLMRequest, LLMResponse, RAGQuery, RAGResult, SMSMessage, ServiceHealth
from backend.shared.communication.smart_router import SmartCommunicationRouter, QueryContext, QueryType, QueryComplexity
from backend.shared.logging import setup_logger

logger = setup_logger("enhanced-lilevy")

class EnhancedLilEVYService:
    """Enhanced lilEVY service with LoRa radio and smart routing capabilities."""
    
    def __init__(self, node_id: str = "lilevy-001"):
        self.node_id = node_id
        self.is_initialized = False
        
        # Core services
        self.smart_router: Optional[SmartCommunicationRouter] = None
        self.lora_radio = None
        self.sms_gateway = None
        self.llm_service = None
        self.rag_service = None
        
        # Service components
        self.services = {}
        self.service_health = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "local_requests": 0,
            "routed_requests": 0,
            "emergency_requests": 0,
            "lora_messages": 0,
            "sms_messages": 0,
            "mesh_nodes_discovered": 0,
            "last_request_time": None,
            "uptime": 0.0,
            "start_time": time.time()
        }
        
        # Configuration
        self.config = {
            "max_local_processing_time": 10.0,  # seconds
            "emergency_response_time": 5.0,  # seconds
            "mesh_discovery_interval": 30,  # seconds
            "health_check_interval": 60,  # seconds
            "max_concurrent_requests": 10
        }
        
        # Request queue
        self.request_queue = asyncio.Queue()
        self.active_requests = {}
        
    async def initialize(self) -> bool:
        """Initialize enhanced lilEVY service."""
        try:
            logger.info(f"Initializing Enhanced lilEVY Service for node {self.node_id}")
            
            # Initialize smart communication router
            self.smart_router = SmartCommunicationRouter(self.node_id)
            if not await self.smart_router.initialize():
                logger.error("Failed to initialize smart router")
                return False
            
            # Initialize LoRa radio service
            await self._initialize_lora_radio()
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Register message handlers
            await self._register_message_handlers()
            
            # Start background tasks
            asyncio.create_task(self._request_processing_loop())
            asyncio.create_task(self._mesh_discovery_loop())
            asyncio.create_task(self._health_monitoring_loop())
            asyncio.create_task(self._statistics_update_loop())
            
            self.is_initialized = True
            self.stats["uptime"] = time.time() - self.stats["start_time"]
            
            logger.info("Enhanced lilEVY Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced lilEVY Service: {e}")
            return False
    
    async def _initialize_lora_radio(self):
        """Initialize LoRa radio service."""
        try:
            from backend.lilevy.services.lora_radio_service import lora_radio_service
            
            if await lora_radio_service.initialize():
                self.lora_radio = lora_radio_service
                logger.info("LoRa radio service initialized")
            else:
                logger.warning("LoRa radio service initialization failed")
                
        except ImportError as e:
            logger.warning(f"LoRa radio service not available: {e}")
    
    async def _initialize_core_services(self):
        """Initialize core lilEVY services."""
        try:
            # Initialize SMS Gateway
            from backend.services.sms_gateway.main import sms_gateway
            self.sms_gateway = sms_gateway
            self.services["sms_gateway"] = sms_gateway
            
            # Initialize LLM Service
            from backend.services.llm_inference.main import llm_inference_engine
            self.llm_service = llm_inference_engine
            self.services["llm_service"] = llm_inference_engine
            
            # Initialize RAG Service
            from backend.services.rag_service.main import rag_service
            self.rag_service = rag_service
            self.services["rag_service"] = rag_service
            
            logger.info("Core services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize core services: {e}")
            raise
    
    async def _register_message_handlers(self):
        """Register message handlers for LoRa communication."""
        if self.lora_radio:
            # Register handlers for different message types
            self.lora_radio.register_message_handler(
                MessageType.DATA, self._handle_data_message
            )
            self.lora_radio.register_message_handler(
                MessageType.SYNC, self._handle_sync_message
            )
            self.lora_radio.register_message_handler(
                MessageType.EMERGENCY, self._handle_emergency_message
            )
            self.lora_radio.register_message_handler(
                MessageType.DISCOVERY, self._handle_discovery_message
            )
            
            # Register discovery callback
            self.lora_radio.register_discovery_callback(self._on_node_discovered)
            
            logger.info("Message handlers registered")
    
    async def process_sms_request(self, sms_message: SMSMessage) -> SMSMessage:
        """Process incoming SMS request with smart routing."""
        try:
            self.stats["total_requests"] += 1
            self.stats["last_request_time"] = time.time()
            
            # Create query context
            context = await self._create_query_context(sms_message)
            
            # Determine if we can handle locally or need to route
            if await self._can_handle_locally(sms_message, context):
                # Handle locally
                response = await self._handle_local_request(sms_message, context)
                self.stats["local_requests"] += 1
            else:
                # Route to appropriate node
                response = await self._handle_routed_request(sms_message, context)
                self.stats["routed_requests"] += 1
            
            # Update statistics
            if context.query_type == QueryType.EMERGENCY_ALERT:
                self.stats["emergency_requests"] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process SMS request: {e}")
            return SMSMessage(
                phone_number=sms_message.phone_number,
                content="I'm experiencing technical difficulties. Please try again later.",
                timestamp=datetime.now()
            )
    
    async def _create_query_context(self, sms_message: SMSMessage) -> QueryContext:
        """Create query context from SMS message."""
        # Analyze message content to determine query type and complexity
        content = sms_message.content.lower()
        
        # Determine query type
        if any(keyword in content for keyword in ["emergency", "help", "urgent", "crisis"]):
            query_type = QueryType.EMERGENCY_ALERT
            complexity = QueryComplexity.EMERGENCY
            priority = 0
            emergency_level = 1
        elif any(keyword in content for keyword in ["what", "how", "why", "explain", "tell me"]):
            query_type = QueryType.LLM_REQUEST
            complexity = QueryComplexity.MEDIUM
            priority = 2
            emergency_level = 0
        elif any(keyword in content for keyword in ["where", "when", "who", "contact", "phone", "address"]):
            query_type = QueryType.RAG_QUERY
            complexity = QueryComplexity.SIMPLE
            priority = 3
            emergency_level = 0
        else:
            query_type = QueryType.LLM_REQUEST
            complexity = QueryComplexity.SIMPLE
            priority = 3
            emergency_level = 0
        
        return QueryContext(
            query_type=query_type,
            complexity=complexity,
            priority=priority,
            user_location=None,  # Would get from GPS if available
            source_node=self.node_id,
            timestamp=time.time(),
            size_estimate=len(sms_message.content),
            requires_response=True,
            emergency_level=emergency_level
        )
    
    async def _can_handle_locally(self, sms_message: SMSMessage, context: QueryContext) -> bool:
        """Determine if request can be handled locally."""
        # Emergency requests should always be handled locally first
        if context.emergency_level > 0:
            return True
        
        # Simple queries can be handled locally
        if context.complexity == QueryComplexity.SIMPLE:
            return True
        
        # Check if we have the required capabilities
        if context.query_type == QueryType.LLM_REQUEST:
            return self.llm_service is not None
        elif context.query_type == QueryType.RAG_QUERY:
            return self.rag_service is not None
        
        return False
    
    async def _handle_local_request(self, sms_message: SMSMessage, context: QueryContext) -> SMSMessage:
        """Handle request locally."""
        try:
            start_time = time.time()
            
            if context.query_type == QueryType.LLM_REQUEST:
                # Handle with LLM service
                llm_request = LLMRequest(
                    prompt=sms_message.content,
                    max_tokens=160,  # SMS limit
                    temperature=0.7
                )
                
                llm_response = await self.llm_service.generate_response(llm_request)
                
                response_content = llm_response.response
                
            elif context.query_type == QueryType.RAG_QUERY:
                # Handle with RAG service
                rag_query = RAGQuery(
                    query=sms_message.content,
                    top_k=3
                )
                
                rag_result = await self.rag_service.search(rag_query)
                
                if rag_result.documents:
                    # Format RAG results for SMS
                    response_content = self._format_rag_response(rag_result)
                else:
                    response_content = "I don't have specific information about that. Let me try to find more details."
            
            else:
                response_content = "I'm not sure how to help with that request."
            
            # Truncate to SMS limit
            if len(response_content) > 160:
                response_content = response_content[:157] + "..."
            
            processing_time = time.time() - start_time
            logger.info(f"Local request processed in {processing_time:.2f}s")
            
            return SMSMessage(
                phone_number=sms_message.phone_number,
                content=response_content,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to handle local request: {e}")
            return SMSMessage(
                phone_number=sms_message.phone_number,
                content="I encountered an error processing your request.",
                timestamp=datetime.now()
            )
    
    async def _handle_routed_request(self, sms_message: SMSMessage, context: QueryContext) -> SMSMessage:
        """Handle request by routing to appropriate node."""
        try:
            # Get routing decision
            routing_decision = await self.smart_router.route_query(sms_message, context)
            
            logger.info(f"Routing request via {routing_decision.layer.value}: {routing_decision.reason}")
            
            # Route based on decision
            if routing_decision.layer.value == "lora":
                response = await self._route_via_lora(sms_message, context, routing_decision)
                self.stats["lora_messages"] += 1
            elif routing_decision.layer.value == "internet":
                response = await self._route_via_internet(sms_message, context, routing_decision)
            else:
                response = await self._route_via_sms(sms_message, context, routing_decision)
                self.stats["sms_messages"] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to handle routed request: {e}")
            # Fallback to local processing
            return await self._handle_local_request(sms_message, context)
    
    async def _route_via_lora(self, sms_message: SMSMessage, context: QueryContext, 
                            routing_decision) -> SMSMessage:
        """Route request via LoRa mesh network."""
        try:
            if not self.lora_radio:
                raise Exception("LoRa radio not available")
            
            # Create LoRa message
            from backend.lilevy.services.lora_radio_service import LoRaMessage, MessageType, MessagePriority
            
            lora_message = LoRaMessage(
                message_type=MessageType.DATA,
                priority=MessagePriority(routing_decision.priority),
                source_node=self.node_id,
                destination_node=routing_decision.target_node or "broadcast",
                payload={
                    "sms_message": {
                        "phone_number": sms_message.phone_number,
                        "content": sms_message.content,
                        "timestamp": sms_message.timestamp.isoformat()
                    },
                    "context": {
                        "query_type": context.query_type.value,
                        "complexity": context.complexity.value,
                        "priority": context.priority,
                        "emergency_level": context.emergency_level
                    },
                    "request_id": f"{self.node_id}_{int(time.time())}"
                },
                sequence_number=self.lora_radio._get_next_sequence_number(),
                timestamp=time.time()
            )
            
            # Send message
            success = await self.lora_radio.send_message(lora_message)
            
            if success:
                # Wait for response (with timeout)
                response = await self._wait_for_lora_response(lora_message, timeout=30)
                return response
            else:
                raise Exception("Failed to send LoRa message")
                
        except Exception as e:
            logger.error(f"LoRa routing failed: {e}")
            raise
    
    async def _route_via_internet(self, sms_message: SMSMessage, context: QueryContext,
                                routing_decision) -> SMSMessage:
        """Route request via internet connection."""
        try:
            # This would make HTTP request to bigEVY or other internet-connected node
            # For now, return a placeholder response
            
            logger.info("Routing via internet (not yet implemented)")
            
            return SMSMessage(
                phone_number=sms_message.phone_number,
                content="Internet routing not yet implemented. Processing locally.",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Internet routing failed: {e}")
            raise
    
    async def _route_via_sms(self, sms_message: SMSMessage, context: QueryContext,
                           routing_decision) -> SMSMessage:
        """Route request via SMS (fallback)."""
        try:
            # This would send SMS to another node with SMS gateway
            # For now, return a placeholder response
            
            logger.info("Routing via SMS (not yet implemented)")
            
            return SMSMessage(
                phone_number=sms_message.phone_number,
                content="SMS routing not yet implemented. Processing locally.",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"SMS routing failed: {e}")
            raise
    
    async def _wait_for_lora_response(self, request_message, timeout: int = 30) -> SMSMessage:
        """Wait for LoRa response message."""
        start_time = time.time()
        request_id = request_message.payload.get("request_id")
        
        while time.time() - start_time < timeout:
            # Check for received messages
            received_message = await self.lora_radio.receive_message()
            
            if received_message:
                # Check if this is a response to our request
                if (received_message.payload.get("response_to") == request_id and
                    received_message.message_type == MessageType.DATA):
                    
                    # Extract SMS response
                    sms_data = received_message.payload.get("sms_response", {})
                    return SMSMessage(
                        phone_number=sms_data.get("phone_number"),
                        content=sms_data.get("content"),
                        timestamp=datetime.now()
                    )
            
            await asyncio.sleep(0.1)  # Check every 100ms
        
        # Timeout - return error message
        return SMSMessage(
            phone_number=request_message.payload["sms_message"]["phone_number"],
            content="Request timed out. Please try again.",
            timestamp=datetime.now()
        )
    
    def _format_rag_response(self, rag_result: RAGResult) -> str:
        """Format RAG results for SMS response."""
        if not rag_result.documents:
            return "I don't have information about that topic."
        
        # Take the best result and format for SMS
        best_doc = rag_result.documents[0]
        
        # Truncate if too long
        if len(best_doc) > 150:
            return best_doc[:147] + "..."
        
        return best_doc
    
    async def _handle_data_message(self, message):
        """Handle incoming data message from LoRa."""
        try:
            payload = message.payload
            
            if "response_to" in payload:
                # This is a response to our request
                logger.info(f"Received LoRa response: {payload.get('request_id')}")
            else:
                # This is a new request - process it
                sms_data = payload.get("sms_message", {})
                if sms_data:
                    sms_message = SMSMessage(
                        phone_number=sms_data["phone_number"],
                        content=sms_data["content"],
                        timestamp=datetime.fromisoformat(sms_data["timestamp"])
                    )
                    
                    # Process the request
                    response = await self.process_sms_request(sms_message)
                    
                    # Send response back
                    response_message = LoRaMessage(
                        message_type=MessageType.DATA,
                        priority=MessagePriority.HIGH,
                        source_node=self.node_id,
                        destination_node=message.source_node,
                        payload={
                            "response_to": payload.get("request_id"),
                            "sms_response": {
                                "phone_number": response.phone_number,
                                "content": response.content,
                                "timestamp": response.timestamp.isoformat()
                            }
                        },
                        sequence_number=self.lora_radio._get_next_sequence_number(),
                        timestamp=time.time()
                    )
                    
                    await self.lora_radio.send_message(response_message)
                    
        except Exception as e:
            logger.error(f"Failed to handle data message: {e}")
    
    async def _handle_sync_message(self, message):
        """Handle knowledge synchronization message."""
        try:
            logger.info(f"Received sync message from {message.source_node}")
            
            # Process sync data
            sync_data = message.payload
            sync_type = sync_data.get("sync_type", "incremental")
            
            if sync_type == "emergency":
                # Handle emergency sync (weather alerts, etc.)
                await self._process_emergency_sync(sync_data)
            else:
                # Handle regular sync
                await self._process_knowledge_sync(sync_data)
            
            self.stats["lora_messages"] += 1
            
        except Exception as e:
            logger.error(f"Failed to handle sync message: {e}")
    
    async def _handle_emergency_message(self, message):
        """Handle emergency message."""
        try:
            logger.warning(f"Received emergency message from {message.source_node}")
            
            # Process emergency message
            emergency_data = message.payload
            emergency_type = emergency_data.get("type", "unknown")
            
            if emergency_type == "weather_alert":
                await self._process_weather_alert(emergency_data)
            elif emergency_type == "system_alert":
                await self._process_system_alert(emergency_data)
            
            self.stats["emergency_requests"] += 1
            
        except Exception as e:
            logger.error(f"Failed to handle emergency message: {e}")
    
    async def _handle_discovery_message(self, message):
        """Handle node discovery message."""
        try:
            # Update node information
            node_id = message.source_node
            capabilities = message.payload.get("capabilities", {})
            
            self.smart_router.register_node(node_id, capabilities)
            self.stats["mesh_nodes_discovered"] += 1
            
            logger.info(f"Discovered node: {node_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle discovery message: {e}")
    
    async def _on_node_discovered(self, node_id: str, capabilities: Dict[str, Any]):
        """Callback when a new node is discovered."""
        logger.info(f"New node discovered: {node_id}")
        self.stats["mesh_nodes_discovered"] += 1
    
    async def _process_emergency_sync(self, sync_data: Dict[str, Any]):
        """Process emergency synchronization data."""
        # This would update local knowledge base with emergency information
        logger.info("Processing emergency sync data")
    
    async def _process_knowledge_sync(self, sync_data: Dict[str, Any]):
        """Process regular knowledge synchronization data."""
        # This would update local knowledge base
        logger.info("Processing knowledge sync data")
    
    async def _process_weather_alert(self, alert_data: Dict[str, Any]):
        """Process weather alert."""
        # This would handle weather alerts
        logger.warning("Processing weather alert")
    
    async def _process_system_alert(self, alert_data: Dict[str, Any]):
        """Process system alert."""
        # This would handle system alerts
        logger.warning("Processing system alert")
    
    async def _request_processing_loop(self):
        """Background task for processing queued requests."""
        while self.is_initialized:
            try:
                # Process requests from queue
                if not self.request_queue.empty():
                    request = await self.request_queue.get()
                    await self._process_queued_request(request)
                
                await asyncio.sleep(0.1)  # 100ms processing interval
                
            except Exception as e:
                logger.error(f"Request processing loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _mesh_discovery_loop(self):
        """Background task for mesh network discovery."""
        while self.is_initialized:
            try:
                if self.lora_radio:
                    # Discovery is handled by LoRa radio service
                    pass
                
                await asyncio.sleep(self.config["mesh_discovery_interval"])
                
            except Exception as e:
                logger.error(f"Mesh discovery loop error: {e}")
                await asyncio.sleep(self.config["mesh_discovery_interval"])
    
    async def _health_monitoring_loop(self):
        """Background task for health monitoring."""
        while self.is_initialized:
            try:
                await self._update_service_health()
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(self.config["health_check_interval"])
    
    async def _statistics_update_loop(self):
        """Background task for updating statistics."""
        while self.is_initialized:
            try:
                self.stats["uptime"] = time.time() - self.stats["start_time"]
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Statistics update loop error: {e}")
                await asyncio.sleep(60)
    
    async def _update_service_health(self):
        """Update health status of all services."""
        try:
            for service_name, service in self.services.items():
                if hasattr(service, 'get_health'):
                    health = await service.get_health()
                    self.service_health[service_name] = health
                else:
                    self.service_health[service_name] = ServiceHealth(
                        status="unknown",
                        message="Health check not available"
                    )
            
            # Update smart router health
            if self.smart_router:
                self.service_health["smart_router"] = ServiceHealth(
                    status="healthy" if self.smart_router.is_initialized else "unhealthy",
                    message="Smart router status"
                )
            
            # Update LoRa radio health
            if self.lora_radio:
                self.service_health["lora_radio"] = ServiceHealth(
                    status="healthy" if self.lora_radio.is_initialized else "unhealthy",
                    message="LoRa radio status"
                )
            
        except Exception as e:
            logger.error(f"Failed to update service health: {e}")
    
    async def _process_queued_request(self, request):
        """Process a queued request."""
        try:
            # This would handle queued requests
            logger.debug("Processing queued request")
            
        except Exception as e:
            logger.error(f"Failed to process queued request: {e}")
    
    def get_health(self) -> ServiceHealth:
        """Get service health status."""
        try:
            if not self.is_initialized:
                return ServiceHealth(
                    status="unhealthy",
                    message="Service not initialized"
                )
            
            # Check critical services
            critical_services = ["smart_router", "sms_gateway", "llm_service"]
            unhealthy_services = []
            
            for service_name in critical_services:
                if service_name not in self.service_health:
                    unhealthy_services.append(service_name)
                elif self.service_health[service_name].status != "healthy":
                    unhealthy_services.append(service_name)
            
            if unhealthy_services:
                return ServiceHealth(
                    status="degraded",
                    message=f"Unhealthy services: {', '.join(unhealthy_services)}"
                )
            
            return ServiceHealth(
                status="healthy",
                message="All services operational"
            )
            
        except Exception as e:
            return ServiceHealth(
                status="unhealthy",
                message=f"Health check failed: {str(e)}"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self.stats,
            "is_initialized": self.is_initialized,
            "services_count": len(self.services),
            "lora_available": self.lora_radio is not None,
            "mesh_nodes": len(self.smart_router.known_nodes) if self.smart_router else 0,
            "service_health": self.service_health
        }
    
    async def cleanup(self):
        """Cleanup enhanced lilEVY service."""
        try:
            self.is_initialized = False
            
            # Cleanup smart router
            if self.smart_router:
                await self.smart_router.cleanup()
            
            # Cleanup LoRa radio
            if self.lora_radio:
                await self.lora_radio.cleanup()
            
            logger.info("Enhanced lilEVY Service cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global service instance
enhanced_lilevy_service = EnhancedLilEVYService("lilevy-001")
