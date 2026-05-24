"""
Game launcher for PyMinecraftLauncher
"""

import subprocess
import platform
import json
from pathlib import Path
from utils.logger import get_logger
from utils.config import Config
from utils.system import JavaDetector
from core.version_manager import VersionManager
from core.profile import ProfileManager

logger = get_logger("launcher")


class GameLauncher:
    """Launch Minecraft game with specified settings"""
    
    def __init__(self):
        self.version_manager = VersionManager()
        self.profile_manager = ProfileManager()
        self.game_dir = Path(Config.get("game_directory", str(Path.home() / ".minecraft")))
    
    def launch(self, profile_name, progress_callback=None):
        """
        Launch game with specified profile
        
        Args:
            profile_name: Name of profile to launch
            progress_callback: Function to call with progress updates
        
        Returns:
            Popen object or None if launch failed
        """
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            logger.error(f"Profile not found: {profile_name}")
            return None
        
        # Check if version is installed
        if not self.version_manager.is_installed(profile.version):
            logger.error(f"Version not installed: {profile.version}")
            return None
        
        # Get version info
        version_info = self.version_manager.get_version_info(profile.version)
        if not version_info:
            logger.error(f"Version info not found: {profile.version}")
            return None
        
        # Verify Java
        java_path = profile.java_path
        if not java_path:
            java_installations = JavaDetector.find_java_installations()
            if not java_installations:
                logger.error("No Java installation found")
                return None
            java_path = java_installations[0]
        
        # Build JVM arguments
        jvm_args = self._build_jvm_args(java_path, profile.ram, version_info)
        
        if not jvm_args:
            logger.error("Failed to build JVM arguments")
            return None
        
        # Get game arguments
        game_args = self._build_game_args(profile, version_info)
        
        # Combine arguments
        cmd = [str(java_path)]
        cmd.extend(jvm_args)
        cmd.append("-cp")
        cmd.append(self._build_classpath(version_info))
        cmd.append(version_info["data"].get("mainClass", "net.minecraft.client.main.Main"))
        cmd.extend(game_args)
        
        logger.info(f"Launching game with command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.game_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("Game launched successfully")
            return process
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return None
    
    def _build_jvm_args(self, java_path, ram, version_info):
        """Build JVM arguments"""
        args = []
        
        # Memory arguments
        args.append(f"-Xmx{ram}M")
        args.append(f"-Xms{int(ram/2)}M")
        
        # System properties
        args.append("-Duser.language=en")
        args.append("-Dfile.encoding=UTF-8")
        
        # Platform-specific arguments
        system = platform.system().lower()
        if system == "darwin":
            args.append("-XstartOnFirstThread")
        
        # Version-specific arguments
        jvm_args = version_info["data"].get("arguments", {}).get("jvm", [])
        for arg in jvm_args:
            if isinstance(arg, str):
                args.append(arg)
        
        return args
    
    def _build_game_args(self, profile, version_info):
        """Build game arguments"""
        args = []
        
        # Username
        args.extend(["--username", profile.name])
        
        # UUID (use random UUID for offline mode)
        import uuid
        args.extend(["--uuid", str(uuid.uuid4())])
        
        # Session ID (offline mode)
        args.extend(["--sessionId", "0"])
        
        # Access token
        args.extend(["--accessToken", "0"])
        
        # Version
        args.extend(["--version", profile.version])
        
        # Game directory
        args.extend(["--gameDir", str(self.game_dir)])
        
        # Assets directory
        assets_dir = self.game_dir / "assets"
        args.extend(["--assetsDir", str(assets_dir)])
        
        # Asset index
        version_data = version_info["data"]
        asset_index = version_data.get("assetIndex", {}).get("id")
        if asset_index:
            args.extend(["--assetIndex", asset_index])
        
        # JVM arguments
        game_jvm_args = version_data.get("arguments", {}).get("game", [])
        for arg in game_jvm_args:
            if isinstance(arg, str):
                args.append(arg)
        
        return args
    
    def _build_classpath(self, version_info):
        """Build Java classpath"""
        classpath_parts = []
        
        # Add version JAR
        version_jar = version_info["jar_path"]
        classpath_parts.append(str(version_jar))
        
        # Add libraries
        libraries = version_info["data"].get("libraries", [])
        libraries_dir = self.game_dir / "libraries"
        
        for lib in libraries:
            if isinstance(lib, dict):
                lib_path = lib.get("downloads", {}).get("artifact", {}).get("path")
                if lib_path:
                    classpath_parts.append(str(libraries_dir / lib_path))
        
        # Platform-specific separator
        separator = ";" if platform.system().lower() == "windows" else ":"
        return separator.join(classpath_parts)
