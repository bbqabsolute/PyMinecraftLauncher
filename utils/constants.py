"""
Constants and configuration for PyMinecraftLauncher
"""

# API Endpoints
MOJANG_MANIFEST_URL = "https://launcher.mojang.com/v1/objects/6ac3ce12f36bfad5850fba40ee1a319296b4411c/version_manifest.json"
MOJANG_API_URL = "https://api.mojang.com"

# Forge API
FORGE_MAVEN_URL = "https://maven.minecraftforge.net"
FORGE_META_URL = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/json"

# Fabric API
FABRIC_META_URL = "https://meta.fabricmc.net/v2"
FABRIC_INSTALLER_URL = "https://maven.fabricmc.net/net/fabricmc/fabric-installer"

# Game directories
DEFAULT_GAME_DIR = "~/.minecraft"
VERSIONS_DIR = "{game_dir}/versions"
LIBRARIES_DIR = "{game_dir}/libraries"
MODS_DIR = "{game_dir}/mods"
ASSETS_DIR = "{game_dir}/assets"
PROFILES_DIR = "{game_dir}/launcher_profiles.json"

# Java configuration
JAVA_MIN_VERSION = 8
JAVA_SEARCH_PATHS = {
    "windows": [
        "C:\\Program Files\\Java",
        "C:\\Program Files (x86)\\Java",
        "C:\\Java",
    ],
    "linux": [
        "/usr/lib/jvm",
        "/usr/lib64/jvm",
        "/opt/java",
        "/opt/jdk",
    ],
    "darwin": [
        "/Library/Java/JavaVirtualMachines",
        "/System/Library/Java/JavaVirtualMachines",
    ]
}

# Game launch settings
DEFAULT_RAM = 2048  # MB
MIN_RAM = 512  # MB
MAX_RAM = 8192  # MB

# UI Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Application metadata
APP_NAME = "PyMinecraftLauncher"
APP_VERSION = "1.0.0"
APP_AUTHOR = "bbqabsolute"
APP_GITHUB = "https://github.com/bbqabsolute/PyMinecraftLauncher"

# Timeouts
DOWNLOAD_TIMEOUT = 30  # seconds
API_TIMEOUT = 10  # seconds
