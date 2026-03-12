//! Error types for Compression Engine

use thiserror::Error;

/// Compression engine error types
#[derive(Debug, Error)]
pub enum CompressionError {
    #[error("Text too short to compress: {0} characters")]
    TextTooShort(usize),
    
    #[error("Compression failed: {0}")]
    CompressionFailed(String),
    
    #[error("Target length too small: {0}")]
    TargetTooSmall(usize),
    
    #[error("Insufficient memory: {0}MB available")]
    InsufficientMemory(usize),
    
    #[error("Battery too low: {0}%")]
    BatteryTooLow(u8),
    
    #[error("Cache error: {0}")]
    CacheError(String),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, CompressionError>;

