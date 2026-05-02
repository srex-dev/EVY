//! GSM HAT driver for SIM800C/SIM7000 modules
//! 
//! Provides low-level AT command interface for GSM communication

use crate::error::{GatewayError, Result};
use async_trait::async_trait;
use chrono::{DateTime, Utc};
use std::time::{Duration, Instant};
use tokio::time::timeout;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio_serial::{SerialPort, SerialPortBuilderExt, SerialStream};
use tracing::{debug, info, warn};

/// GSM driver trait for different implementations
#[async_trait]
pub trait GSMDriver: Send + Sync {
    /// Initialize the GSM connection
    async fn initialize(&mut self) -> Result<()>;
    
    /// Check if connected
    fn is_connected(&self) -> bool;
    
    /// Send SMS message
    async fn send_sms(&mut self, phone_number: &str, message: &str) -> Result<()>;
    
    /// Receive pending SMS messages
    async fn receive_sms(&mut self) -> Result<Vec<ReceivedSMS>>;
    
    /// Get signal strength (0-100)
    async fn get_signal_strength(&mut self) -> Result<u8>;
    
    /// Get network name
    async fn get_network_name(&mut self) -> Result<String>;
    
    /// Check if network is registered
    async fn is_network_registered(&mut self) -> Result<bool>;
    
    /// Disconnect from GSM module
    async fn disconnect(&mut self) -> Result<()>;
}

/// Received SMS message structure
#[derive(Debug, Clone)]
pub struct ReceivedSMS {
    pub id: String,
    pub sender: String,
    pub content: String,
    pub timestamp: DateTime<Utc>,
    pub folder: u8,
    pub location: u16,
}

/// Serial-based GSM driver using AT commands
pub struct SerialGSMDriver {
    port: Option<SerialStream>,
    config: SerialDriverConfig,
    last_command_time: Option<Instant>,
}

struct SerialDriverConfig {
    device: String,
    baud_rate: u32,
    timeout: Duration,
    min_command_interval: Duration,
}

impl SerialDriverConfig {
    fn new(device: String, baud_rate: u32) -> Self {
        Self {
            device,
            baud_rate,
            timeout: Duration::from_secs(5),
            min_command_interval: Duration::from_millis(100),
        }
    }
}

impl SerialGSMDriver {
    /// Create a new serial GSM driver
    pub fn new(device: String, baud_rate: u32) -> Self {
        Self {
            port: None,
            config: SerialDriverConfig::new(device, baud_rate),
            last_command_time: None,
        }
    }
    
    /// Send AT command and wait for response
    async fn send_at_command(&mut self, command: &str) -> Result<String> {
        // Rate limiting: ensure minimum interval between commands
        if let Some(last_time) = self.last_command_time {
            let elapsed = last_time.elapsed();
            if elapsed < self.config.min_command_interval {
                tokio::time::sleep(self.config.min_command_interval - elapsed).await;
            }
        }
        
        let port = self.port.as_mut().ok_or(GatewayError::NotConnected)?;
        
        // Clear input buffer
        let _ = port.clear(tokio_serial::ClearBuffer::Input);
        
        // Send command
        let cmd_bytes = format!("{}\r\n", command);
        port.write_all(cmd_bytes.as_bytes())
            .await
            .map_err(|e| GatewayError::Io(e))?;
        
        self.last_command_time = Some(Instant::now());
        
        // Read response with timeout
        let mut response = String::new();
        let mut buffer = [0u8; 256];
        let start = Instant::now();
        
        while start.elapsed() < self.config.timeout {
            match timeout(Duration::from_millis(100), port.read(&mut buffer)).await {
                Ok(Ok(n)) if n > 0 => {
                    let text = String::from_utf8_lossy(&buffer[..n]);
                    response.push_str(&text);
                    
                    // Check for end of response
                    if response.contains("OK") || response.contains("ERROR") {
                        break;
                    }
                }
                Ok(Ok(_)) => {
                    tokio::time::sleep(Duration::from_millis(10)).await;
                }
                Ok(Err(e)) => {
                    return Err(GatewayError::Io(e));
                }
                Err(_) => {
                    // Timeout on read, continue waiting
                    tokio::time::sleep(Duration::from_millis(10)).await;
                }
            }
        }
        
        if response.is_empty() {
            return Err(GatewayError::Timeout(format!(
                "No response to command: {}",
                command
            )));
        }
        
        debug!("AT command: {} -> {}", command, response.trim());
        Ok(response)
    }
    
    /// Wait for specific response
    async fn wait_for_response(&mut self, expected: &str) -> Result<()> {
        let mut buffer = [0u8; 256];
        let start = Instant::now();
        
        while start.elapsed() < self.config.timeout {
            match timeout(Duration::from_millis(100), self.port.as_mut().unwrap().read(&mut buffer)).await {
                Ok(Ok(n)) if n > 0 => {
                    let text = String::from_utf8_lossy(&buffer[..n]);
                    if text.contains(expected) {
                        return Ok(());
                    }
                    if text.contains("ERROR") {
                        return Err(GatewayError::AtCommandFailed(text.to_string()));
                    }
                }
                _ => {
                    tokio::time::sleep(Duration::from_millis(10)).await;
                }
            }
        }
        
        Err(GatewayError::Timeout(format!("Expected: {}", expected)))
    }
    
    /// Format phone number for SMS
    fn format_phone_number(&self, phone: &str) -> Result<String> {
        // Remove all non-digit characters
        let digits: String = phone.chars().filter(|c| c.is_ascii_digit()).collect();
        
        if digits.len() < 10 {
            return Err(GatewayError::InvalidPhoneNumber(phone.to_string()));
        }
        
        // Add country code if needed
        let formatted = if digits.len() == 10 {
            format!("+1{}", digits)
        } else if digits.len() == 11 && digits.starts_with('1') {
            format!("+{}", digits)
        } else if !digits.starts_with('+') {
            format!("+{}", digits)
        } else {
            format!("+{}", digits)
        };
        
        Ok(formatted)
    }
}

#[async_trait]
impl GSMDriver for SerialGSMDriver {
    async fn initialize(&mut self) -> Result<()> {
        info!("Initializing serial GSM driver on {}", self.config.device);
        
        // Try to open serial port
        let port = tokio_serial::new(&self.config.device, self.config.baud_rate)
            .open_native_async()
            .map_err(|e| GatewayError::Serial(e))?;
        
        self.port = Some(port);
        
        // Wait for module to be ready
        tokio::time::sleep(Duration::from_secs(2)).await;
        
        // Test connection with AT command
        let response = self.send_at_command("AT").await?;
        if !response.contains("OK") {
            return Err(GatewayError::InitializationFailed(
                "AT command failed".to_string(),
            ));
        }
        
        // Check if SIM card is ready
        let response = self.send_at_command("AT+CPIN?").await?;
        if !response.contains("READY") {
            warn!("SIM card may not be ready: {}", response);
        }
        
        // Set SMS text mode
        let response = self.send_at_command("AT+CMGF=1").await?;
        if !response.contains("OK") {
            return Err(GatewayError::InitializationFailed(
                "Failed to set SMS text mode".to_string(),
            ));
        }
        
        // Get network info
        let _ = self.get_network_name().await;
        let _ = self.get_signal_strength().await;
        
        info!("Serial GSM driver initialized successfully");
        Ok(())
    }
    
    fn is_connected(&self) -> bool {
        self.port.is_some()
    }
    
    async fn send_sms(&mut self, phone_number: &str, message: &str) -> Result<()> {
        if !self.is_connected() {
            return Err(GatewayError::NotConnected);
        }
        
        // Validate message length
        if message.len() > 160 {
            return Err(GatewayError::MessageTooLong(message.len()));
        }
        
        // Format phone number
        let formatted_number = self.format_phone_number(phone_number)?;
        
        info!("Sending SMS to {}: {}...", formatted_number, &message[..message.len().min(50)]);
        
        // Set SMS text mode (ensure it's set)
        self.send_at_command("AT+CMGF=1").await?;
        
        // Set recipient number
        let cmd = format!("AT+CMGS=\"{}\"", formatted_number);
        let response = self.send_at_command(&cmd).await?;
        
        if !response.contains(">") {
            return Err(GatewayError::AtCommandFailed(
                "Did not receive prompt for message".to_string(),
            ));
        }
        
        // Send message content with Ctrl+Z terminator
        let port = self.port.as_mut().unwrap();
        let message_bytes = format!("{}\x1A", message);
        port.write_all(message_bytes.as_bytes())
            .await
            .map_err(|e| GatewayError::Io(e))?;
        
        // Wait for confirmation
        self.wait_for_response("OK").await?;
        
        info!("SMS sent successfully to {}", formatted_number);
        Ok(())
    }
    
    async fn receive_sms(&mut self) -> Result<Vec<ReceivedSMS>> {
        if !self.is_connected() {
            return Err(GatewayError::NotConnected);
        }
        
        // List all unread SMS
        let response = self.send_at_command("AT+CMGL=\"REC UNREAD\"").await?;
        
        if response.contains("ERROR") {
            return Err(GatewayError::AtCommandFailed(response));
        }
        
        // Parse SMS messages from response
        let mut messages = Vec::new();
        let lines: Vec<&str> = response.lines().collect();
        
        let mut i = 0;
        while i < lines.len() {
            // Look for SMS header line (e.g., "+CMGL: 0,\"REC UNREAD\",\"+1234567890\",\"\",\"23/12/15,10:30:00+00\"")
            if lines[i].starts_with("+CMGL:") {
                // Parse header
                let parts: Vec<&str> = lines[i].split(',').collect();
                if parts.len() >= 5 {
                    let location = parts[0].split(':').nth(1).and_then(|s| s.trim().parse().ok()).unwrap_or(0);
                    let sender = parts[2].trim_matches('"');
                    
                    // Next line should be the message content
                    if i + 1 < lines.len() {
                        let content = lines[i + 1].trim().to_string();
                        let timestamp = Utc::now(); // TODO: Parse actual timestamp from header
                        
                        messages.push(ReceivedSMS {
                            id: format!("sms_{}_{}", location, timestamp.timestamp()),
                            sender: sender.to_string(),
                            content,
                            timestamp,
                            folder: 1, // Inbox
                            location: location as u16,
                        });
                        
                        i += 2;
                        continue;
                    }
                }
            }
            i += 1;
        }
        
        if !messages.is_empty() {
            info!("Received {} SMS messages", messages.len());
        }
        
        Ok(messages)
    }
    
    async fn get_signal_strength(&mut self) -> Result<u8> {
        if !self.is_connected() {
            return Err(GatewayError::NotConnected);
        }
        
        let response = self.send_at_command("AT+CSQ").await?;
        
        // Parse response: +CSQ: <rssi>,<ber>
        // RSSI: 0-31 (99 = not known/not detectable)
        // Convert to percentage: (rssi / 31) * 100
        if let Some(start) = response.find("+CSQ:") {
            let rest = &response[start + 5..];
            if let Some(comma) = rest.find(',') {
                if let Ok(rssi) = rest[..comma].trim().parse::<u8>() {
                    if rssi == 99 {
                        return Ok(0);
                    }
                    let percentage = (rssi as f32 / 31.0 * 100.0) as u8;
                    return Ok(percentage.min(100));
                }
            }
        }
        
        Ok(0)
    }
    
    async fn get_network_name(&mut self) -> Result<String> {
        if !self.is_connected() {
            return Err(GatewayError::NotConnected);
        }
        
        let response = self.send_at_command("AT+COPS?").await?;
        
        // Parse response: +COPS: <mode>[,<format>,<oper>]
        if let Some(start) = response.find("+COPS:") {
            let rest = &response[start + 6..];
            let parts: Vec<&str> = rest.split(',').collect();
            if parts.len() >= 3 {
                let name = parts[2].trim_matches('"');
                return Ok(name.to_string());
            }
        }
        
        Ok("Unknown".to_string())
    }
    
    async fn is_network_registered(&mut self) -> Result<bool> {
        if !self.is_connected() {
            return Err(GatewayError::NotConnected);
        }
        
        let response = self.send_at_command("AT+CREG?").await?;
        
        // Parse response: +CREG: <n>,<stat>
        // stat: 0=not registered, 1=registered (home), 2=searching, 3=denied, 5=registered (roaming)
        if let Some(start) = response.find("+CREG:") {
            let rest = &response[start + 6..];
            if let Some(comma) = rest.find(',') {
                if let Ok(stat) = rest[comma + 1..].trim().parse::<u8>() {
                    return Ok(stat == 1 || stat == 5);
                }
            }
        }
        
        Ok(false)
    }
    
    async fn disconnect(&mut self) -> Result<()> {
        if let Some(mut port) = self.port.take() {
            // Send AT command to put module in low power mode (optional)
            let _ = self.send_at_command("AT+CPOWD=1").await;
            
            // Close port
            port.shutdown().await.map_err(|e| GatewayError::Io(e))?;
            info!("GSM driver disconnected");
        }
        Ok(())
    }
}

