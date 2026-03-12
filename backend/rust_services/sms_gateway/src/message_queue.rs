//! Memory-efficient message queue for SMS processing
//! 
//! Provides priority-based queuing with rate limiting

use crate::error::{GatewayError, Result};
use chrono::{DateTime, Utc};
use smallvec::SmallVec;
use std::collections::{HashMap, VecDeque};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info, warn};

/// Message priority levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum MessagePriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Emergency = 3,
}

/// Queued SMS message
#[derive(Debug, Clone)]
pub struct QueuedMessage {
    pub id: String,
    pub phone_number: String,
    pub content: String,
    pub priority: MessagePriority,
    pub created_at: DateTime<Utc>,
    pub retry_count: u32,
    pub metadata: HashMap<String, String>,
}

/// Message queue statistics
#[derive(Debug, Clone)]
pub struct QueueStats {
    pub total_messages: usize,
    pub pending_messages: usize,
    pub emergency_messages: usize,
    pub high_priority_messages: usize,
    pub normal_priority_messages: usize,
    pub low_priority_messages: usize,
    pub failed_messages: usize,
}

/// Memory-efficient priority queue for SMS messages
pub struct SMSMessageQueue {
    queues: Arc<RwLock<HashMap<MessagePriority, VecDeque<QueuedMessage>>>>,
    rate_limiter: Arc<RwLock<RateLimiter>>,
    config: QueueConfig,
}

struct RateLimiter {
    per_minute: HashMap<String, Vec<DateTime<Utc>>>,
    per_hour: HashMap<String, Vec<DateTime<Utc>>>,
}

struct QueueConfig {
    max_size: usize,
    max_per_minute: u32,
    max_per_hour: u32,
}

impl RateLimiter {
    fn new() -> Self {
        Self {
            per_minute: HashMap::new(),
            per_hour: HashMap::new(),
        }
    }
    
    fn check_rate_limit(&mut self, phone_number: &str, max_per_minute: u32, max_per_hour: u32) -> bool {
        let now = Utc::now();
        
        // Clean old entries
        self.per_minute.entry(phone_number.to_string())
            .or_insert_with(Vec::new)
            .retain(|&time| (now - time).num_seconds() < 60);
        
        self.per_hour.entry(phone_number.to_string())
            .or_insert_with(Vec::new)
            .retain(|&time| (now - time).num_hours() < 1);
        
        // Check limits
        let minute_count = self.per_minute.get(phone_number)
            .map(|v| v.len())
            .unwrap_or(0) as u32;
        
        let hour_count = self.per_hour.get(phone_number)
            .map(|v| v.len())
            .unwrap_or(0) as u32;
        
        if minute_count >= max_per_minute || hour_count >= max_per_hour {
            return false;
        }
        
        // Record this send
        self.per_minute.entry(phone_number.to_string())
            .or_insert_with(Vec::new)
            .push(now);
        
        self.per_hour.entry(phone_number.to_string())
            .or_insert_with(Vec::new)
            .push(now);
        
        true
    }
}

impl SMSMessageQueue {
    /// Create a new message queue
    pub fn new(max_size: usize, max_per_minute: u32, max_per_hour: u32) -> Self {
        let mut queues = HashMap::new();
        queues.insert(MessagePriority::Emergency, VecDeque::new());
        queues.insert(MessagePriority::High, VecDeque::new());
        queues.insert(MessagePriority::Normal, VecDeque::new());
        queues.insert(MessagePriority::Low, VecDeque::new());
        
        Self {
            queues: Arc::new(RwLock::new(queues)),
            rate_limiter: Arc::new(RwLock::new(RateLimiter::new())),
            config: QueueConfig {
                max_size,
                max_per_minute,
                max_per_hour,
            },
        }
    }
    
    /// Enqueue a message
    pub async fn enqueue(
        &self,
        phone_number: String,
        content: String,
        priority: MessagePriority,
    ) -> Result<String> {
        // Check rate limit
        let mut limiter = self.rate_limiter.write().await;
        if !limiter.check_rate_limit(
            &phone_number,
            self.config.max_per_minute,
            self.config.max_per_hour,
        ) {
            return Err(GatewayError::RateLimitExceeded);
        }
        drop(limiter);
        
        // Check queue size
        let mut queues = self.queues.write().await;
        let total_size: usize = queues.values().map(|q| q.len()).sum();
        
        if total_size >= self.config.max_size {
            return Err(GatewayError::QueueFull);
        }
        
        // Create message
        let message_id = format!("msg_{}_{}", Utc::now().timestamp(), phone_number);
        let message = QueuedMessage {
            id: message_id.clone(),
            phone_number,
            content,
            priority,
            created_at: Utc::now(),
            retry_count: 0,
            metadata: HashMap::new(),
        };
        
        // Add to appropriate priority queue
        queues.get_mut(&priority)
            .ok_or_else(|| GatewayError::Unknown("Invalid priority".to_string()))?
            .push_back(message);
        
        debug!("Message enqueued: {} (priority: {:?})", message_id, priority);
        Ok(message_id)
    }
    
    /// Dequeue next message (highest priority first)
    pub async fn dequeue(&self) -> Option<QueuedMessage> {
        let mut queues = self.queues.write().await;
        
        // Check queues in priority order
        for priority in [MessagePriority::Emergency, MessagePriority::High, MessagePriority::Normal, MessagePriority::Low] {
            if let Some(queue) = queues.get_mut(&priority) {
                if let Some(message) = queue.pop_front() {
                    return Some(message);
                }
            }
        }
        
        None
    }
    
    /// Peek at next message without removing it
    pub async fn peek(&self) -> Option<QueuedMessage> {
        let queues = self.queues.read().await;
        
        for priority in [MessagePriority::Emergency, MessagePriority::High, MessagePriority::Normal, MessagePriority::Low] {
            if let Some(queue) = queues.get(&priority) {
                if let Some(message) = queue.front() {
                    return Some(message.clone());
                }
            }
        }
        
        None
    }
    
    /// Get queue statistics
    pub async fn get_stats(&self) -> QueueStats {
        let queues = self.queues.read().await;
        
        let emergency = queues.get(&MessagePriority::Emergency)
            .map(|q| q.len())
            .unwrap_or(0);
        
        let high = queues.get(&MessagePriority::High)
            .map(|q| q.len())
            .unwrap_or(0);
        
        let normal = queues.get(&MessagePriority::Normal)
            .map(|q| q.len())
            .unwrap_or(0);
        
        let low = queues.get(&MessagePriority::Low)
            .map(|q| q.len())
            .unwrap_or(0);
        
        let pending = emergency + high + normal + low;
        
        QueueStats {
            total_messages: pending,
            pending_messages: pending,
            emergency_messages: emergency,
            high_priority_messages: high,
            normal_priority_messages: normal,
            low_priority_messages: low,
            failed_messages: 0, // TODO: Track failed messages
        }
    }
    
    /// Clean up old messages
    pub async fn cleanup_old(&self, max_age_hours: u32) -> usize {
        let mut queues = self.queues.write().await;
        let mut cleaned = 0;
        let cutoff = Utc::now() - chrono::Duration::hours(max_age_hours as i64);
        
        for queue in queues.values_mut() {
            let initial_len = queue.len();
            queue.retain(|msg| msg.created_at > cutoff);
            cleaned += initial_len - queue.len();
        }
        
        if cleaned > 0 {
            info!("Cleaned up {} old messages", cleaned);
        }
        
        cleaned
    }
}

