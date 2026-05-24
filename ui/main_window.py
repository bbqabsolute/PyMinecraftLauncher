"""
Main window for PyMinecraftLauncher
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QProgressBar,
                             QStatusBar, QMenuBar, QMenu, QListWidget, 
                             QListWidgetItem, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont
from utils.logger import get_logger
from utils.config import Config
from utils.downloader import VersionManifest, DownloadManager
from utils.system import JavaDetector
from core.version_manager import VersionManager
from core.profile import ProfileManager
from core.launcher import GameLauncher
from ui.dialogs.profile_dialog import ProfileDialog
from ui.dialogs.settings_dialog import SettingsDialog

logger = get_logger("main_window")


class DownloadThread(QThread):
    """Thread for downloading versions"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(bool)
    
    def __init__(self, version_id, version_url):
        super().__init__()
        self.version_id = version_id
        self.version_url = version_url
        self.version_manager = VersionManager()
    
    def run(self):
        """Run download"""
        try:
            success = self.version_manager.download_version(
                self.version_id,
                self.version_url,
                progress_callback=lambda d, t: self.progress.emit(d, t)
            )
            self.finished.emit(success)
        except Exception as e:
            logger.error(f"Download thread error: {e}")
            self.finished.emit(False)


class LaunchThread(QThread):
    """Thread for launching game"""
    finished = pyqtSignal(bool)
    
    def __init__(self, profile_name):
        super().__init__()
        self.profile_name = profile_name
        self.launcher = GameLauncher()
    
    def run(self):
        """Run launcher"""
        try:
            process = self.launcher.launch(self.profile_name)
            if process:
                process.wait()
                self.finished.emit(True)
            else:
                self.finished.emit(False)
        except Exception as e:
            logger.error(f"Launch thread error: {e}")
            self.finished.emit(False)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMinecraftLauncher")
        self.setGeometry(100, 100, 1000, 700)
        
        self.config = Config.load()
        self.version_manager = VersionManager()
        self.profile_manager = ProfileManager()
        self.version_manifest = VersionManifest()
        self.launcher = GameLauncher()
        
        self.download_thread = None
        self.launch_thread = None
        
        self._init_ui()
        self._load_stylesheet()
        self._fetch_versions()
        
        logger.info("Application started")
    
    def _init_ui(self):
        """Initialize UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        title_label = QLabel("PyMinecraftLauncher")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Version and profile selection
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)
        
        version_label = QLabel("Version:")
        self.version_combo = QComboBox()
        self.version_combo.addItem("Loading versions...")
        self.version_combo.currentTextChanged.connect(self._on_version_changed)
        selection_layout.addWidget(version_label)
        selection_layout.addWidget(self.version_combo)
        
        profile_label = QLabel("Profile:")
        self.profile_combo = QComboBox()
        self._update_profiles()
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        selection_layout.addWidget(profile_label)
        selection_layout.addWidget(self.profile_combo)
        
        main_layout.addLayout(selection_layout)
        
        # Profile management buttons
        profile_button_layout = QHBoxLayout()
        profile_button_layout.setSpacing(10)
        
        new_profile_button = QPushButton("New Profile")
        new_profile_button.setObjectName("primaryButton")
        new_profile_button.clicked.connect(self._create_profile)
        profile_button_layout.addWidget(new_profile_button)
        
        edit_profile_button = QPushButton("Edit Profile")
        edit_profile_button.clicked.connect(self._edit_profile)
        profile_button_layout.addWidget(edit_profile_button)
        
        delete_profile_button = QPushButton("Delete Profile")
        delete_profile_button.setObjectName("dangerButton")
        delete_profile_button.clicked.connect(self._delete_profile)
        profile_button_layout.addWidget(delete_profile_button)
        
        profile_button_layout.addStretch()
        main_layout.addLayout(profile_button_layout)
        
        # Installed versions list
        versions_label = QLabel("Installed Versions:")
        main_layout.addWidget(versions_label)
        
        self.versions_list = QListWidget()
        self._update_versions_list()
        main_layout.addWidget(self.versions_list)
        
        # Download section
        download_layout = QHBoxLayout()
        download_layout.setSpacing(10)
        
        download_button = QPushButton("Download Version")
        download_button.clicked.connect(self._download_version)
        download_layout.addWidget(download_button)
        
        download_layout.addStretch()
        main_layout.addLayout(download_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Launch button
        launch_layout = QHBoxLayout()
        launch_layout.setSpacing(10)
        launch_layout.addStretch()
        
        self.launch_button = QPushButton("Launch Game")
        self.launch_button.setObjectName("primaryButton")
        self.launch_button.setMinimumHeight(40)
        self.launch_button.clicked.connect(self._launch_game)
        launch_layout.addWidget(self.launch_button)
        
        main_layout.addLayout(launch_layout)
        
        central_widget.setLayout(main_layout)
        
        # Menu bar
        self._create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self._open_settings)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)
    
    def _load_stylesheet(self):
        """Load dark theme stylesheet"""
        try:
            stylesheet_path = Path(__file__).parent / "styles" / "dark_theme.qss"
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            logger.warning("Stylesheet not found, using default theme")
    
    def _fetch_versions(self):
        """Fetch versions from Mojang API"""
        logger.info("Fetching Minecraft versions...")
        
        def fetch_in_thread():
            success = self.version_manifest.fetch_manifest()
            if success:
                self._update_version_combo()
            else:
                logger.warning("Failed to fetch versions")
        
        # Run in thread
        import threading
        thread = threading.Thread(target=fetch_in_thread)
        thread.daemon = True
        thread.start()
    
    def _update_version_combo(self):
        """Update version combo with fetched versions"""
        self.version_combo.clear()
        
        # Add latest release
        latest_release = self.version_manifest.get_latest_release()
        if latest_release:
            self.version_combo.addItem(f"{latest_release} (Latest Release)")
        
        # Add latest snapshot
        latest_snapshot = self.version_manifest.get_latest_snapshot()
        if latest_snapshot:
            self.version_combo.addItem(f"{latest_snapshot} (Latest Snapshot)")
        
        # Add releases
        releases = self.version_manifest.get_versions_by_type("release")
        for version in releases[:10]:  # Show top 10 recent releases
            self.version_combo.addItem(version["id"])
        
        self.statusBar().showMessage("Versions loaded successfully")
    
    def _update_profiles(self):
        """Update profile combo"""
        self.profile_combo.clear()
        profiles = self.profile_manager.get_profile_names()
        
        if profiles:
            self.profile_combo.addItems(profiles)
        else:
            self.profile_combo.addItem("No profiles")
    
    def _update_versions_list(self):
        """Update installed versions list"""
        self.versions_list.clear()
        installed = self.version_manager.get_installed_versions()
        
        for version in sorted(installed, reverse=True):
            item = QListWidgetItem(version)
            self.versions_list.addItem(item)
    
    def _on_version_changed(self, version):
        """Handle version selection change"""
        logger.debug(f"Selected version: {version}")
    
    def _on_profile_changed(self, profile):
        """Handle profile selection change"""
        logger.debug(f"Selected profile: {profile}")
    
    def _create_profile(self):
        """Create new profile"""
        versions = self.version_manifest.get_installed_versions() if self.version_manifest.manifest else []
        dialog = ProfileDialog(self, versions=versions)
        
        if dialog.exec() == ProfileDialog.Accepted:
            result = dialog.get_result()
            if result:
                self.profile_manager.create_profile(**result)
                self._update_profiles()
                self.statusBar().showMessage(f"Profile '{result['name']}' created")
    
    def _edit_profile(self):
        """Edit selected profile"""
        current_profile_name = self.profile_combo.currentText()
        if current_profile_name == "No profiles":
            QMessageBox.warning(self, "Warning", "No profile selected")
            return
        
        profile = self.profile_manager.get_profile(current_profile_name)
        versions = list(self.version_manifest.versions.keys()) if self.version_manifest.manifest else []
        
        dialog = ProfileDialog(self, profile=profile, versions=versions)
        
        if dialog.exec() == ProfileDialog.Accepted:
            result = dialog.get_result()
            if result:
                self.profile_manager.update_profile(current_profile_name, **result)
                self.statusBar().showMessage(f"Profile '{current_profile_name}' updated")
    
    def _delete_profile(self):
        """Delete selected profile"""
        current_profile_name = self.profile_combo.currentText()
        if current_profile_name == "No profiles":
            QMessageBox.warning(self, "Warning", "No profile selected")
            return
        
        reply = QMessageBox.question(self, "Confirm", 
                                     f"Delete profile '{current_profile_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profile_manager.delete_profile(current_profile_name)
            self._update_profiles()
            self.statusBar().showMessage(f"Profile '{current_profile_name}' deleted")
    
    def _download_version(self):
        """Download version"""
        if not self.version_manifest.manifest:
            QMessageBox.warning(self, "Warning", "Versions not loaded yet")
            return
        
        current_version = self.version_combo.currentText()
        if not current_version:
            QMessageBox.warning(self, "Warning", "Select a version first")
            return
        
        # Extract version ID from text
        version_id = current_version.split(" ")[0]
        
        if self.version_manager.is_installed(version_id):
            QMessageBox.information(self, "Info", f"Version {version_id} already installed")
            return
        
        version_info = self.version_manifest.versions.get(version_id)
        if not version_info:
            QMessageBox.warning(self, "Warning", "Version not found in manifest")
            return
        
        # Start download
        self.download_thread = DownloadThread(version_id, version_info["url"])
        self.download_thread.progress.connect(self._update_download_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.start()
        
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage(f"Downloading {version_id}...")
    
    def _update_download_progress(self, downloaded, total):
        """Update download progress"""
        if total > 0:
            progress = int((downloaded / total) * 100)
            self.progress_bar.setValue(progress)
    
    def _on_download_finished(self, success):
        """Handle download finish"""
        self.progress_bar.setVisible(False)
        
        if success:
            self._update_versions_list()
            self.statusBar().showMessage("Download complete")
            QMessageBox.information(self, "Success", "Version downloaded successfully")
        else:
            self.statusBar().showMessage("Download failed")
            QMessageBox.warning(self, "Error", "Download failed")
    
    def _launch_game(self):
        """Launch game"""
        current_profile = self.profile_combo.currentText()
        
        if current_profile == "No profiles":
            QMessageBox.warning(self, "Warning", "Create a profile first")
            return
        
        self.launch_button.setEnabled(False)
        self.statusBar().showMessage("Launching game...")
        
        self.launch_thread = LaunchThread(current_profile)
        self.launch_thread.finished.connect(self._on_launch_finished)
        self.launch_thread.start()
    
    def _on_launch_finished(self, success):
        """Handle launch finish"""
        self.launch_button.setEnabled(True)
        
        if success:
            self.statusBar().showMessage("Game launched successfully")
        else:
            self.statusBar().showMessage("Launch failed")
            QMessageBox.warning(self, "Error", "Failed to launch game")
    
    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, config=self.config)
        
        if dialog.exec() == SettingsDialog.Accepted:
            result = dialog.get_result()
            if result:
                for key, value in result.items():
                    Config.set(key, value)
                self.config = Config.load()
                self.statusBar().showMessage("Settings saved")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>PyMinecraftLauncher</h2>
        <p>Version 1.0.0</p>
        <p>A beautiful Minecraft launcher built with Python and PyQt6</p>
        <p>Features:</p>
        <ul>
        <li>Vanilla Minecraft support</li>
        <li>Forge and Fabric modloader support</li>
        <li>Java auto-detection</li>
        <li>Profile management</li>
        <li>Customizable settings</li>
        </ul>
        <p><a href="https://github.com/bbqabsolute/PyMinecraftLauncher">GitHub Repository</a></p>
        """
        
        QMessageBox.about(self, "About PyMinecraftLauncher", about_text)
