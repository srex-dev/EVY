"""GSM HAT driver for SMS communication."""
import asyncio
import serial
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import gammu
from backend.shared.config import settings

logger = logging.getLogger(__name__)


class GSMDriver:
    """GSM HAT driver using Gammu library."""
    
    def __init__(self):
        self.state_machine = None
        self.is_connected = False
        self.signal_strength = 0
        self.network_name = ""
        self.phone_number = ""
        
    async def initialize(self) -> bool:
        """Initialize GSM connection."""
        try:
            # Configure Gammu state machine
            self.state_machine = gammu.StateMachine()
            
            # Try different device configurations
            configs = [
                {
                    'Device': settings.sms_device,
                    'Connection': 'serial',
                    'BaudRate': settings.sms_baud_rate,
                    'DataBits': 8,
                    'StopBits': 1,
                    'Parity': 'None',
                    'FlowControl': 'None'
                },
                {
                    'Device': '/dev/ttyACM0',  # Alternative device path
                    'Connection': 'serial',
                    'BaudRate': 115200,
                    'DataBits': 8,
                    'StopBits': 1,
                    'Parity': 'None',
                    'FlowControl': 'None'
                }
            ]
            
            for config in configs:
                try:
                    self.state_machine.ReadConfig(config)
                    await asyncio.sleep(1)  # Wait for connection
                    
                    # Test connection
                    self.state_machine.Init()
                    self.is_connected = True
                    
                    # Get device info
                    await self._get_device_info()
                    
                    logger.info(f"GSM connection established on {config['Device']}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to connect on {config['Device']}: {e}")
                    continue
            
            logger.error("Failed to establish GSM connection on any device")
            return False
            
        except Exception as e:
            logger.error(f"GSM initialization failed: {e}")
            return False
    
    async def _get_device_info(self) -> None:
        """Get device information."""
        try:
            # Get network info
            network_info = self.state_machine.GetNetworkInfo()
            self.network_name = network_info.get('NetworkName', 'Unknown')
            
            # Get signal strength
            signal_info = self.state_machine.GetSignalQuality()
            self.signal_strength = signal_info.get('SignalPercent', 0)
            
            # Get phone number
            identity = self.state_machine.GetIMEI()
            self.phone_number = identity.get('IMEI', 'Unknown')
            
            logger.info(f"Network: {self.network_name}, Signal: {self.signal_strength}%, IMEI: {self.phone_number}")
            
        except Exception as e:
            logger.warning(f"Could not get device info: {e}")
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS message."""
        if not self.is_connected:
            logger.error("GSM not connected")
            return False
        
        try:
            # Validate phone number format
            phone_number = self._format_phone_number(phone_number)
            if not phone_number:
                logger.error(f"Invalid phone number format: {phone_number}")
                return False
            
            # Check message length
            if len(message) > 160:
                logger.error(f"Message too long: {len(message)} characters")
                return False
            
            # Create SMS message
            sms_message = {
                'Text': message,
                'SMSC': {'Location': 1},
                'Number': phone_number,
            }
            
            # Send SMS
            self.state_machine.SendSMS(sms_message)
            
            logger.info(f"SMS sent to {phone_number}: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    async def receive_sms(self) -> List[Dict[str, Any]]:
        """Receive pending SMS messages."""
        if not self.is_connected:
            logger.error("GSM not connected")
            return []
        
        try:
            messages = []
            
            # Get SMS memory status
            status = self.state_machine.GetSMSFoldersStatus()
            
            for folder in status:
                if folder['New'] > 0:
                    # Read messages from this folder
                    start = True
                    
                    while True:
                        try:
                            if start:
                                sms_list = self.state_machine.GetNextSMS(Start=True, Folder=folder['Folder'])
                                start = False
                            else:
                                sms_list = self.state_machine.GetNextSMS(Location=sms_list[0]['Location'], Folder=folder['Folder'])
                            
                            for sms in sms_list:
                                message = {
                                    'id': f"sms_{sms['Location']}_{datetime.utcnow().timestamp()}",
                                    'sender': sms['Number'],
                                    'content': sms['Text'],
                                    'timestamp': sms['DateTime'],
                                    'folder': folder['Folder'],
                                    'location': sms['Location']
                                }
                                messages.append(message)
                                
                        except gammu.ERR_EMPTY:
                            break
                        except Exception as e:
                            logger.error(f"Error reading SMS: {e}")
                            break
            
            if messages:
                logger.info(f"Received {len(messages)} new SMS messages")
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to receive SMS: {e}")
            return []
    
    async def delete_sms(self, folder: int, location: int) -> bool:
        """Delete SMS message."""
        if not self.is_connected:
            return False
        
        try:
            self.state_machine.DeleteSMS(Folder=folder, Location=location)
            logger.info(f"Deleted SMS from folder {folder}, location {location}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete SMS: {e}")
            return False
    
    async def get_signal_strength(self) -> int:
        """Get current signal strength."""
        if not self.is_connected:
            return 0
        
        try:
            signal_info = self.state_machine.GetSignalQuality()
            self.signal_strength = signal_info.get('SignalPercent', 0)
            return self.signal_strength
        except Exception as e:
            logger.error(f"Failed to get signal strength: {e}")
            return 0
    
    async def is_network_available(self) -> bool:
        """Check if network is available."""
        if not self.is_connected:
            return False
        
        try:
            network_info = self.state_machine.GetNetworkInfo()
            return network_info.get('State') == 'Registered'
        except Exception as e:
            logger.error(f"Failed to check network status: {e}")
            return False
    
    def _format_phone_number(self, phone_number: str) -> Optional[str]:
        """Format phone number for SMS sending."""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone_number)
        
        # Add country code if missing
        if len(digits) == 10:
            digits = '+1' + digits  # Assume US number
        elif len(digits) == 11 and digits.startswith('1'):
            digits = '+' + digits
        elif not digits.startswith('+'):
            digits = '+' + digits
        
        # Validate format
        if len(digits) < 10:
            return None
        
        return digits
    
    async def disconnect(self) -> None:
        """Disconnect GSM connection."""
        if self.is_connected and self.state_machine:
            try:
                self.state_machine.Terminate()
                self.is_connected = False
                logger.info("GSM connection terminated")
            except Exception as e:
                logger.error(f"Error disconnecting GSM: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get GSM health status."""
        return {
            'connected': self.is_connected,
            'signal_strength': self.signal_strength,
            'network_name': self.network_name,
            'phone_number': self.phone_number,
            'network_available': await self.is_network_available() if self.is_connected else False
        }


class SerialGSMDriver:
    """Alternative GSM driver using direct serial communication."""
    
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        
    async def initialize(self) -> bool:
        """Initialize serial connection to GSM module."""
        try:
            # Try different serial configurations
            configs = [
                {'port': settings.sms_device, 'baudrate': settings.sms_baud_rate},
                {'port': '/dev/ttyACM0', 'baudrate': 115200},
                {'port': '/dev/ttyUSB1', 'baudrate': 115200},
            ]
            
            for config in configs:
                try:
                    self.serial_connection = serial.Serial(
                        port=config['port'],
                        baudrate=config['baudrate'],
                        timeout=1,
                        write_timeout=1
                    )
                    
                    # Test connection with AT command
                    await self._send_at_command('AT')
                    await asyncio.sleep(1)
                    
                    # Check if GSM module responds
                    response = await self._send_at_command('AT+CPIN?')
                    if 'READY' in response:
                        self.is_connected = True
                        logger.info(f"Serial GSM connection established on {config['port']}")
                        return True
                    
                except Exception as e:
                    logger.warning(f"Failed to connect on {config['port']}: {e}")
                    if self.serial_connection:
                        self.serial_connection.close()
                    continue
            
            logger.error("Failed to establish serial GSM connection")
            return False
            
        except Exception as e:
            logger.error(f"Serial GSM initialization failed: {e}")
            return False
    
    async def _send_at_command(self, command: str, timeout: float = 5.0) -> str:
        """Send AT command and get response."""
        if not self.serial_connection:
            raise Exception("Serial connection not established")
        
        try:
            # Clear input buffer
            self.serial_connection.reset_input_buffer()
            
            # Send command
            self.serial_connection.write(f"{command}\r\n".encode())
            
            # Read response
            response = ""
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    response += data.decode('utf-8', errors='ignore')
                    
                    # Check for end of response
                    if 'OK' in response or 'ERROR' in response:
                        break
                
                await asyncio.sleep(0.1)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"AT command failed: {e}")
            return ""
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS using AT commands."""
        if not self.is_connected:
            return False
        
        try:
            # Set SMS text mode
            await self._send_at_command('AT+CMGF=1')
            
            # Set recipient number
            await self._send_at_command(f'AT+CMGS="{phone_number}"')
            
            # Send message content
            self.serial_connection.write(f"{message}\x1A".encode())
            await asyncio.sleep(2)
            
            # Check response
            response = ""
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < 10:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    response += data.decode('utf-8', errors='ignore')
                    
                    if 'OK' in response:
                        logger.info(f"SMS sent to {phone_number}")
                        return True
                    elif 'ERROR' in response:
                        logger.error(f"SMS send failed: {response}")
                        return False
                
                await asyncio.sleep(0.1)
            
            logger.error("SMS send timeout")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect serial connection."""
        if self.serial_connection and self.is_connected:
            try:
                self.serial_connection.close()
                self.is_connected = False
                logger.info("Serial GSM connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
