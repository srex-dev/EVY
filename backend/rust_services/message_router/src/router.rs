//! Main message router
//! 
//! Orchestrates intent classification, service selection, and routing

use crate::config::RouterConfig;
use crate::error::{RouterError, Result};
use crate::intent_classifier::{IntentClassifier, ClassificationResult};
use crate::resource_monitor::ResourceMonitor;
use crate::service_registry::{ServiceRegistry, ServiceInfo, ServiceType, RouteDecision};
use crate::service_registry::RoutingCache;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info, warn};

/// Routing statistics
#[derive(Debug, Clone)]
pub struct RouterStats {
    pub total_routes: usize,
    pub cache_hits: usize,
    pub cache_misses: usize,
    pub emergency_routes: usize,
    pub query_routes: usize,
    pub command_routes: usize,
    pub average_routing_time_ms: f64,
}

/// Message structure for routing
#[derive(Debug, Clone)]
pub struct Message {
    pub id: String,
    pub sender: String,
    pub content: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Main message router
pub struct MessageRouter {
    classifier: IntentClassifier,
    service_registry: Arc<ServiceRegistry>,
    routing_cache: Arc<RoutingCache>,
    resource_monitor: Arc<RwLock<ResourceMonitor>>,
    config: RouterConfig,
    stats: Arc<RwLock<RouterStats>>,
}

impl MessageRouter {
    /// Create a new message router
    pub fn new(config: RouterConfig) -> Self {
        let service_registry = Arc::new(ServiceRegistry::new());
        let routing_cache = Arc::new(RoutingCache::new(config.cache_size));
        let resource_monitor = Arc::new(RwLock::new(ResourceMonitor::new()));
        
        Self {
            classifier: IntentClassifier::new(),
            service_registry,
            routing_cache,
            resource_monitor,
            config,
            stats: Arc::new(RwLock::new(RouterStats {
                total_routes: 0,
                cache_hits: 0,
                cache_misses: 0,
                emergency_routes: 0,
                query_routes: 0,
                command_routes: 0,
                average_routing_time_ms: 0.0,
            })),
        }
    }
    
    /// Initialize router with default services
    pub async fn initialize(&self) -> Result<()> {
        info!("Initializing Message Router...");
        
        // Register default services
        self.service_registry.register(ServiceInfo {
            service_type: ServiceType::LLM,
            url: self.config.llm_service_url.clone(),
            status: crate::service_registry::ServiceStatus::Available,
            priority: 100,
        }).await;
        
        self.service_registry.register(ServiceInfo {
            service_type: ServiceType::RAG,
            url: self.config.rag_service_url.clone(),
            status: crate::service_registry::ServiceStatus::Available,
            priority: 80,
        }).await;
        
        info!("Message Router initialized successfully");
        Ok(())
    }
    
    /// Route a message
    pub async fn route(&self, message: &Message) -> Result<RouteDecision> {
        let start = std::time::Instant::now();
        
        // Check cache first (fast path)
        let cache_key = format!("{}:{}", message.sender, message.content);
        if let Some(cached) = self.routing_cache.get(&cache_key).await {
            let mut stats = self.stats.write().await;
            stats.cache_hits += 1;
            stats.total_routes += 1;
            debug!("Cache hit for routing");
            return Ok(cached);
        }
        
        let mut stats = self.stats.write().await;
        stats.cache_misses += 1;
        drop(stats);
        
        // Classify intent
        let classification = self.classifier.classify(&message.content);
        debug!("Classified as: {:?} (confidence: {:.2})", classification.intent, classification.confidence);
        
        // Get resource status
        let monitor = self.resource_monitor.read().await;
        let battery = monitor.battery_level();
        let memory = monitor.available_memory_mb();
        drop(monitor);
        
        // Select service (resource-aware)
        let route = self.service_registry.select_service(
            classification.intent,
            battery,
            memory,
            self.config.battery_threshold,
            self.config.memory_threshold_mb,
        ).await?;
        
        // Update statistics
        let mut stats = self.stats.write().await;
        stats.total_routes += 1;
        
        match classification.intent {
            crate::intent_classifier::Intent::Emergency => {
                stats.emergency_routes += 1;
            }
            crate::intent_classifier::Intent::Query => {
                stats.query_routes += 1;
            }
            crate::intent_classifier::Intent::Command => {
                stats.command_routes += 1;
            }
            _ => {}
        }
        
        // Update average routing time
        let duration = start.elapsed();
        let n = stats.total_routes as f64;
        stats.average_routing_time_ms = 
            (stats.average_routing_time_ms * (n - 1.0) + duration.as_millis() as f64) / n;
        
        // Cache the route
        self.routing_cache.put(cache_key, route.clone()).await;
        
        info!("Routed message in {}ms: {:?} -> {:?}", duration.as_millis(), classification.intent, route.service_type);
        Ok(route)
    }
    
    /// Classify message without routing
    pub fn classify(&self, text: &str) -> ClassificationResult {
        self.classifier.classify(text)
    }
    
    /// Get router statistics
    pub async fn get_stats(&self) -> RouterStats {
        self.stats.read().await.clone()
    }
    
    /// Update resource monitor
    pub async fn update_resources(&self, memory_mb: usize, battery: u8, cpu: f32) {
        let mut monitor = self.resource_monitor.write().await;
        monitor.set_available_memory_mb(memory_mb);
        monitor.set_battery_level(battery);
        monitor.set_cpu_usage(cpu);
    }
    
    /// Clear routing cache
    pub async fn clear_cache(&self) {
        self.routing_cache.clear().await;
        info!("Routing cache cleared");
    }
}

