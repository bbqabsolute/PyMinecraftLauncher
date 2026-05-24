"""
Configuration management for PyMinecraftLauncher
"""

import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("config")


class Config:
    """Manage launcher configuration"""
    
    CONFIG_DIR = Path.home() / ".minecraft"
    CONFIG_FILE = CONFIG_DIR / "launcher_config.json"
    
    DEFAULT_CONFIG = {
        "player_name": "Steve",
        "java_path": None,
        "ram_allocation": 2048,
        "game_directory": str(CONFIG_DIR),
        "last_version": "1.20.1",
        "last_profile": None,
        "theme": "dark",
        "profiles": {},
    }
    
    @classmethod
    def load(cls):
        """Load configuration from file"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                logger.info("Configuration loaded")
                return config
            except json.JSONDecodeError:
                logger.warning("Config file corrupted, using defaults")
                return cls.DEFAULT_CONFIG.copy()
        else:
            logger.info("Creating default configuration")
            cls.save(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        """Save configuration to file"""
        try:
            cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration saved")
            return True
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    @classmethod
    def get(cls, key, default=None):
        """Get configuration value"""
        config = cls.load()
        return config.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """Set configuration value"""
        config = cls.load()
        config[key] = value
        return cls.save(config)
