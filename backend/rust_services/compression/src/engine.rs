//! Main compression engine
//! 
//! Orchestrates rule-based compression, caching, and resource awareness

use crate::cache::CompressionCache;
use crate::config::CompressionConfig;
use crate::error::{CompressionError, Result};
use crate::resource_monitor::ResourceMonitor;
use crate::rule_compressor::RuleBasedCompressor;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info, warn};

/// Compression statistics
#[derive(Debug, Clone)]
pub struct CompressionStats {
    pub total_compressions: usize,
    pub cache_hits: usize,
    pub cache_misses: usize,
    pub average_compression_ratio: f32,
    pub average_compression_time_ms: f64,
}

/// Main compression engine
pub struct CompressionEngine {
    rule_compressor: RuleBasedCompressor,
    cache: Arc<CompressionCache>,
    resource_monitor: Arc<RwLock<ResourceMonitor>>,
    config: CompressionConfig,
    stats: Arc<RwLock<CompressionStats>>,
}

impl CompressionEngine {
    /// Create a new compression engine
    pub fn new(config: CompressionConfig) -> Self {
        let cache = Arc::new(CompressionCache::new(config.cache_size));
        let resource_monitor = Arc::new(RwLock::new(ResourceMonitor::new()));
        
        Self {
            rule_compressor: RuleBasedCompressor::new(),
            cache,
            resource_monitor,
            config,
            stats: Arc::new(RwLock::new(CompressionStats {
                total_compressions: 0,
                cache_hits: 0,
                cache_misses: 0,
                average_compression_ratio: 0.0,
                average_compression_time_ms: 0.0,
            })),
        }
    }
    
    /// Compress text to target length
    pub async fn compress(&self, text: &str, target_length: Option<usize>) -> Result<String> {
        let target = target_length.unwrap_or(self.config.target_length);
        
        // Validate input
        if text.is_empty() {
            return Err(CompressionError::TextTooShort(0));
        }
        
        if target < 10 {
            return Err(CompressionError::TargetTooSmall(target));
        }
        
        // Check cache first
        let cache_key = format!("{}:{}", text, target);
        if let Some(cached) = self.cache.get(&cache_key).await {
            let mut stats = self.stats.write().await;
            stats.cache_hits += 1;
            debug!("Cache hit for compression");
            return Ok(cached);
        }
        
        let mut stats = self.stats.write().await;
        stats.cache_misses += 1;
        drop(stats);
        
        // Check resources if resource-aware
        if self.config.resource_aware {
            let monitor = self.resource_monitor.read().await;
            
            // Check memory
            if !monitor.has_sufficient_memory(self.config.memory_threshold_mb) {
                warn!("Low memory ({}MB), using fast compression only", monitor.available_memory_mb());
            }
            
            // Check battery if battery-aware
            if self.config.battery_aware {
                if !monitor.has_sufficient_battery(self.config.battery_threshold) {
                    warn!("Low battery ({}%), using fast compression only", monitor.battery_level());
                }
            }
        }
        
        // Perform compression
        let start = std::time::Instant::now();
        let compressed = self.rule_compressor.compress(text, target);
        let duration = start.elapsed();
        
        // Update statistics
        let ratio = self.rule_compressor.compression_ratio(text, &compressed);
        let mut stats = self.stats.write().await;
        stats.total_compressions += 1;
        
        // Update running average
        let n_ratio = stats.total_compressions as f32;
        stats.average_compression_ratio = 
            (stats.average_compression_ratio * (n_ratio - 1.0) + ratio) / n_ratio;
        let n = stats.total_compressions as f64;
        stats.average_compression_time_ms = 
            (stats.average_compression_time_ms * (n - 1.0) + duration.as_millis() as f64) / n;
        
        // Cache the result
        self.cache.put(cache_key, compressed.clone()).await;
        
        debug!("Compressed in {}ms, ratio: {:.1}%", duration.as_millis(), ratio);
        Ok(compressed)
    }
    
    /// Compress with resource awareness
    pub async fn compress_with_resources(
        &self,
        text: &str,
        target_length: Option<usize>,
    ) -> Result<String> {
        // Check resources first
        let monitor = self.resource_monitor.read().await;
        
        if self.config.resource_aware {
            if !monitor.has_sufficient_memory(self.config.memory_threshold_mb) {
                return Err(CompressionError::InsufficientMemory(monitor.available_memory_mb()));
            }
        }
        
        if self.config.battery_aware {
            if !monitor.has_sufficient_battery(self.config.battery_threshold) {
                return Err(CompressionError::BatteryTooLow(monitor.battery_level()));
            }
        }
        
        drop(monitor);
        self.compress(text, target_length).await
    }
    
    /// Get compression statistics
    pub async fn get_stats(&self) -> CompressionStats {
        self.stats.read().await.clone()
    }
    
    /// Update resource monitor
    pub async fn update_resources(&self, memory_mb: usize, battery: u8, cpu: f32) {
        let mut monitor = self.resource_monitor.write().await;
        monitor.set_available_memory_mb(memory_mb);
        monitor.set_battery_level(battery);
        monitor.set_cpu_usage(cpu);
    }
    
    /// Clear compression cache
    pub async fn clear_cache(&self) {
        self.cache.clear().await;
        info!("Compression cache cleared");
    }
}

