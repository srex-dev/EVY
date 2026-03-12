//! PyO3 bindings for Python integration

use crate::config::RouterConfig;
use crate::router::{MessageRouter, RouterStats, Message};
use crate::intent_classifier::{ClassificationResult, Intent, MessagePriority};
use crate::error::RouterError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::sync::Arc;
use tokio::runtime::Runtime;

/// Python wrapper for Message Router
#[pyclass]
pub struct PyMessageRouter {
    router: Arc<MessageRouter>,
    runtime: Runtime,
}

#[pymethods]
impl PyMessageRouter {
    /// Create a new message router
    #[new]
    fn new(config: Option<PyRouterConfig>) -> PyResult<Self> {
        let config = config.map(|c| c.into()).unwrap_or_else(RouterConfig::default);
        let router = MessageRouter::new(config);
        
        let runtime = Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;
        
        Ok(Self {
            router: Arc::new(router),
            runtime,
        })
    }
    
    /// Initialize router
    fn initialize(&self) -> PyResult<()> {
        let router = Arc::clone(&self.router);
        self.runtime.block_on(async {
            router.initialize().await
                .map_err(|e| PyRuntimeError::new_err(format!("Initialization failed: {}", e)))
        })
    }
    
    /// Route a message
    fn route(&self, sender: String, content: String) -> PyResult<PyRouteDecision> {
        let router = Arc::clone(&self.router);
        let message = Message {
            id: format!("msg_{}", chrono::Utc::now().timestamp()),
            sender,
            content: content.clone(),
            timestamp: chrono::Utc::now(),
        };
        
        let route = self.runtime.block_on(async {
            router.route(&message).await
                .map_err(|e| PyRuntimeError::new_err(format!("Routing failed: {}", e)))
        })?;
        
        Ok(PyRouteDecision::from(route))
    }
    
    /// Classify message
    fn classify(&self, text: String) -> PyResult<PyClassificationResult> {
        let router = Arc::clone(&self.router);
        let result = router.classify(&text);
        Ok(PyClassificationResult::from(result))
    }
    
    /// Get router statistics
    fn get_stats(&self) -> PyResult<PyRouterStats> {
        let router = Arc::clone(&self.router);
        let stats = self.runtime.block_on(async {
            router.get_stats().await
        });
        
        Ok(PyRouterStats::from(stats))
    }
    
    /// Update resource monitor
    fn update_resources(&self, memory_mb: usize, battery: u8, cpu: f32) {
        let router = Arc::clone(&self.router);
        self.runtime.block_on(async {
            router.update_resources(memory_mb, battery, cpu).await;
        });
    }
    
    /// Clear cache
    fn clear_cache(&self) {
        let router = Arc::clone(&self.router);
        self.runtime.block_on(async {
            router.clear_cache().await;
        });
    }
}

/// Python wrapper for RouterConfig
#[pyclass]
#[derive(Clone)]
pub struct PyRouterConfig {
    #[pyo3(get, set)]
    llm_service_url: String,
    #[pyo3(get, set)]
    rag_service_url: String,
    #[pyo3(get, set)]
    sms_gateway_url: String,
    #[pyo3(get, set)]
    cache_size: usize,
    #[pyo3(get, set)]
    battery_threshold: u8,
}

#[pymethods]
impl PyRouterConfig {
    #[new]
    fn new(
        llm_service_url: Option<String>,
        rag_service_url: Option<String>,
        sms_gateway_url: Option<String>,
        cache_size: Option<usize>,
        battery_threshold: Option<u8>,
    ) -> Self {
        Self {
            llm_service_url: llm_service_url.unwrap_or_else(|| "http://localhost:8003".to_string()),
            rag_service_url: rag_service_url.unwrap_or_else(|| "http://localhost:8004".to_string()),
            sms_gateway_url: sms_gateway_url.unwrap_or_else(|| "http://localhost:8001".to_string()),
            cache_size: cache_size.unwrap_or(1000),
            battery_threshold: battery_threshold.unwrap_or(50),
        }
    }
}

impl From<PyRouterConfig> for RouterConfig {
    fn from(py_config: PyRouterConfig) -> Self {
        let mut config = RouterConfig::default();
        config.llm_service_url = py_config.llm_service_url;
        config.rag_service_url = py_config.rag_service_url;
        config.sms_gateway_url = py_config.sms_gateway_url;
        config.cache_size = py_config.cache_size;
        config.battery_threshold = py_config.battery_threshold;
        config
    }
}

/// Python wrapper for RouteDecision
#[pyclass]
#[derive(Clone)]
pub struct PyRouteDecision {
    #[pyo3(get)]
    service_type: String,
    #[pyo3(get)]
    service_url: String,
    #[pyo3(get)]
    requires_rag: bool,
    #[pyo3(get)]
    requires_llm: bool,
    #[pyo3(get)]
    priority: u8,
}

impl From<crate::service_registry::RouteDecision> for PyRouteDecision {
    fn from(route: crate::service_registry::RouteDecision) -> Self {
        let service_type = match route.service_type {
            crate::service_registry::ServiceType::LLM => "LLM",
            crate::service_registry::ServiceType::RAG => "RAG",
            crate::service_registry::ServiceType::Emergency => "Emergency",
            crate::service_registry::ServiceType::Template => "Template",
            crate::service_registry::ServiceType::Local => "Local",
            crate::service_registry::ServiceType::BigEVY => "BigEVY",
        }.to_string();
        
        Self {
            service_type,
            service_url: route.service_url,
            requires_rag: route.requires_rag,
            requires_llm: route.requires_llm,
            priority: route.priority,
        }
    }
}

/// Python wrapper for ClassificationResult
#[pyclass]
#[derive(Clone)]
pub struct PyClassificationResult {
    #[pyo3(get)]
    intent: String,
    #[pyo3(get)]
    priority: String,
    #[pyo3(get)]
    requires_rag: bool,
    #[pyo3(get)]
    requires_llm: bool,
    #[pyo3(get)]
    confidence: f32,
}

impl From<ClassificationResult> for PyClassificationResult {
    fn from(result: ClassificationResult) -> Self {
        let intent = match result.intent {
            Intent::Emergency => "Emergency",
            Intent::Command => "Command",
            Intent::Query => "Query",
            Intent::Greeting => "Greeting",
            Intent::Unknown => "Unknown",
        }.to_string();
        
        let priority = match result.priority {
            MessagePriority::Low => "Low",
            MessagePriority::Normal => "Normal",
            MessagePriority::High => "High",
            MessagePriority::Emergency => "Emergency",
        }.to_string();
        
        Self {
            intent,
            priority,
            requires_rag: result.requires_rag,
            requires_llm: result.requires_llm,
            confidence: result.confidence,
        }
    }
}

/// Python wrapper for RouterStats
#[pyclass]
#[derive(Clone)]
pub struct PyRouterStats {
    #[pyo3(get)]
    total_routes: usize,
    #[pyo3(get)]
    cache_hits: usize,
    #[pyo3(get)]
    cache_misses: usize,
    #[pyo3(get)]
    emergency_routes: usize,
    #[pyo3(get)]
    query_routes: usize,
    #[pyo3(get)]
    command_routes: usize,
    #[pyo3(get)]
    average_routing_time_ms: f64,
}

impl From<RouterStats> for PyRouterStats {
    fn from(stats: RouterStats) -> Self {
        Self {
            total_routes: stats.total_routes,
            cache_hits: stats.cache_hits,
            cache_misses: stats.cache_misses,
            emergency_routes: stats.emergency_routes,
            query_routes: stats.query_routes,
            command_routes: stats.command_routes,
            average_routing_time_ms: stats.average_routing_time_ms,
        }
    }
}

/// Python module definition
#[pymodule]
fn evy_message_router(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyMessageRouter>()?;
    m.add_class::<PyRouterConfig>()?;
    m.add_class::<PyRouteDecision>()?;
    m.add_class::<PyClassificationResult>()?;
    m.add_class::<PyRouterStats>()?;
    Ok(())
}

