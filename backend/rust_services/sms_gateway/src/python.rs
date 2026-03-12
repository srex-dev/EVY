//! PyO3 bindings for Python integration

use crate::config::GatewayConfig;
use crate::gateway::{SMSGateway, GatewayStats};
use crate::message_queue::MessagePriority;
use crate::error::GatewayError;
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use std::sync::Arc;
use tokio::runtime::Runtime;

/// Python wrapper for SMS Gateway
#[pyclass]
pub struct PySMSGateway {
    gateway: Arc<tokio::sync::Mutex<SMSGateway>>,
    runtime: Runtime,
}

#[pymethods]
impl PySMSGateway {
    /// Create a new SMS Gateway
    #[new]
    fn new(config: Option<PyGatewayConfig>) -> PyResult<Self> {
        let config = config.map(|c| c.into()).unwrap_or_else(GatewayConfig::default);
        let gateway = SMSGateway::new(config);
        
        let runtime = Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;
        
        Ok(Self {
            gateway: Arc::new(tokio::sync::Mutex::new(gateway)),
            runtime,
        })
    }
    
    /// Initialize the gateway
    fn initialize(&self) -> PyResult<()> {
        let gateway = Arc::clone(&self.gateway);
        self.runtime.block_on(async {
            let mut g = gateway.lock().await;
            g.initialize().await
                .map_err(|e| PyRuntimeError::new_err(format!("Initialization failed: {}", e)))
        })
    }
    
    /// Send SMS message
    fn send_sms(
        &self,
        phone_number: String,
        content: String,
        priority: Option<u8>,
    ) -> PyResult<String> {
        let gateway = Arc::clone(&self.gateway);
        let msg_priority = match priority {
            Some(0) => MessagePriority::Low,
            Some(1) => MessagePriority::Normal,
            Some(2) => MessagePriority::High,
            Some(3) => MessagePriority::Emergency,
            _ => MessagePriority::Normal,
        };
        
        self.runtime.block_on(async {
            let g = gateway.lock().await;
            g.send_sms(phone_number, content, msg_priority).await
                .map_err(|e| PyRuntimeError::new_err(format!("Send failed: {}", e)))
        })
    }
    
    /// Get gateway statistics
    fn get_stats(&self) -> PyResult<PyGatewayStats> {
        let gateway = Arc::clone(&self.gateway);
        let stats = self.runtime.block_on(async {
            let g = gateway.lock().await;
            g.get_stats().await
        });
        
        Ok(PyGatewayStats::from(stats))
    }
    
    /// Shutdown the gateway
    fn shutdown(&mut self) -> PyResult<()> {
        let gateway = Arc::clone(&self.gateway);
        self.runtime.block_on(async {
            let mut g = gateway.lock().await;
            g.shutdown().await
                .map_err(|e| PyRuntimeError::new_err(format!("Shutdown failed: {}", e)))
        })
    }
}

/// Python wrapper for GatewayConfig
#[pyclass]
#[derive(Clone)]
pub struct PyGatewayConfig {
    #[pyo3(get, set)]
    device: String,
    #[pyo3(get, set)]
    baud_rate: u32,
    #[pyo3(get, set)]
    max_sms_per_minute: u32,
    #[pyo3(get, set)]
    max_sms_per_hour: u32,
}

#[pymethods]
impl PyGatewayConfig {
    #[new]
    fn new(
        device: Option<String>,
        baud_rate: Option<u32>,
        max_sms_per_minute: Option<u32>,
        max_sms_per_hour: Option<u32>,
    ) -> Self {
        Self {
            device: device.unwrap_or_else(|| "/dev/ttyUSB0".to_string()),
            baud_rate: baud_rate.unwrap_or(115200),
            max_sms_per_minute: max_sms_per_minute.unwrap_or(10),
            max_sms_per_hour: max_sms_per_hour.unwrap_or(100),
        }
    }
}

impl From<PyGatewayConfig> for GatewayConfig {
    fn from(py_config: PyGatewayConfig) -> Self {
        let mut config = GatewayConfig::default();
        config.device = py_config.device;
        config.baud_rate = py_config.baud_rate;
        config.max_sms_per_minute = py_config.max_sms_per_minute;
        config.max_sms_per_hour = py_config.max_sms_per_hour;
        config
    }
}

/// Python wrapper for GatewayStats
#[pyclass]
#[derive(Clone)]
pub struct PyGatewayStats {
    #[pyo3(get)]
    connected: bool,
    #[pyo3(get)]
    pending_messages: usize,
    #[pyo3(get)]
    emergency_messages: usize,
    #[pyo3(get)]
    high_priority_messages: usize,
    #[pyo3(get)]
    normal_priority_messages: usize,
    #[pyo3(get)]
    low_priority_messages: usize,
    #[pyo3(get)]
    battery_level: u8,
    #[pyo3(get)]
    power_aware_mode: bool,
}

impl From<GatewayStats> for PyGatewayStats {
    fn from(stats: GatewayStats) -> Self {
        Self {
            connected: stats.connected,
            pending_messages: stats.queue_stats.pending_messages,
            emergency_messages: stats.queue_stats.emergency_messages,
            high_priority_messages: stats.queue_stats.high_priority_messages,
            normal_priority_messages: stats.queue_stats.normal_priority_messages,
            low_priority_messages: stats.queue_stats.low_priority_messages,
            battery_level: stats.battery_level,
            power_aware_mode: stats.power_aware_mode,
        }
    }
}

/// Python module definition
#[pymodule]
fn evy_sms_gateway(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySMSGateway>()?;
    m.add_class::<PyGatewayConfig>()?;
    m.add_class::<PyGatewayStats>()?;
    Ok(())
}

