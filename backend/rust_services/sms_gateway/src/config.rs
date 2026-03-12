//! Configuration for SMS Gateway

use serde::{Deserialize, Serialize};
use std::time::Duration;

/// SMS Gateway configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatewayConfig {
    /// Serial device path (e.g., "/dev/ttyUSB0")
    pub device: String,
    
    /// Baud rate for serial communication
    pub baud_rate: u32,
    
    /// Maximum SMS messages per minute
    pub max_sms_per_minute: u32,
    
    /// Maximum SMS messages per hour
    pub max_sms_per_hour: u32,
    
    /// Message queue size
    pub queue_size: usize,
    
    /// Power-aware mode threshold (battery percentage)
    pub power_aware_threshold: u8,
    
    /// Enable power-aware processing
    pub power_aware_enabled: bool,
    
    /// Timeout for AT commands (seconds)
    pub at_command_timeout: Duration,
    
    /// Retry attempts for failed sends
    pub retry_attempts: u32,
    
    /// Retry delay (milliseconds)
    pub retry_delay_ms: u64,
}

impl Default for GatewayConfig {
    fn default() -> Self {
        Self {
            device: "/dev/ttyUSB0".to_string(),
            baud_rate: 115200,
            max_sms_per_minute: 10,
            max_sms_per_hour: 100,
            queue_size: 1000,
            power_aware_threshold: 30,
            power_aware_enabled: true,
            at_command_timeout: Duration::from_secs(5),
            retry_attempts: 3,
            retry_delay_ms: 1000,
        }
    }
}

impl GatewayConfig {
    /// Create config from environment variables
    pub fn from_env() -> Self {
        let device = std::env::var("SMS_DEVICE")
            .unwrap_or_else(|_| "/dev/ttyUSB0".to_string());
        
        let baud_rate = std::env::var("SMS_BAUD_RATE")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(115200);
        
        let max_sms_per_minute = std::env::var("MAX_SMS_PER_MINUTE")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(10);
        
        let max_sms_per_hour = std::env::var("MAX_SMS_PER_HOUR")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(100);
        
        Self {
            device,
            baud_rate,
            max_sms_per_minute,
            max_sms_per_hour,
            ..Default::default()
        }
    }
}

