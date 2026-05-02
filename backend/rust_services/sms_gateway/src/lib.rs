//! EVY SMS Gateway - High-performance Rust implementation
//! 
//! This module provides a high-performance SMS gateway for EVY edge nodes,
//! optimized for Raspberry Pi 4 hardware constraints.

pub mod config;
pub mod gsm_driver;
pub mod message_queue;
pub mod gateway;
pub mod error;

// Re-export main types
pub use gateway::SMSGateway;
pub use config::GatewayConfig;
pub use error::{GatewayError, Result};
pub use message_queue::{MessagePriority, QueueStats, QueuedMessage, SMSMessageQueue};

#[cfg(feature = "python")]
pub mod python;

// Python module entry point
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pymodule]
fn evy_sms_gateway(_py: Python, m: &PyModule) -> PyResult<()> {
    python::evy_sms_gateway(_py, m)
}

