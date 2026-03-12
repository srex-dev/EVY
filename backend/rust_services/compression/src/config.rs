//! Configuration for Compression Engine

use serde::{Deserialize, Serialize};

/// Compression engine configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompressionConfig {
    /// Target length for compressed text (default: 160 for SMS)
    pub target_length: usize,
    
    /// Compression level (0.0-1.0, aggressiveness)
    pub compression_level: f32,
    
    /// Use tiny model if available (optional)
    pub use_model: bool,
    
    /// Memory threshold in MB for using model
    pub memory_threshold_mb: usize,
    
    /// Battery threshold percentage for using model
    pub battery_threshold: u8,
    
    /// Maximum cache size (number of entries)
    pub cache_size: usize,
    
    /// Enable resource-aware compression
    pub resource_aware: bool,
    
    /// Enable battery-aware compression
    pub battery_aware: bool,
}

impl Default for CompressionConfig {
    fn default() -> Self {
        Self {
            target_length: 160,
            compression_level: 0.7,
            use_model: false, // Model support to be added later
            memory_threshold_mb: 100,
            battery_threshold: 30,
            cache_size: 1000,
            resource_aware: true,
            battery_aware: true,
        }
    }
}

impl CompressionConfig {
    /// Create config from environment variables
    pub fn from_env() -> Self {
        let target_length = std::env::var("COMPRESSION_TARGET_LENGTH")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(160);
        
        let compression_level = std::env::var("COMPRESSION_LEVEL")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0.7);
        
        let cache_size = std::env::var("COMPRESSION_CACHE_SIZE")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(1000);
        
        Self {
            target_length,
            compression_level,
            cache_size,
            ..Default::default()
        }
    }
}

