//! Service registry for routing
//! 
//! Lightweight in-memory service registry

use crate::error::{RouterError, Result};
use lru::LruCache;
use std::collections::HashMap;
use std::num::NonZeroUsize;
use std::sync::Arc;
use tokio::sync::RwLock;

/// Service types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ServiceType {
    LLM,
    RAG,
    Emergency,
    Template,
    Local,
    BigEVY,
}

/// Service status
#[derive(Debug, Clone)]
pub enum ServiceStatus {
    Available,
    Unavailable,
    LowResources,
}

/// Service information
#[derive(Debug, Clone)]
pub struct ServiceInfo {
    pub service_type: ServiceType,
    pub url: String,
    pub status: ServiceStatus,
    pub priority: u8, // 0-255, higher = more preferred
}

/// Routing cache
pub struct RoutingCache {
    cache: Arc<RwLock<LruCache<String, RouteDecision>>>,
}

/// Route decision
#[derive(Debug, Clone)]
pub struct RouteDecision {
    pub service_type: ServiceType,
    pub service_url: String,
    pub requires_rag: bool,
    pub requires_llm: bool,
    pub priority: u8,
}

impl RoutingCache {
    /// Create a new routing cache
    pub fn new(capacity: usize) -> Self {
        let capacity = NonZeroUsize::new(capacity.max(1)).unwrap();
        Self {
            cache: Arc::new(RwLock::new(LruCache::new(capacity))),
        }
    }
    
    /// Get cached route
    pub async fn get(&self, key: &str) -> Option<RouteDecision> {
        let mut cache = self.cache.write().await;
        cache.get(key).cloned()
    }
    
    /// Put route in cache
    pub async fn put(&self, key: String, value: RouteDecision) {
        let mut cache = self.cache.write().await;
        cache.put(key, value);
    }
    
    /// Clear cache
    pub async fn clear(&self) {
        let mut cache = self.cache.write().await;
        cache.clear();
    }
    
    /// Get cache statistics
    pub async fn stats(&self) -> CacheStats {
        let cache = self.cache.read().await;
        CacheStats {
            size: cache.len(),
            capacity: cache.cap().get(),
        }
    }
}

/// Cache statistics
#[derive(Debug, Clone)]
pub struct CacheStats {
    pub size: usize,
    pub capacity: usize,
}

/// Service registry
pub struct ServiceRegistry {
    services: Arc<RwLock<HashMap<ServiceType, ServiceInfo>>>,
}

impl ServiceRegistry {
    /// Create a new service registry
    pub fn new() -> Self {
        Self {
            services: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Register a service
    pub async fn register(&self, service: ServiceInfo) {
        let mut services = self.services.write().await;
        services.insert(service.service_type, service);
    }
    
    /// Get service by type
    pub async fn get_service(&self, service_type: ServiceType) -> Option<ServiceInfo> {
        let services = self.services.read().await;
        services.get(&service_type).cloned()
    }
    
    /// Get available services (filtered by status)
    pub async fn get_available_services(&self) -> Vec<ServiceInfo> {
        let services = self.services.read().await;
        services
            .values()
            .filter(|s| matches!(s.status, ServiceStatus::Available))
            .cloned()
            .collect()
    }
    
    /// Update service status
    pub async fn update_status(&self, service_type: ServiceType, status: ServiceStatus) {
        let mut services = self.services.write().await;
        if let Some(service) = services.get_mut(&service_type) {
            service.status = status;
        }
    }
    
    /// Select best service for intent (resource-aware)
    pub async fn select_service(
        &self,
        intent: crate::intent_classifier::Intent,
        battery_level: u8,
        memory_mb: usize,
        battery_threshold: u8,
        memory_threshold_mb: usize,
    ) -> Result<RouteDecision> {
        match intent {
            crate::intent_classifier::Intent::Emergency => {
                // Emergency always uses local handler
                Ok(RouteDecision {
                    service_type: ServiceType::Emergency,
                    service_url: "local".to_string(),
                    requires_rag: false,
                    requires_llm: false,
                    priority: 255,
                })
            }
            crate::intent_classifier::Intent::Command => {
                // Commands use local handler
                Ok(RouteDecision {
                    service_type: ServiceType::Local,
                    service_url: "local".to_string(),
                    requires_rag: false,
                    requires_llm: false,
                    priority: 200,
                })
            }
            crate::intent_classifier::Intent::Greeting => {
                // Greetings use local LLM
                if let Some(llm) = self.get_service(ServiceType::LLM).await {
                    Ok(RouteDecision {
                        service_type: ServiceType::LLM,
                        service_url: llm.url,
                        requires_rag: false,
                        requires_llm: true,
                        priority: 100,
                    })
                } else {
                    Err(RouterError::ServiceNotFound("LLM".to_string()))
                }
            }
            crate::intent_classifier::Intent::Query => {
                // Queries: resource-aware selection
                // Check if we can use bigEVY (requires good battery and memory)
                let can_use_bigevy = battery_level >= battery_threshold 
                    && memory_mb >= memory_threshold_mb;
                
                if can_use_bigevy {
                    if let Some(bigevy) = self.get_service(ServiceType::BigEVY).await {
                        if matches!(bigevy.status, ServiceStatus::Available) {
                            return Ok(RouteDecision {
                                service_type: ServiceType::BigEVY,
                                service_url: bigevy.url,
                                requires_rag: true,
                                requires_llm: true,
                                priority: 150,
                            });
                        }
                    }
                }
                
                // Fallback to local LLM
                if let Some(llm) = self.get_service(ServiceType::LLM).await {
                    Ok(RouteDecision {
                        service_type: ServiceType::LLM,
                        service_url: llm.url,
                        requires_rag: false,
                        requires_llm: true,
                        priority: 100,
                    })
                } else {
                    Err(RouterError::ServiceNotFound("LLM".to_string()))
                }
            }
            crate::intent_classifier::Intent::Unknown => {
                // Unknown: try local LLM
                if let Some(llm) = self.get_service(ServiceType::LLM).await {
                    Ok(RouteDecision {
                        service_type: ServiceType::LLM,
                        service_url: llm.url,
                        requires_rag: false,
                        requires_llm: true,
                        priority: 50,
                    })
                } else {
                    Err(RouterError::ServiceNotFound("LLM".to_string()))
                }
            }
        }
    }
}

impl Default for ServiceRegistry {
    fn default() -> Self {
        Self::new()
    }
}

