//! Configuration for Message Router

use serde::{Deserialize, Serialize};

/// Message router configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RouterConfig {
    /// LLM service URL
    pub llm_service_url: String,
    
    /// RAG service URL
    pub rag_service_url: String,
    
    /// SMS gateway URL
    pub sms_gateway_url: String,
    
    /// Maximum routing cache size
    pub cache_size: usize,
    
    /// Battery threshold for skipping bigEVY (0-100)
    pub battery_threshold: u8,
    
    /// Memory threshold in MB for service selection
    pub memory_threshold_mb: usize,
    
    /// Enable resource-aware routing
    pub resource_aware: bool,
    
    /// Enable battery-aware routing
    pub battery_aware: bool,
    
    /// Enable memory-aware routing
    pub memory_aware: bool,
}

impl Default for RouterConfig {
    fn default() -> Self {
        Self {
            llm_service_url: "http://localhost:8003".to_string(),
            rag_service_url: "http://localhost:8004".to_string(),
            sms_gateway_url: "http://localhost:8001".to_string(),
            cache_size: 1000,
            battery_threshold: 50,
            memory_threshold_mb: 100,
            resource_aware: true,
            battery_aware: true,
            memory_aware: true,
        }
    }
}

impl RouterConfig {
    /// Create config from environment variables
    pub fn from_env() -> Self {
        let llm_url = std::env::var("LLM_SERVICE_URL")
            .unwrap_or_else(|_| "http://localhost:8003".to_string());
        
        let rag_url = std::env::var("RAG_SERVICE_URL")
            .unwrap_or_else(|_| "http://localhost:8004".to_string());
        
        let sms_url = std::env::var("SMS_GATEWAY_URL")
            .unwrap_or_else(|_| "http://localhost:8001".to_string());
        
        let cache_size = std::env::var("ROUTER_CACHE_SIZE")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(1000);
        
        Self {
            llm_service_url: llm_url,
            rag_service_url: rag_url,
            sms_gateway_url: sms_url,
            cache_size,
            ..Default::default()
        }
    }
}

