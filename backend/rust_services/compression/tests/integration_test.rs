//! Integration tests for Compression Engine

use evy_compression::*;
use evy_compression::rule_compressor::RuleBasedCompressor;

#[tokio::test]
async fn test_rule_based_compression() {
    let compressor = RuleBasedCompressor::new();
    
    let text = "The emergency medical services are on their way to the hospital";
    let compressed = compressor.compress(text, 50);
    
    assert!(compressed.len() <= 50);
    assert!(compressed.len() < text.len());
    println!("Compressed: '{}' -> '{}'", text, compressed);
}

#[tokio::test]
async fn test_compression_engine() {
    let config = CompressionConfig::default();
    let engine = CompressionEngine::new(config);
    
    let text = "Please call the emergency services as soon as possible. The hospital is located on Main Street.";
    let compressed = engine.compress(text, Some(80)).await.unwrap();
    
    assert!(compressed.len() <= 80);
    println!("Compressed: {} -> {} chars", text.len(), compressed.len());
}

#[tokio::test]
async fn test_cache() {
    let config = CompressionConfig::default();
    let engine = CompressionEngine::new(config);
    
    let text = "This is a test message that will be compressed";
    
    // First compression
    let compressed1 = engine.compress(text, Some(30)).await.unwrap();
    
    // Second compression (should use cache)
    let compressed2 = engine.compress(text, Some(30)).await.unwrap();
    
    assert_eq!(compressed1, compressed2);
    
    let stats = engine.get_stats().await;
    assert!(stats.cache_hits > 0);
}

#[tokio::test]
async fn test_compression_ratio() {
    let compressor = RuleBasedCompressor::new();
    
    let text = "The emergency medical services are on their way to the hospital as soon as possible";
    let compressed = compressor.compress(text, 50);
    
    let ratio = compressor.compression_ratio(text, &compressed);
    assert!(ratio > 0.0);
    println!("Compression ratio: {:.1}%", ratio);
}

#[tokio::test]
async fn test_short_text() {
    let engine = CompressionEngine::new(CompressionConfig::default());
    
    let text = "Short";
    let result = engine.compress(text, Some(160)).await;
    
    // Should return original text if already short enough
    assert!(result.is_ok());
    let compressed = result.unwrap();
    assert_eq!(compressed, text);
}

#[tokio::test]
async fn test_resource_aware() {
    let mut config = CompressionConfig::default();
    config.resource_aware = true;
    config.battery_aware = true;
    config.memory_threshold_mb = 100;
    config.battery_threshold = 30;
    
    let engine = CompressionEngine::new(config);
    
    // Set low battery
    engine.update_resources(200, 25, 0.5).await;
    
    // Should still compress (just warns, doesn't fail)
    let text = "This is a test message for resource-aware compression";
    let result = engine.compress(text, Some(40)).await;
    assert!(result.is_ok());
}

#[test]
fn test_abbreviations() {
    let compressor = RuleBasedCompressor::new();
    
    let text = "thank you for your information";
    let compressed = compressor.compress(text, 20);
    
    // Should use abbreviations
    assert!(compressed.len() <= 20);
    println!("Abbreviation test: '{}' -> '{}'", text, compressed);
}

