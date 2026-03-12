//! Error types for Message Router

use thiserror::Error;

/// Message router error types
#[derive(Debug, Error)]
pub enum RouterError {
    #[error("Service not found: {0}")]
    ServiceNotFound(String),
    
    #[error("Routing failed: {0}")]
    RoutingFailed(String),
    
    #[error("Intent classification failed: {0}")]
    ClassificationFailed(String),
    
    #[error("Insufficient memory: {0}MB available")]
    InsufficientMemory(usize),
    
    #[error("Battery too low: {0}%")]
    BatteryTooLow(u8),
    
    #[error("Service unavailable: {0}")]
    ServiceUnavailable(String),
    
    #[error("HTTP error: {0}")]
    HttpError(#[from] reqwest::Error),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, RouterError>;

