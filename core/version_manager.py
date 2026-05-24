"""
Version management for Minecraft versions
"""

import json
from pathlib import Path
from utils.logger import get_logger
from utils.downloader import DownloadManager
from utils.config import Config

logger = get_logger("version_manager")


class VersionManager:
    """Manage Minecraft versions"""
    
    def __init__(self):
        game_dir = Path(Config.get("game_directory", str(Path.home() / ".minecraft")))
        self.versions_dir = game_dir / "versions"
        self.versions = {}
        self._scan_versions()
    
    def _scan_versions(self):
        """Scan for installed versions"""
        self.versions = {}
        
        if not self.versions_dir.exists():
            return
        
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                json_file = version_dir / f"{version_dir.name}.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r') as f:
                            version_data = json.load(f)
                        
                        self.versions[version_dir.name] = {
                            "id": version_dir.name,
                            "path": version_dir,
                            "json_path": json_file,
                            "jar_path": version_dir / f"{version_dir.name}.jar",
                            "data": version_data
                        }
                        logger.debug(f"Found version: {version_dir.name}")
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON for version: {version_dir.name}")
    
    def get_installed_versions(self):
        """Get list of installed versions"""
        return list(self.versions.keys())
    
    def is_installed(self, version_id):
        """Check if version is installed"""
        return version_id in self.versions
    
    def get_version_info(self, version_id):
        """Get information about a version"""
        return self.versions.get(version_id)
    
    def download_version(self, version_id, version_url, progress_callback=None):
        """Download and install a version"""
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Download version JSON
        json_file = version_dir / f"{version_id}.json"
        
        if not DownloadManager.download_file(version_url, json_file):
            logger.error(f"Failed to download version JSON: {version_id}")
            return False
        
        # Parse JSON and download client JAR
        try:
            with open(json_file, 'r') as f:
                version_data = json.load(f)
            
            # Download client JAR
            downloads = version_data.get("downloads", {})
            client_data = downloads.get("client", {})
            client_url = client_data.get("url")
            
            if client_url:
                jar_file = version_dir / f"{version_id}.jar"
                if not DownloadManager.download_file(client_url, jar_file, progress_callback):
                    logger.error(f"Failed to download client JAR: {version_id}")
                    return False
            
            # Rescan versions
            self._scan_versions()
            logger.info(f"Successfully downloaded version: {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading version: {e}")
            return False


class ModloaderVersion:
    """Base class for modloader versions"""
    
    def __init__(self, version_id, modloader_type, mc_version):
        self.version_id = version_id
        self.modloader_type = modloader_type
        self.mc_version = mc_version
        self.installed = False


class ForgeVersion(ModloaderVersion):
    """Forge modloader version"""
    
    def __init__(self, version_id, mc_version, forge_version):
        super().__init__(version_id, "forge", mc_version)
        self.forge_version = forge_version
        self.installer_url = None
        self.universal_url = None


class FabricVersion(ModloaderVersion):
    """Fabric modloader version"""
    
    def __init__(self, version_id, mc_version, loader_version, installer_version=None):
        super().__init__(version_id, "fabric", mc_version)
        self.loader_version = loader_version
        self.installer_version = installer_version or "latest"


class ModloaderManager:
    """Manage modloader installations"""
    
    def __init__(self):
        game_dir = Path(Config.get("game_directory", str(Path.home() / ".minecraft")))
        self.modloaders_dir = game_dir / "modloaders"
        self.modloaders_dir.mkdir(parents=True, exist_ok=True)
        self.installed_modloaders = {}
        self._scan_modloaders()
    
    def _scan_modloaders(self):
        """Scan for installed modloaders"""
        self.installed_modloaders = {}
        
        if not self.modloaders_dir.exists():
            return
        
        for modloader_dir in self.modloaders_dir.iterdir():
            if modloader_dir.is_dir():
                try:
                    config_file = modloader_dir / "modloader.json"
                    if config_file.exists():
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        modloader_id = f"{config['type']}-{config['mc_version']}-{config['version']}"
                        self.installed_modloaders[modloader_id] = {
                            "type": config["type"],
                            "mc_version": config["mc_version"],
                            "version": config["version"],
                            "path": modloader_dir
                        }
                        logger.debug(f"Found modloader: {modloader_id}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid modloader config: {modloader_dir}")
    
    def get_installed_modloaders(self):
        """Get list of installed modloaders"""
        return list(self.installed_modloaders.keys())
    
    def install_forge(self, mc_version, forge_version, progress_callback=None):
        """Install Forge modloader"""
        modloader_id = f"forge-{mc_version}-{forge_version}"
        modloader_dir = self.modloaders_dir / modloader_id
        modloader_dir.mkdir(parents=True, exist_ok=True)
        
        # Save modloader config
        config = {
            "type": "forge",
            "mc_version": mc_version,
            "version": forge_version
        }
        
        config_file = modloader_dir / "modloader.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        logger.info(f"Installed Forge: {modloader_id}")
        self._scan_modloaders()
        return True
    
    def install_fabric(self, mc_version, loader_version, progress_callback=None):
        """Install Fabric modloader"""
        modloader_id = f"fabric-{mc_version}-{loader_version}"
        modloader_dir = self.modloaders_dir / modloader_id
        modloader_dir.mkdir(parents=True, exist_ok=True)
        
        # Save modloader config
        config = {
            "type": "fabric",
            "mc_version": mc_version,
            "version": loader_version
        }
        
        config_file = modloader_dir / "modloader.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        logger.info(f"Installed Fabric: {modloader_id}")
        self._scan_modloaders()
        return True
