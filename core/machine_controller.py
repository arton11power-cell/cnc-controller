"""Machine controller - handles communication with STM32"""

import serial
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MachineController:
    """Main controller for CNC machine communication"""

    def __init__(self):
        """Initialize machine controller"""
        self.connection: Optional[serial.Serial] = None
        self.is_connected_flag = False
        self.current_position = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'A': 0.0, 'B': 0.0}
        self.machine_state = {
            'running': False,
            'paused': False,
            'error': False
        }
        self.gcode_program: List[str] = []
        self.current_line = 0

    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to STM32 via serial port"""
        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected_flag = True
            logger.info(f"Connected to {port} at {baudrate} baud")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from STM32"""
        if self.connection:
            self.connection.close()
            self.is_connected_flag = False
            logger.info("Disconnected")

    def is_connected(self) -> bool:
        """Check if connected"""
        return self.is_connected_flag and self.connection and self.connection.is_open

    def send_command(self, command: str) -> bool:
        """Send command to STM32"""
        if not self.is_connected():
            logger.warning("Not connected")
            return False

        try:
            self.connection.write((command + '\n').encode())
            logger.debug(f"Sent: {command}")
            return True
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def move_axis(self, axis: str, distance: float, speed: float) -> bool:
        """Move specific axis"""
        command = f"MOVE {axis} {distance} {speed}"
        return self.send_command(command)

    def home_all(self) -> bool:
        """Move all axes to home position"""
        return self.send_command("HOME")

    def emergency_stop(self) -> bool:
        """Emergency stop"""
        return self.send_command("E-STOP")

    def enable_motors(self) -> bool:
        """Enable all motors"""
        return self.send_command("ENABLE")

    def disable_motors(self) -> bool:
        """Disable all motors"""
        return self.send_command("DISABLE")

    def spindle_on(self, speed: int) -> bool:
        """Turn on spindle"""
        command = f"SPINDLE ON {speed}"
        return self.send_command(command)

    def spindle_off(self) -> bool:
        """Turn off spindle"""
        return self.send_command("SPINDLE OFF")

    def load_gcode_program(self, lines: List[str]) -> bool:
        """Load G-code program"""
        self.gcode_program = [line.strip() for line in lines if line.strip()]
        self.current_line = 0
        logger.info(f"Loaded {len(self.gcode_program)} lines")
        return True

    def start_program(self) -> bool:
        """Start G-code program execution"""
        if not self.gcode_program:
            logger.warning("No program loaded")
            return False
        
        self.machine_state['running'] = True
        self.machine_state['paused'] = False
        return self.send_command("START")

    def pause_program(self) -> bool:
        """Pause program execution"""
        self.machine_state['paused'] = True
        return self.send_command("PAUSE")

    def stop_program(self) -> bool:
        """Stop program execution"""
        self.machine_state['running'] = False
        self.machine_state['paused'] = False
        return self.send_command("STOP")

    def get_status(self) -> Optional[Dict]:
        """Get machine status"""
        if not self.is_connected():
            return None

        try:
            if self.connection.in_waiting:
                response = self.connection.readline().decode().strip()
                logger.debug(f"Received: {response}")
                # Parse response and update status
        except Exception as e:
            logger.error(f"Failed to get status: {e}")

        return {
            'pos_x': self.current_position['X'],
            'pos_y': self.current_position['Y'],
            'pos_z': self.current_position['Z'],
            'pos_a': self.current_position['A'],
            'pos_b': self.current_position['B'],
            'running': self.machine_state['running']
        }
