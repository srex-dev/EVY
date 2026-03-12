//! PyO3 bindings for Python integration

use crate::config::CompressionConfig;
use crate::engine::{CompressionEngine, CompressionStats};
use crate::error::CompressionError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::sync::Arc;
use tokio::runtime::Runtime;

/// Python wrapper for Compression Engine
#[pyclass]
pub struct PyCompressionEngine {
    engine: Arc<CompressionEngine>,
    runtime: Runtime,
}

#[pymethods]
impl PyCompressionEngine {
    /// Create a new compression engine
    #[new]
    fn new(config: Option<PyCompressionConfig>) -> PyResult<Self> {
        let config = config.map(|c| c.into()).unwrap_or_else(CompressionConfig::default);
        let engine = CompressionEngine::new(config);
        
        let runtime = Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;
        
        Ok(Self {
            engine: Arc::new(engine),
            runtime,
        })
    }
    
    /// Compress text
    fn compress(&self, text: String, target_length: Option<usize>) -> PyResult<String> {
        let engine = Arc::clone(&self.engine);
        self.runtime.block_on(async {
            engine.compress(&text, target_length).await
                .map_err(|e| PyRuntimeError::new_err(format!("Compression failed: {}", e)))
        })
    }
    
    /// Compress with resource awareness
    fn compress_with_resources(
        &self,
        text: String,
        target_length: Option<usize>,
    ) -> PyResult<String> {
        let engine = Arc::clone(&self.engine);
        self.runtime.block_on(async {
            engine.compress_with_resources(&text, target_length).await
                .map_err(|e| PyRuntimeError::new_err(format!("Compression failed: {}", e)))
        })
    }
    
    /// Get compression statistics
    fn get_stats(&self) -> PyResult<PyCompressionStats> {
        let engine = Arc::clone(&self.engine);
        let stats = self.runtime.block_on(async {
            engine.get_stats().await
        });
        
        Ok(PyCompressionStats::from(stats))
    }
    
    /// Update resource monitor
    fn update_resources(&self, memory_mb: usize, battery: u8, cpu: f32) {
        let engine = Arc::clone(&self.engine);
        self.runtime.block_on(async {
            engine.update_resources(memory_mb, battery, cpu).await;
        });
    }
    
    /// Clear cache
    fn clear_cache(&self) {
        let engine = Arc::clone(&self.engine);
        self.runtime.block_on(async {
            engine.clear_cache().await;
        });
    }
}

/// Python wrapper for CompressionConfig
#[pyclass]
#[derive(Clone)]
pub struct PyCompressionConfig {
    #[pyo3(get, set)]
    target_length: usize,
    #[pyo3(get, set)]
    compression_level: f32,
    #[pyo3(get, set)]
    cache_size: usize,
}

#[pymethods]
impl PyCompressionConfig {
    #[new]
    fn new(
        target_length: Option<usize>,
        compression_level: Option<f32>,
        cache_size: Option<usize>,
    ) -> Self {
        Self {
            target_length: target_length.unwrap_or(160),
            compression_level: compression_level.unwrap_or(0.7),
            cache_size: cache_size.unwrap_or(1000),
        }
    }
}

impl From<PyCompressionConfig> for CompressionConfig {
    fn from(py_config: PyCompressionConfig) -> Self {
        let mut config = CompressionConfig::default();
        config.target_length = py_config.target_length;
        config.compression_level = py_config.compression_level;
        config.cache_size = py_config.cache_size;
        config
    }
}

/// Python wrapper for CompressionStats
#[pyclass]
#[derive(Clone)]
pub struct PyCompressionStats {
    #[pyo3(get)]
    total_compressions: usize,
    #[pyo3(get)]
    cache_hits: usize,
    #[pyo3(get)]
    cache_misses: usize,
    #[pyo3(get)]
    average_compression_ratio: f32,
    #[pyo3(get)]
    average_compression_time_ms: f64,
}

impl From<CompressionStats> for PyCompressionStats {
    fn from(stats: CompressionStats) -> Self {
        Self {
            total_compressions: stats.total_compressions,
            cache_hits: stats.cache_hits,
            cache_misses: stats.cache_misses,
            average_compression_ratio: stats.average_compression_ratio,
            average_compression_time_ms: stats.average_compression_time_ms,
        }
    }
}

/// Python module definition
#[pymodule]
fn evy_compression(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyCompressionEngine>()?;
    m.add_class::<PyCompressionConfig>()?;
    m.add_class::<PyCompressionStats>()?;
    Ok(())
}

