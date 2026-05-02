//! LRU cache for compression results

use lru::LruCache;
use std::num::NonZeroUsize;
use std::sync::Arc;
use tokio::sync::RwLock;

/// Compression cache using LRU eviction
pub struct CompressionCache {
    cache: Arc<RwLock<LruCache<String, String>>>,
}

impl CompressionCache {
    /// Create a new compression cache
    pub fn new(capacity: usize) -> Self {
        let capacity = NonZeroUsize::new(capacity.max(1)).unwrap();
        Self {
            cache: Arc::new(RwLock::new(LruCache::new(capacity))),
        }
    }
    
    /// Get cached compression result
    pub async fn get(&self, key: &str) -> Option<String> {
        let mut cache = self.cache.write().await;
        cache.get(key).cloned()
    }
    
    /// Put compression result in cache
    pub async fn put(&self, key: String, value: String) {
        let mut cache = self.cache.write().await;
        cache.put(key, value);
    }
    
    /// Check if key exists in cache
    pub async fn contains(&self, key: &str) -> bool {
        let cache = self.cache.read().await;
        cache.contains(key)
    }
    
    /// Clear the cache
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

