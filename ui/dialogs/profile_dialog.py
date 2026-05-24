"""
Profile dialog for creating and editing profiles
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSpinBox, QComboBox, QPushButton, 
                             QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt
from utils.system import JavaDetector
from utils.logger import get_logger

logger = get_logger("profile_dialog")


class ProfileDialog(QDialog):
    """Dialog for creating/editing profiles"""
    
    def __init__(self, parent=None, profile=None, versions=None):
        super().__init__(parent)
        self.profile = profile
        self.versions = versions or []
        self.result_data = None
        
        self.setWindowTitle("Create Profile" if not profile else "Edit Profile")
        self.setGeometry(100, 100, 500, 400)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Profile name
        name_layout = QHBoxLayout()
        name_label = QLabel("Profile Name:")
        self.name_input = QLineEdit()
        if self.profile:
            self.name_input.setText(self.profile.name)
            self.name_input.setReadOnly(True)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Version selection
        version_layout = QHBoxLayout()
        version_label = QLabel("Minecraft Version:")
        self.version_combo = QComboBox()
        self.version_combo.addItems(self.versions)
        if self.profile:
            index = self.version_combo.findText(self.profile.version)
            if index >= 0:
                self.version_combo.setCurrentIndex(index)
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_combo)
        layout.addLayout(version_layout)
        
        # Java path
        java_layout = QHBoxLayout()
        java_label = QLabel("Java Path:")
        self.java_input = QLineEdit()
        if self.profile and self.profile.java_path:
            self.java_input.setText(self.profile.java_path)
        java_button = QPushButton("Auto-Detect")
        java_button.clicked.connect(self._auto_detect_java)
        java_layout.addWidget(java_label)
        java_layout.addWidget(self.java_input)
        java_layout.addWidget(java_button)
        layout.addLayout(java_layout)
        
        # RAM allocation
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM (MB):")
        self.ram_spin = QSpinBox()
        self.ram_spin.setMinimum(512)
        self.ram_spin.setMaximum(8192)
        self.ram_spin.setValue(self.profile.ram if self.profile else 2048)
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_spin)
        layout.addLayout(ram_layout)
        
        # Modloader selection
        modloader_layout = QHBoxLayout()
        modloader_label = QLabel("Modloader:")
        self.modloader_combo = QComboBox()
        self.modloader_combo.addItems(["Vanilla", "Forge", "Fabric"])
        if self.profile:
            index = self.modloader_combo.findText(self.profile.modloader.capitalize())
            if index >= 0:
                self.modloader_combo.setCurrentIndex(index)
        modloader_layout.addWidget(modloader_label)
        modloader_layout.addWidget(self.modloader_combo)
        layout.addLayout(modloader_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("OK")
        ok_button.setObjectName("primaryButton")
        ok_button.clicked.connect(self._accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _auto_detect_java(self):
        """Auto-detect Java installation"""
        java_installations = JavaDetector.find_java_installations()
        
        if java_installations:
            self.java_input.setText(java_installations[0])
        else:
            logger.warning("No Java installation found")
    
    def _accept(self):
        """Accept and return data"""
        if not self.name_input.text().strip():
            logger.error("Profile name cannot be empty")
            return
        
        self.result_data = {
            "name": self.name_input.text().strip(),
            "version": self.version_combo.currentText(),
            "java_path": self.java_input.text().strip() or None,
            "ram": self.ram_spin.value(),
            "modloader": self.modloader_combo.currentText().lower()
        }
        
        self.accept()
    
    def get_result(self):
        """Get dialog result"""
        return self.result_data
