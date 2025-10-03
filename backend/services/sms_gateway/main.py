"""SMS Gateway Service - Handles SMS communication."""
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import httpx
from datetime import datetime
import signal
import sys

from backend.shared.models import SMSMessage, ServiceHealth, ErrorResponse, MessagePriority
from backend.shared.config import settings
from backend.shared.logging import setup_logger
from backend.services.sms_gateway.gsm_driver import GSMDriver, SerialGSMDriver
from backend.services.sms_gateway.message_queue import SMSMessageQueue, MessagePriority as QueuePriority
from backend.services.sms_gateway.message_parser import MessageParser

logger = setup_logger("sms-gateway")


class SMSGateway:
    """Manages SMS sending and receiving with GSM integration."""
    
    def __init__(self):
        self.sent_messages: List[SMSMessage] = []
        self.received_messages: List[SMSMessage] = []
        self.message_router_url = f"http://localhost:{settings.message_router_port}"
        
        # GSM Driver (try Gammu first, fallback to Serial)
        self.gsm_driver = GSMDriver()
        self.serial_driver = SerialGSMDriver()
        self.active_driver = None
        
        # Message Queue
        self.message_queue = SMSMessageQueue()
        
        # Message Parser
        self.message_parser = MessageParser()
        
        # Processing tasks
        self.queue_task = None
        self.receive_task = None
        
        # Rate limiting
        self.last_send_times = {}
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def initialize(self) -> bool:
        """Initialize the SMS gateway."""
        try:
            logger.info("Initializing SMS Gateway...")
            
            # Initialize message queue
            if not await self.message_queue.initialize():
                logger.error("Failed to initialize message queue")
                return False
            
            # Try to initialize GSM driver
            if await self.gsm_driver.initialize():
                self.active_driver = self.gsm_driver
                logger.info("Using Gammu GSM driver")
            elif await self.serial_driver.initialize():
                self.active_driver = self.serial_driver
                logger.info("Using Serial GSM driver")
            else:
                logger.warning("No GSM driver available, running in simulation mode")
                self.active_driver = None
            
            # Set up message queue handlers
            await self.message_queue.set_send_handler(self._send_message_handler)
            await self.message_queue.set_receive_handler(self._receive_message_handler)
            
            # Start background tasks
            self.queue_task = asyncio.create_task(self.message_queue.start_processing())
            if self.active_driver:
                self.receive_task = asyncio.create_task(self._sms_receive_loop())
            
            logger.info("SMS Gateway initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SMS Gateway: {e}")
            return False
    
    async def send_sms(self, message: SMSMessage) -> bool:
        """Send SMS message via queue system."""
        try:
            # Convert priority
            queue_priority = self._convert_priority(message.priority)
            
            # Check rate limiting
            if not self._check_rate_limit(message.receiver):
                logger.warning(f"Rate limit exceeded for {message.receiver}")
                return False
            
            # Add to queue
            message_id = await self.message_queue.enqueue_message(
                phone_number=message.receiver,
                content=message.content,
                priority=queue_priority,
                metadata={'sender': message.sender, 'original_message': message.model_dump()}
            )
            
            logger.info(f"SMS queued for sending: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue SMS: {e}")
            return False
    
    async def _send_message_handler(self, phone_number: str, content: str) -> bool:
        """Handler for sending messages via GSM driver."""
        try:
            if self.active_driver:
                success = await self.active_driver.send_sms(phone_number, content)
                if success:
                    # Update rate limiting
                    self.last_send_times[phone_number] = datetime.utcnow()
                return success
            else:
                # Simulation mode
                logger.info(f"[SIMULATION] SMS sent to {phone_number}: {content[:50]}...")
                self.last_send_times[phone_number] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error in send handler: {e}")
            return False
    
    async def receive_sms(self, message: SMSMessage) -> None:
        """Receive and process incoming SMS."""
        try:
            logger.info(f"Received SMS from {message.sender}: {message.content}")
            
            # Parse and validate message
            parsed_message = self.message_parser.parse_message(message.content, message.sender)
            validation = self.message_parser.validate_message(message.content)
            
            logger.info(f"Parsed message - Intent: {parsed_message.intent}, Category: {parsed_message.category}, Priority: {parsed_message.priority}")
            
            # Add parsing results to message metadata
            message.metadata = message.metadata or {}
            message.metadata.update({
                'parsed': {
                    'intent': parsed_message.intent.value,
                    'category': parsed_message.category.value,
                    'entities': parsed_message.entities,
                    'confidence': parsed_message.confidence,
                    'requires_rag': parsed_message.requires_rag,
                    'requires_llm': parsed_message.requires_llm,
                    'priority': parsed_message.priority,
                    'language': parsed_message.language,
                    'clean_text': parsed_message.clean_text
                },
                'validation': validation
            })
            
            # Set message priority based on parsing
            if parsed_message.priority == "emergency":
                message.priority = MessagePriority.EMERGENCY
            elif parsed_message.priority == "high":
                message.priority = MessagePriority.HIGH
            elif parsed_message.priority == "low":
                message.priority = MessagePriority.LOW
            else:
                message.priority = MessagePriority.NORMAL
            
            message.id = f"sms_{datetime.utcnow().timestamp()}"
            message.timestamp = datetime.utcnow()
            self.received_messages.append(message)
            
            # Log validation warnings/errors
            if validation['warnings']:
                logger.warning(f"Message validation warnings: {validation['warnings']}")
            if validation['errors']:
                logger.error(f"Message validation errors: {validation['errors']}")
            
            # Forward to message router for processing
            await self.forward_to_router(message)
            
        except Exception as e:
            logger.error(f"Failed to process received SMS: {e}")
    
    async def _receive_message_handler(self, message_data: Dict[str, Any]) -> None:
        """Handler for receiving messages from GSM driver."""
        try:
            sms_message = SMSMessage(
                sender=message_data['sender'],
                receiver="+1234567890",  # Our number
                content=message_data['content'],
                timestamp=message_data['timestamp']
            )
            
            await self.receive_sms(sms_message)
            
        except Exception as e:
            logger.error(f"Error in receive handler: {e}")
    
    async def _sms_receive_loop(self) -> None:
        """Background loop for receiving SMS messages."""
        while True:
            try:
                if self.active_driver:
                    messages = await self.active_driver.receive_sms()
                    for message in messages:
                        await self._receive_message_handler(message)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in SMS receive loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def forward_to_router(self, message: SMSMessage) -> None:
        """Forward message to message router service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.message_router_url}/route",
                    json=message.model_dump(mode='json'),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Message forwarded to router: {message.id}")
                else:
                    logger.error(f"Failed to forward message: {response.status_code}")
        except Exception as e:
            logger.error(f"Error forwarding to router: {e}")
    
    def _check_rate_limit(self, phone_number: str) -> bool:
        """Check if sending to this number is within rate limits."""
        current_time = datetime.utcnow()
        
        # Check per-minute limit
        if phone_number in self.last_send_times:
            last_send = self.last_send_times[phone_number]
            if (current_time - last_send).total_seconds() < 60:
                return False
        
        return True
    
    def _convert_priority(self, priority: MessagePriority) -> QueuePriority:
        """Convert MessagePriority to QueuePriority."""
        priority_map = {
            MessagePriority.LOW: QueuePriority.LOW,
            MessagePriority.NORMAL: QueuePriority.NORMAL,
            MessagePriority.HIGH: QueuePriority.HIGH,
            MessagePriority.EMERGENCY: QueuePriority.EMERGENCY
        }
        return priority_map.get(priority, QueuePriority.NORMAL)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())
    
    async def shutdown(self) -> None:
        """Shutdown the SMS gateway."""
        try:
            logger.info("Shutting down SMS Gateway...")
            
            # Cancel background tasks
            if self.queue_task:
                self.queue_task.cancel()
            if self.receive_task:
                self.receive_task.cancel()
            
            # Disconnect GSM drivers
            if self.gsm_driver:
                await self.gsm_driver.disconnect()
            if self.serial_driver:
                await self.serial_driver.disconnect()
            
            # Close message queue
            await self.message_queue.close()
            
            logger.info("SMS Gateway shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            sys.exit(0)


# Global gateway instance
sms_gateway = SMSGateway()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the service."""
    logger.info("SMS Gateway Service starting up...")
    
    # Initialize the gateway
    if not await sms_gateway.initialize():
        logger.error("Failed to initialize SMS Gateway")
        raise RuntimeError("SMS Gateway initialization failed")
    
    yield
    
    logger.info("SMS Gateway Service shutting down...")
    await sms_gateway.shutdown()


# Create FastAPI app
app = FastAPI(
    title="EVY SMS Gateway Service",
    description="Handles SMS communication for EVY system",
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
    gsm_status = "disconnected"
    if sms_gateway.active_driver:
        gsm_status = "connected"
    
    queue_stats = await sms_gateway.message_queue.get_queue_stats()
    
    return ServiceHealth(
        service_name="sms-gateway",
        status="healthy",
        version="1.0.0",
        details={
            "sent_messages": len(sms_gateway.sent_messages),
            "received_messages": len(sms_gateway.received_messages),
            "gsm_status": gsm_status,
            "queue_stats": queue_stats
        }
    )


@app.post("/sms/send", response_model=dict)
async def send_sms(message: SMSMessage):
    """Send an SMS message."""
    success = await sms_gateway.send_sms(message)
    
    if success:
        return {"status": "sent", "message_id": message.id}
    else:
        raise HTTPException(status_code=500, detail="Failed to send SMS")


@app.post("/sms/receive", response_model=dict)
async def receive_sms(message: SMSMessage, background_tasks: BackgroundTasks):
    """Receive an incoming SMS message."""
    background_tasks.add_task(sms_gateway.receive_sms, message)
    return {"status": "received", "message": "Processing in background"}


@app.get("/sms/sent", response_model=List[SMSMessage])
async def get_sent_messages(limit: int = 100):
    """Get list of sent messages."""
    return sms_gateway.sent_messages[-limit:]


@app.get("/sms/received", response_model=List[SMSMessage])
async def get_received_messages(limit: int = 100):
    """Get list of received messages."""
    return sms_gateway.received_messages[-limit:]


@app.get("/gsm/status", response_model=dict)
async def get_gsm_status():
    """Get GSM driver status."""
    if sms_gateway.active_driver:
        if hasattr(sms_gateway.active_driver, 'health_check'):
            return await sms_gateway.active_driver.health_check()
        else:
            return {"connected": True, "driver": type(sms_gateway.active_driver).__name__}
    else:
        return {"connected": False, "driver": None}


@app.get("/queue/stats", response_model=dict)
async def get_queue_stats():
    """Get message queue statistics."""
    return await sms_gateway.message_queue.get_queue_stats()


@app.post("/queue/cleanup")
async def cleanup_queue(hours: int = 24):
    """Clean up old messages from queue."""
    cleaned = await sms_gateway.message_queue.cleanup_old_messages(hours)
    return {"cleaned_messages": cleaned}


@app.post("/gsm/reconnect")
async def reconnect_gsm():
    """Reconnect GSM driver."""
    try:
        # Disconnect current driver
        if sms_gateway.active_driver:
            await sms_gateway.active_driver.disconnect()
        
        # Try to reconnect
        if await sms_gateway.gsm_driver.initialize():
            sms_gateway.active_driver = sms_gateway.gsm_driver
            return {"status": "connected", "driver": "gammu"}
        elif await sms_gateway.serial_driver.initialize():
            sms_gateway.active_driver = sms_gateway.serial_driver
            return {"status": "connected", "driver": "serial"}
        else:
            sms_gateway.active_driver = None
            return {"status": "disconnected", "driver": None}
            
    except Exception as e:
        logger.error(f"Failed to reconnect GSM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-message")
async def parse_message(message_data: dict):
    """Parse and validate a message."""
    try:
        message_text = message_data.get('text', '')
        sender = message_data.get('sender', '')
        
        if not message_text:
            raise HTTPException(status_code=400, detail="Message text is required")
        
        # Parse the message
        parsed_message = sms_gateway.message_parser.parse_message(message_text, sender)
        
        # Validate the message
        validation = sms_gateway.message_parser.validate_message(message_text)
        
        return {
            "parsed": {
                "intent": parsed_message.intent.value,
                "category": parsed_message.category.value,
                "entities": parsed_message.entities,
                "confidence": parsed_message.confidence,
                "requires_rag": parsed_message.requires_rag,
                "requires_llm": parsed_message.requires_llm,
                "priority": parsed_message.priority,
                "language": parsed_message.language,
                "clean_text": parsed_message.clean_text
            },
            "validation": validation
        }
        
    except Exception as e:
        logger.error(f"Failed to parse message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.sms_gateway_port,
        log_level="info"
    )


