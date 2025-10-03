"""Message queue system for SMS handling."""
import asyncio
import json
import redis
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MessageStatus(str, Enum):
    """Message processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


@dataclass
class QueuedMessage:
    """Message in the queue."""
    id: str
    phone_number: str
    content: str
    priority: MessagePriority
    status: MessageStatus
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    next_retry: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['next_retry'] = self.next_retry.isoformat() if self.next_retry else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedMessage':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['next_retry'] = datetime.fromisoformat(data['next_retry']) if data['next_retry'] else None
        return cls(**data)


class SMSMessageQueue:
    """Redis-based message queue for SMS handling."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = "sms_queue"
        self.processing_queue = "sms_processing"
        self.failed_queue = "sms_failed"
        self.sent_queue = "sms_sent"
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min
        
        # Message handlers
        self.send_handler: Optional[Callable] = None
        self.receive_handler: Optional[Callable] = None
        
    async def initialize(self) -> bool:
        """Initialize the queue system."""
        try:
            # Test Redis connection
            self.redis_client.ping()
            logger.info("Message queue initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize message queue: {e}")
            return False
    
    async def enqueue_message(
        self,
        phone_number: str,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add message to queue."""
        message_id = f"sms_{datetime.utcnow().timestamp()}_{hash(phone_number + content) % 10000}"
        
        message = QueuedMessage(
            id=message_id,
            phone_number=phone_number,
            content=content,
            priority=priority,
            status=MessageStatus.PENDING,
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        
        try:
            # Store message
            self.redis_client.hset(f"message:{message_id}", mapping=message.to_dict())
            
            # Add to priority queue
            priority_score = self._get_priority_score(priority)
            self.redis_client.zadd(self.queue_name, {message_id: priority_score})
            
            logger.info(f"Message {message_id} queued with priority {priority}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue message: {e}")
            raise
    
    async def dequeue_message(self) -> Optional[QueuedMessage]:
        """Get next message from queue."""
        try:
            # Get highest priority message
            result = self.redis_client.bzpopmin(self.queue_name, timeout=1)
            if not result:
                return None
            
            queue_name, message_id, score = result
            
            # Get message data
            message_data = self.redis_client.hgetall(f"message:{message_id}")
            if not message_data:
                logger.warning(f"Message {message_id} not found in storage")
                return None
            
            message = QueuedMessage.from_dict(message_data)
            
            # Move to processing queue
            self.redis_client.zadd(self.processing_queue, {message_id: score})
            self.redis_client.hset(f"message:{message_id}", "status", MessageStatus.PROCESSING)
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to dequeue message: {e}")
            return None
    
    async def mark_sent(self, message_id: str) -> None:
        """Mark message as sent."""
        try:
            # Move to sent queue
            score = self.redis_client.zscore(self.processing_queue, message_id)
            if score:
                self.redis_client.zrem(self.processing_queue, message_id)
                self.redis_client.zadd(self.sent_queue, {message_id: score})
            
            # Update status
            self.redis_client.hset(f"message:{message_id}", "status", MessageStatus.SENT)
            
            # Clean up old data (keep for 24 hours)
            self.redis_client.expire(f"message:{message_id}", 86400)
            
            logger.info(f"Message {message_id} marked as sent")
            
        except Exception as e:
            logger.error(f"Failed to mark message as sent: {e}")
    
    async def mark_failed(self, message_id: str, error: str) -> None:
        """Mark message as failed and schedule retry if applicable."""
        try:
            # Get message data
            message_data = self.redis_client.hgetall(f"message:{message_id}")
            if not message_data:
                return
            
            message = QueuedMessage.from_dict(message_data)
            message.attempts += 1
            message.metadata = message.metadata or {}
            message.metadata['last_error'] = error
            message.metadata['failed_at'] = datetime.utcnow().isoformat()
            
            # Check if we should retry
            if message.attempts < message.max_attempts:
                # Schedule retry
                retry_delay = self.retry_delays[min(message.attempts - 1, len(self.retry_delays) - 1)]
                message.next_retry = datetime.utcnow() + timedelta(seconds=retry_delay)
                message.status = MessageStatus.RETRYING
                
                # Move back to queue for retry
                self.redis_client.zrem(self.processing_queue, message_id)
                priority_score = self._get_priority_score(message.priority)
                # Add delay to score to schedule retry
                retry_score = priority_score + message.next_retry.timestamp()
                self.redis_client.zadd(self.queue_name, {message_id: retry_score})
                
                logger.info(f"Message {message_id} scheduled for retry in {retry_delay}s")
            else:
                # Move to failed queue
                self.redis_client.zrem(self.processing_queue, message_id)
                self.redis_client.zadd(self.failed_queue, {message_id: datetime.utcnow().timestamp()})
                message.status = MessageStatus.FAILED
                
                logger.warning(f"Message {message_id} failed permanently after {message.attempts} attempts")
            
            # Update message data
            self.redis_client.hset(f"message:{message_id}", mapping=message.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to mark message as failed: {e}")
    
    async def process_retry_messages(self) -> None:
        """Process messages that are ready for retry."""
        try:
            current_time = datetime.utcnow().timestamp()
            
            # Get messages ready for retry
            ready_messages = self.redis_client.zrangebyscore(
                self.queue_name, 0, current_time, withscores=True
            )
            
            for message_id, score in ready_messages:
                message_data = self.redis_client.hgetall(f"message:{message_id}")
                if message_data:
                    message = QueuedMessage.from_dict(message_data)
                    
                    # Check if it's time to retry
                    if message.next_retry and message.next_retry <= datetime.utcnow():
                        # Reset status and move to processing
                        priority_score = self._get_priority_score(message.priority)
                        self.redis_client.zrem(self.queue_name, message_id)
                        self.redis_client.zadd(self.queue_name, {message_id: priority_score})
                        
                        self.redis_client.hset(f"message:{message_id}", "status", MessageStatus.PENDING)
                        
                        logger.info(f"Message {message_id} ready for retry")
            
        except Exception as e:
            logger.error(f"Failed to process retry messages: {e}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            stats = {
                'pending': self.redis_client.zcard(self.queue_name),
                'processing': self.redis_client.zcard(self.processing_queue),
                'sent': self.redis_client.zcard(self.sent_queue),
                'failed': self.redis_client.zcard(self.failed_queue),
                'total_messages': 0
            }
            
            stats['total_messages'] = sum(stats.values())
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    async def cleanup_old_messages(self, hours: int = 24) -> int:
        """Clean up old messages."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Clean up sent messages
            old_sent = self.redis_client.zrangebyscore(
                self.sent_queue, 0, cutoff_timestamp
            )
            
            cleaned = 0
            for message_id in old_sent:
                self.redis_client.zrem(self.sent_queue, message_id)
                self.redis_client.delete(f"message:{message_id}")
                cleaned += 1
            
            logger.info(f"Cleaned up {cleaned} old messages")
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup old messages: {e}")
            return 0
    
    def _get_priority_score(self, priority: MessagePriority) -> float:
        """Get numeric score for priority (lower = higher priority)."""
        priority_scores = {
            MessagePriority.EMERGENCY: 1.0,
            MessagePriority.HIGH: 2.0,
            MessagePriority.NORMAL: 3.0,
            MessagePriority.LOW: 4.0
        }
        return priority_scores.get(priority, 3.0)
    
    async def set_send_handler(self, handler: Callable) -> None:
        """Set handler for sending messages."""
        self.send_handler = handler
    
    async def set_receive_handler(self, handler: Callable) -> None:
        """Set handler for receiving messages."""
        self.receive_handler = handler
    
    async def start_processing(self) -> None:
        """Start the message processing loop."""
        logger.info("Starting message queue processing")
        
        while True:
            try:
                # Process retry messages first
                await self.process_retry_messages()
                
                # Get next message
                message = await self.dequeue_message()
                if not message:
                    await asyncio.sleep(1)
                    continue
                
                # Process message
                if self.send_handler:
                    success = await self.send_handler(message.phone_number, message.content)
                    
                    if success:
                        await self.mark_sent(message.id)
                    else:
                        await self.mark_failed(message.id, "Send handler returned False")
                else:
                    logger.warning("No send handler configured")
                    await self.mark_failed(message.id, "No send handler configured")
                
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(5)
    
    async def close(self) -> None:
        """Close the queue system."""
        try:
            self.redis_client.close()
            logger.info("Message queue closed")
        except Exception as e:
            logger.error(f"Error closing message queue: {e}")
