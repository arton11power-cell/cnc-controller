"""Serial communication handler"""

import serial
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SerialHandler:
    """Handle serial communication with CNC controller"""

    def __init__(self, port: str = None, baudrate: int = 115200):
        """Initialize serial handler"""
        self.port = port
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """Connect to serial port"""
        try:
            self.connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1
            )
            logger.info(f"Connected to {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from serial port"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected")

    def send_command(self, command: str) -> bool:
        """Send command to CNC controller"""
        if not self.connection or not self.connection.is_open:
            logger.warning("Not connected")
            return False

        try:
            self.connection.write((command + '\n').encode())
            logger.debug(f"Sent: {command}")
            return True
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def read_response(self) -> Optional[str]:
        """Read response from CNC controller"""
        if not self.connection or not self.connection.is_open:
            return None

        try:
            if self.connection.in_waiting:
                response = self.connection.readline().decode().strip()
                logger.debug(f"Received: {response}")
                return response
        except Exception as e:
            logger.error(f"Failed to read response: {e}")

        return None
