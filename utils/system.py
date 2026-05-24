"""
System utilities for Java detection and system information
"""

import subprocess
import platform
import os
from pathlib import Path
from utils.logger import get_logger
from utils.constants import JAVA_SEARCH_PATHS, JAVA_MIN_VERSION

logger = get_logger("system")


class JavaDetector:
    """Detect Java installations on the system"""
    
    @staticmethod
    def find_java_installations():
        """Find all Java installations on the system"""
        java_paths = []
        system = platform.system().lower()
        
        # Get search paths for current system
        if system == "windows":
            search_paths = JAVA_SEARCH_PATHS["windows"]
        elif system == "darwin":
            search_paths = JAVA_SEARCH_PATHS["darwin"]
        else:
            search_paths = JAVA_SEARCH_PATHS["linux"]
        
        # Search common directories
        for search_path in search_paths:
            if Path(search_path).exists():
                java_paths.extend(JavaDetector._search_directory(search_path))
        
        # Also try PATH environment variable
        java_paths.extend(JavaDetector._search_path_env())
        
        # Remove duplicates and verify
        verified_paths = []
        for path in set(java_paths):
            if JavaDetector._verify_java(path):
                verified_paths.append(path)
        
        return verified_paths
    
    @staticmethod
    def _search_directory(directory):
        """Search directory for Java installations"""
        java_paths = []
        try:
            for item in Path(directory).iterdir():
                try:
                    java_path = JavaDetector._find_java_executable(item)
                    if java_path:
                        java_paths.append(str(java_path))
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass
        return java_paths
    
    @staticmethod
    def _find_java_executable(java_home):
        """Find java executable in a java home directory"""
        system = platform.system().lower()
        
        if system == "windows":
            java_exe = Path(java_home) / "bin" / "java.exe"
        else:
            java_exe = Path(java_home) / "bin" / "java"
        
        if java_exe.exists() and java_exe.is_file():
            return java_exe
        
        return None
    
    @staticmethod
    def _search_path_env():
        """Search PATH environment variable for Java"""
        java_paths = []
        path_env = os.environ.get("PATH", "")
        
        for path_dir in path_env.split(os.pathsep):
            if platform.system().lower() == "windows":
                java_exe = Path(path_dir) / "java.exe"
            else:
                java_exe = Path(path_dir) / "java"
            
            if java_exe.exists():
                # Get the actual java home
                try:
                    java_home = subprocess.check_output(
                        [str(java_exe), "-XshowSettings:properties", "-version"],
                        stderr=subprocess.STDOUT,
                        text=True
                    ).split("java.home = ")[1].split("\n")[0].strip()
                    java_paths.append(java_home)
                except (subprocess.CalledProcessError, IndexError, AttributeError):
                    java_paths.append(str(Path(path_dir).parent))
        
        return java_paths
    
    @staticmethod
    def _verify_java(java_path):
        """Verify that Java installation is valid and meets minimum version"""
        system = platform.system().lower()
        
        if system == "windows":
            java_exe = Path(java_path) / "bin" / "java.exe"
        else:
            java_exe = Path(java_path) / "bin" / "java"
        
        if not java_exe.exists():
            return False
        
        try:
            version_output = subprocess.check_output(
                [str(java_exe), "-version"],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Parse version
            if "java version" in version_output or "openjdk version" in version_output:
                logger.debug(f"Found Java installation: {java_path}")
                return True
        except (subprocess.CalledProcessError, OSError):
            pass
        
        return False
    
    @staticmethod
    def get_java_version(java_path):
        """Get Java version from path"""
        system = platform.system().lower()
        
        if system == "windows":
            java_exe = Path(java_path) / "bin" / "java.exe"
        else:
            java_exe = Path(java_path) / "bin" / "java"
        
        if not java_exe.exists():
            return None
        
        try:
            version_output = subprocess.check_output(
                [str(java_exe), "-version"],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Extract version number
            if "java version" in version_output:
                version_str = version_output.split("java version")[1].split("\"")[1]
            elif "openjdk version" in version_output:
                version_str = version_output.split("openjdk version")[1].split("\"")[1]
            else:
                return None
            
            # Parse major version
            major_version = int(version_str.split(".")[0])
            if major_version == 1:  # Java 1.8, etc
                major_version = int(version_str.split(".")[1])
            
            return major_version
        except (subprocess.CalledProcessError, OSError, ValueError, IndexError):
            return None


def get_system_info():
    """Get system information"""
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
    }


def get_available_memory():
    """Get available system memory in MB"""
    try:
        import psutil
        return int(psutil.virtual_memory().available / (1024 * 1024))
    except ImportError:
        return None
