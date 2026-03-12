//! Error types for SMS Gateway

use thiserror::Error;

/// SMS Gateway error types
#[derive(Debug, Error)]
pub enum GatewayError {
    #[error("Serial communication error: {0}")]
    Serial(#[from] serialport::Error),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("GSM module not connected")]
    NotConnected,
    
    #[error("GSM module initialization failed: {0}")]
    InitializationFailed(String),
    
    #[error("AT command failed: {0}")]
    AtCommandFailed(String),
    
    #[error("Invalid phone number: {0}")]
    InvalidPhoneNumber(String),
    
    #[error("Message too long: {0} characters (max 160)")]
    MessageTooLong(usize),
    
    #[error("Rate limit exceeded")]
    RateLimitExceeded,
    
    #[error("Queue full")]
    QueueFull,
    
    #[error("Power level too low: {0}%")]
    PowerTooLow(u8),
    
    #[error("Timeout: {0}")]
    Timeout(String),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, GatewayError>;

