//! EVY Compression Engine - Edge-optimized text compression
//! 
//! This module provides high-performance text compression for SMS responses,
//! optimized for Raspberry Pi 4 hardware constraints.

pub mod config;
pub mod rule_compressor;
pub mod cache;
pub mod engine;
pub mod error;
pub mod resource_monitor;

// Re-export main types
pub use engine::CompressionEngine;
pub use config::CompressionConfig;
pub use error::{CompressionError, Result};

#[cfg(feature = "python")]
pub mod python;

// Python module entry point
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pymodule]
fn evy_compression(_py: Python, m: &PyModule) -> PyResult<()> {
    python::evy_compression(_py, m)
}

