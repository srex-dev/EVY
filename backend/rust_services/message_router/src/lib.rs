//! EVY Message Router - High-performance message routing
//! 
//! This module provides fast message routing with resource awareness,
//! optimized for Raspberry Pi 4 hardware constraints.

pub mod config;
pub mod intent_classifier;
pub mod service_registry;
pub mod router;
pub mod error;
pub mod resource_monitor;

// Re-export main types
pub use router::MessageRouter;
pub use config::RouterConfig;
pub use error::{RouterError, Result};

#[cfg(feature = "python")]
pub mod python;

// Python module entry point
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pymodule]
fn evy_message_router(_py: Python, m: &PyModule) -> PyResult<()> {
    python::evy_message_router(_py, m)
}

