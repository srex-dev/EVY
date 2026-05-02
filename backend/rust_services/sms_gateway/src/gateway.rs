//! Main SMS Gateway service
//! 
//! Orchestrates GSM driver, message queue, and power management

use crate::config::GatewayConfig;
use crate::error::{GatewayError, Result};
use crate::gsm_driver::{GSMDriver, SerialGSMDriver};
use crate::message_queue::{MessagePriority, SMSMessageQueue};
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::time::{interval, Duration};
use tracing::{error, info, warn};

/// Power monitoring (placeholder - would integrate with actual power monitoring)
pub struct PowerMonitor {
    battery_level: u8,
    power_aware_enabled: bool,
    threshold: u8,
}

impl PowerMonitor {
    pub fn new(threshold: u8, enabled: bool) -> Self {
        Self {
            battery_level: 100, // Default to full
            power_aware_enabled: enabled,
            threshold,
        }
    }
    
    pub fn get_battery_level(&self) -> u8 {
        self.battery_level
    }
    
    pub fn set_battery_level(&mut self, level: u8) {
        self.battery_level = level;
    }
    
    pub fn is_power_aware(&self) -> bool {
        self.power_aware_enabled && self.battery_level < self.threshold
    }
}

/// Main SMS Gateway service
pub struct SMSGateway {
    driver: Arc<RwLock<SerialGSMDriver>>,
    queue: Arc<SMSMessageQueue>,
    power_monitor: Arc<RwLock<PowerMonitor>>,
    config: GatewayConfig,
    processing_task: Option<tokio::task::JoinHandle<()>>,
    receive_task: Option<tokio::task::JoinHandle<()>>,
}

impl SMSGateway {
    /// Create a new SMS Gateway
    pub fn new(config: GatewayConfig) -> Self {
        let driver = SerialGSMDriver::new(
            config.device.clone(),
            config.baud_rate,
        );
        
        let queue = Arc::new(SMSMessageQueue::new(
            config.queue_size,
            config.max_sms_per_minute,
            config.max_sms_per_hour,
        ));
        
        let power_monitor = Arc::new(RwLock::new(PowerMonitor::new(
            config.power_aware_threshold,
            config.power_aware_enabled,
        )));
        
        Self {
            driver: Arc::new(RwLock::new(driver)),
            queue,
            power_monitor,
            config,
            processing_task: None,
            receive_task: None,
        }
    }
    
    /// Initialize the gateway
    pub async fn initialize(&mut self) -> Result<()> {
        info!("Initializing SMS Gateway...");
        
        // Initialize GSM driver
        let mut driver = self.driver.write().await;
        driver.initialize().await?;
        drop(driver);
        
        // Check power level
        let power = self.power_monitor.read().await;
        if power.is_power_aware() {
            warn!("Power level low ({}%), enabling power-aware mode", power.get_battery_level());
        }
        drop(power);
        
        // Start background tasks
        self.start_processing_task();
        self.start_receive_task();
        
        info!("SMS Gateway initialized successfully");
        Ok(())
    }
    
    /// Start message processing task
    fn start_processing_task(&mut self) {
        let queue = Arc::clone(&self.queue);
        let driver = Arc::clone(&self.driver);
        let power_monitor = Arc::clone(&self.power_monitor);
        let retry_attempts = self.config.retry_attempts;
        let retry_delay = Duration::from_millis(self.config.retry_delay_ms);
        
        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(1));
            
            loop {
                interval.tick().await;
                
                // Check power level
                let power = power_monitor.read().await;
                if power.is_power_aware() {
                    // Reduce processing frequency in power-aware mode
                    tokio::time::sleep(Duration::from_secs(5)).await;
                    continue;
                }
                drop(power);
                
                // Dequeue next message
                if let Some(message) = queue.dequeue().await {
                    // Try to send
                    let mut driver_guard = driver.write().await;
                    let mut success = false;
                    
                    for attempt in 0..retry_attempts {
                        match driver_guard.send_sms(&message.phone_number, &message.content).await {
                            Ok(()) => {
                                success = true;
                                info!("SMS sent successfully: {} -> {}", message.id, message.phone_number);
                                break;
                            }
                            Err(e) => {
                                warn!("SMS send failed (attempt {}/{}): {}", attempt + 1, retry_attempts, e);
                                if attempt < retry_attempts - 1 {
                                    tokio::time::sleep(retry_delay).await;
                                }
                            }
                        }
                    }
                    
                    if !success {
                        error!("Failed to send SMS after {} attempts: {}", retry_attempts, message.id);
                        // TODO: Move to failed queue or notify
                    }
                }
            }
        });
        
        self.processing_task = Some(handle);
    }
    
    /// Start SMS receive task
    fn start_receive_task(&mut self) {
        let driver = Arc::clone(&self.driver);
        
        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(10));
            
            loop {
                interval.tick().await;
                
                let mut driver_guard = driver.write().await;
                match driver_guard.receive_sms().await {
                    Ok(messages) => {
                        for msg in messages {
                            info!("Received SMS from {}: {}...", msg.sender, &msg.content[..msg.content.len().min(50)]);
                            // TODO: Forward to message router via callback
                        }
                    }
                    Err(e) => {
                        warn!("Error receiving SMS: {}", e);
                    }
                }
            }
        });
        
        self.receive_task = Some(handle);
    }
    
    /// Send SMS message
    pub async fn send_sms(
        &self,
        phone_number: String,
        content: String,
        priority: MessagePriority,
    ) -> Result<String> {
        // Validate message length
        if content.len() > 160 {
            return Err(GatewayError::MessageTooLong(content.len()));
        }
        
        // Check power level
        let power = self.power_monitor.read().await;
        if power.is_power_aware() && priority < MessagePriority::High {
            return Err(GatewayError::PowerTooLow(power.get_battery_level()));
        }
        drop(power);
        
        // Enqueue message
        self.queue.enqueue(phone_number, content, priority).await
    }
    
    /// Get gateway statistics
    pub async fn get_stats(&self) -> GatewayStats {
        let queue_stats = self.queue.get_stats().await;
        let driver = self.driver.read().await;
        let power = self.power_monitor.read().await;
        
        GatewayStats {
            connected: driver.is_connected(),
            queue_stats,
            battery_level: power.get_battery_level(),
            power_aware_mode: power.is_power_aware(),
        }
    }
    
    /// Shutdown the gateway
    pub async fn shutdown(&mut self) -> Result<()> {
        info!("Shutting down SMS Gateway...");
        
        // Cancel background tasks
        if let Some(task) = self.processing_task.take() {
            task.abort();
        }
        if let Some(task) = self.receive_task.take() {
            task.abort();
        }
        
        // Disconnect driver
        let mut driver = self.driver.write().await;
        driver.disconnect().await?;
        
        info!("SMS Gateway shutdown complete");
        Ok(())
    }
}

/// Gateway statistics
#[derive(Debug, Clone)]
pub struct GatewayStats {
    pub connected: bool,
    pub queue_stats: crate::message_queue::QueueStats,
    pub battery_level: u8,
    pub power_aware_mode: bool,
}
