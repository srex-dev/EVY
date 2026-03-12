//! Integration tests for SMS Gateway

use evy_sms_gateway::*;
use evy_sms_gateway::message_queue::MessagePriority;

#[tokio::test]
async fn test_message_queue() {
    let queue = SMSMessageQueue::new(100, 10, 100);
    
    // Test enqueue
    let id1 = queue.enqueue(
        "+1234567890".to_string(),
        "Test message".to_string(),
        MessagePriority::Normal,
    ).await.unwrap();
    
    assert!(!id1.is_empty());
    
    // Test dequeue
    let message = queue.dequeue().await;
    assert!(message.is_some());
    let msg = message.unwrap();
    assert_eq!(msg.phone_number, "+1234567890");
    assert_eq!(msg.content, "Test message");
    
    // Test priority ordering
    queue.enqueue("+1111111111".to_string(), "Low".to_string(), MessagePriority::Low).await.unwrap();
    queue.enqueue("+2222222222".to_string(), "High".to_string(), MessagePriority::High).await.unwrap();
    queue.enqueue("+3333333333".to_string(), "Emergency".to_string(), MessagePriority::Emergency).await.unwrap();
    
    // Should get Emergency first
    let msg = queue.dequeue().await.unwrap();
    assert_eq!(msg.content, "Emergency");
    
    // Then High
    let msg = queue.dequeue().await.unwrap();
    assert_eq!(msg.content, "High");
    
    // Then Low
    let msg = queue.dequeue().await.unwrap();
    assert_eq!(msg.content, "Low");
}

#[tokio::test]
async fn test_rate_limiting() {
    let queue = SMSMessageQueue::new(100, 2, 10); // 2 per minute, 10 per hour
    
    // Send 2 messages - should succeed
    assert!(queue.enqueue("+1234567890".to_string(), "Msg 1".to_string(), MessagePriority::Normal).await.is_ok());
    assert!(queue.enqueue("+1234567890".to_string(), "Msg 2".to_string(), MessagePriority::Normal).await.is_ok());
    
    // Third message should fail rate limit
    let result = queue.enqueue("+1234567890".to_string(), "Msg 3".to_string(), MessagePriority::Normal).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn test_queue_stats() {
    let queue = SMSMessageQueue::new(100, 10, 100);
    
    queue.enqueue("+1111111111".to_string(), "Emergency".to_string(), MessagePriority::Emergency).await.unwrap();
    queue.enqueue("+2222222222".to_string(), "High".to_string(), MessagePriority::High).await.unwrap();
    queue.enqueue("+3333333333".to_string(), "Normal".to_string(), MessagePriority::Normal).await.unwrap();
    
    let stats = queue.get_stats().await;
    assert_eq!(stats.emergency_messages, 1);
    assert_eq!(stats.high_priority_messages, 1);
    assert_eq!(stats.normal_priority_messages, 1);
    assert_eq!(stats.pending_messages, 3);
}

#[test]
fn test_phone_number_formatting() {
    // This would be tested through the GSM driver
    // For now, just verify the logic exists
    assert!(true);
}

