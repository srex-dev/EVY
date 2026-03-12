//! Integration tests for Message Router

use evy_message_router::*;
use evy_message_router::intent_classifier::Intent;

#[tokio::test]
async fn test_intent_classification() {
    let classifier = intent_classifier::IntentClassifier::new();
    
    // Test emergency
    let result = classifier.classify("EMERGENCY! Fire in building!");
    assert_eq!(result.intent, Intent::Emergency);
    assert_eq!(result.priority, intent_classifier::MessagePriority::Emergency);
    
    // Test command
    let result = classifier.classify("/help");
    assert_eq!(result.intent, Intent::Command);
    
    // Test query
    let result = classifier.classify("What's the weather like?");
    assert_eq!(result.intent, Intent::Query);
    assert!(result.requires_rag);
    
    // Test greeting
    let result = classifier.classify("Hello there!");
    assert_eq!(result.intent, Intent::Greeting);
}

#[tokio::test]
async fn test_message_routing() {
    let config = RouterConfig::default();
    let router = MessageRouter::new(config);
    router.initialize().await.unwrap();
    
    let message = router::Message {
        id: "test1".to_string(),
        sender: "+1234567890".to_string(),
        content: "What's the weather?".to_string(),
        timestamp: chrono::Utc::now(),
    };
    
    let route = router.route(&message).await.unwrap();
    assert_eq!(route.service_type, service_registry::ServiceType::LLM);
    assert!(route.requires_llm);
}

#[tokio::test]
async fn test_emergency_routing() {
    let config = RouterConfig::default();
    let router = MessageRouter::new(config);
    router.initialize().await.unwrap();
    
    let message = router::Message {
        id: "test2".to_string(),
        sender: "+1234567890".to_string(),
        content: "EMERGENCY! Help needed!".to_string(),
        timestamp: chrono::Utc::now(),
    };
    
    let route = router.route(&message).await.unwrap();
    assert_eq!(route.service_type, service_registry::ServiceType::Emergency);
    assert!(!route.requires_llm);
}

#[tokio::test]
async fn test_routing_cache() {
    let config = RouterConfig::default();
    let router = MessageRouter::new(config);
    router.initialize().await.unwrap();
    
    let message = router::Message {
        id: "test3".to_string(),
        sender: "+1234567890".to_string(),
        content: "What time is it?".to_string(),
        timestamp: chrono::Utc::now(),
    };
    
    // First route (cache miss)
    let route1 = router.route(&message).await.unwrap();
    
    // Second route (cache hit)
    let route2 = router.route(&message).await.unwrap();
    
    assert_eq!(route1.service_type, route2.service_type);
    
    let stats = router.get_stats().await;
    assert!(stats.cache_hits > 0);
}

#[tokio::test]
async fn test_battery_aware_routing() {
    let mut config = RouterConfig::default();
    config.battery_aware = true;
    config.battery_threshold = 50;
    
    let router = MessageRouter::new(config);
    router.initialize().await.unwrap();
    
    // Set low battery
    router.update_resources(200, 30, 0.5).await;
    
    let message = router::Message {
        id: "test4".to_string(),
        sender: "+1234567890".to_string(),
        content: "Complex query that might need bigEVY".to_string(),
        timestamp: chrono::Utc::now(),
    };
    
    // Should route to local LLM instead of bigEVY
    let route = router.route(&message).await.unwrap();
    assert_eq!(route.service_type, service_registry::ServiceType::LLM);
}

#[test]
fn test_classification_confidence() {
    let classifier = intent_classifier::IntentClassifier::new();
    
    // Emergency should have high confidence
    let result = classifier.classify("EMERGENCY 911");
    assert!(result.confidence > 0.8);
    
    // Commands should have high confidence
    let result = classifier.classify("/status");
    assert!(result.confidence > 0.9);
}

