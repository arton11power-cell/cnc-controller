"""Configuration module"""

import json
import os
from typing import Dict, Any


class Config:
    """Application configuration"""

    DEFAULT_CONFIG = {
        'serial_port': 'COM1',
        'baudrate': 115200,
        'feed_rate': 100,
        'spindle_speed': 0,
        'window_width': 1200,
        'window_height': 800,
    }

    def __init__(self, config_file: str = 'config.json'):
        """Initialize configuration"""
        self.config_file = config_file
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
