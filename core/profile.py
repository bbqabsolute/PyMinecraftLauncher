"""
Profile management for PyMinecraftLauncher
"""

import json
from pathlib import Path
from utils.logger import get_logger
from utils.config import Config

logger = get_logger("profile")


class Profile:
    """Minecraft game profile"""
    
    def __init__(self, name, version, java_path=None, ram=2048, modloader=None):
        self.name = name
        self.version = version
        self.java_path = java_path
        self.ram = ram
        self.modloader = modloader or "vanilla"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "java_path": self.java_path,
            "ram": self.ram,
            "modloader": self.modloader
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            name=data.get("name"),
            version=data.get("version"),
            java_path=data.get("java_path"),
            ram=data.get("ram", 2048),
            modloader=data.get("modloader", "vanilla")
        )


class ProfileManager:
    """Manage game profiles"""
    
    PROFILES_FILE = Path.home() / ".minecraft" / "launcher_profiles.json"
    
    def __init__(self):
        self.profiles = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load profiles from file"""
        if self.PROFILES_FILE.exists():
            try:
                with open(self.PROFILES_FILE, 'r') as f:
                    data = json.load(f)
                
                for profile_name, profile_data in data.items():
                    self.profiles[profile_name] = Profile.from_dict(profile_data)
                
                logger.info(f"Loaded {len(self.profiles)} profiles")
            except json.JSONDecodeError:
                logger.warning("Corrupted profiles file")
        else:
            logger.info("No profiles file found")
    
    def _save_profiles(self):
        """Save profiles to file"""
        try:
            self.PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            profiles_data = {
                name: profile.to_dict()
                for name, profile in self.profiles.items()
            }
            
            with open(self.PROFILES_FILE, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            logger.info("Profiles saved")
            return True
        except IOError as e:
            logger.error(f"Failed to save profiles: {e}")
            return False
    
    def create_profile(self, name, version, java_path=None, ram=2048, modloader="vanilla"):
        """Create a new profile"""
        if name in self.profiles:
            logger.warning(f"Profile already exists: {name}")
            return False
        
        profile = Profile(name, version, java_path, ram, modloader)
        self.profiles[name] = profile
        
        logger.info(f"Created profile: {name}")
        return self._save_profiles()
    
    def delete_profile(self, name):
        """Delete a profile"""
        if name not in self.profiles:
            logger.warning(f"Profile not found: {name}")
            return False
        
        del self.profiles[name]
        logger.info(f"Deleted profile: {name}")
        return self._save_profiles()
    
    def update_profile(self, name, **kwargs):
        """Update profile settings"""
        if name not in self.profiles:
            logger.warning(f"Profile not found: {name}")
            return False
        
        profile = self.profiles[name]
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        logger.info(f"Updated profile: {name}")
        return self._save_profiles()
    
    def get_profile(self, name):
        """Get profile by name"""
        return self.profiles.get(name)
    
    def get_all_profiles(self):
        """Get all profiles"""
        return list(self.profiles.values())
    
    def get_profile_names(self):
        """Get all profile names"""
        return list(self.profiles.keys())
