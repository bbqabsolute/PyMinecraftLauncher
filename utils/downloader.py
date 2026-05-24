"""
Download manager for PyMinecraftLauncher
"""

import requests
import os
from pathlib import Path
from utils.logger import get_logger
from utils.constants import DOWNLOAD_TIMEOUT, API_TIMEOUT

logger = get_logger("downloader")


class DownloadManager:
    """Manage downloads with progress tracking"""
    
    @staticmethod
    def download_file(url, destination, callback=None):
        """
        Download a file from URL to destination
        
        Args:
            url: File URL
            destination: Save path
            callback: Progress callback function (bytes_downloaded, total_bytes)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            destination = Path(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading: {url}")
            
            response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if callback and total_size > 0:
                            callback(downloaded, total_size)
            
            logger.info(f"Download complete: {destination}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
        except IOError as e:
            logger.error(f"File write error: {e}")
            return False
    
    @staticmethod
    def fetch_json(url):
        """Fetch JSON from URL"""
        try:
            logger.debug(f"Fetching JSON: {url}")
            response = requests.get(url, timeout=API_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JSON: {e}")
            return None


class VersionManifest:
    """Manage Minecraft version manifest"""
    
    def __init__(self):
        self.manifest = None
        self.versions = {}
    
    def fetch_manifest(self):
        """Fetch version manifest from Mojang"""
        from utils.constants import MOJANG_MANIFEST_URL
        
        manifest_data = DownloadManager.fetch_json(MOJANG_MANIFEST_URL)
        
        if manifest_data:
            self.manifest = manifest_data
            self._parse_versions()
            logger.info(f"Fetched manifest with {len(self.versions)} versions")
            return True
        
        return False
    
    def _parse_versions(self):
        """Parse versions from manifest"""
        if not self.manifest:
            return
        
        self.versions = {}
        for version in self.manifest.get("versions", []):
            version_id = version.get("id")
            version_type = version.get("type")
            
            if version_id:
                self.versions[version_id] = {
                    "id": version_id,
                    "type": version_type,
                    "url": version.get("url"),
                    "release_time": version.get("releaseTime"),
                    "time": version.get("time")
                }
    
    def get_versions_by_type(self, version_type):
        """Get versions by type (snapshot, release, etc)"""
        return [
            v for v in self.versions.values()
            if v["type"] == version_type
        ]
    
    def get_latest_release(self):
        """Get latest release version"""
        if self.manifest:
            return self.manifest.get("latest", {}).get("release")
        return None
    
    def get_latest_snapshot(self):
        """Get latest snapshot version"""
        if self.manifest:
            return self.manifest.get("latest", {}).get("snapshot")
        return None


class ForgeMeta:
    """Fetch Forge version metadata"""
    
    @staticmethod
    def get_forge_versions(mc_version):
        """Get available Forge versions for Minecraft version"""
        from utils.constants import FORGE_META_URL
        
        try:
            url = f"{FORGE_META_URL}"
            manifest = DownloadManager.fetch_json(url)
            
            if manifest and mc_version in manifest:
                return manifest[mc_version]
            
            return []
        except Exception as e:
            logger.error(f"Failed to fetch Forge versions: {e}")
            return []


class FabricMeta:
    """Fetch Fabric version metadata"""
    
    @staticmethod
    def get_fabric_versions():
        """Get available Fabric Loader versions"""
        from utils.constants import FABRIC_META_URL
        
        try:
            url = f"{FABRIC_META_URL}/versions/loader"
            versions = DownloadManager.fetch_json(url)
            return versions if versions else []
        except Exception as e:
            logger.error(f"Failed to fetch Fabric versions: {e}")
            return []
    
    @staticmethod
    def get_fabric_games():
        """Get available Fabric game versions"""
        from utils.constants import FABRIC_META_URL
        
        try:
            url = f"{FABRIC_META_URL}/versions/game"
            versions = DownloadManager.fetch_json(url)
            return versions if versions else []
        except Exception as e:
            logger.error(f"Failed to fetch Fabric game versions: {e}")
            return []
