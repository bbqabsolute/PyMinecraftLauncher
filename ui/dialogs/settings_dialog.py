"""
Settings dialog for launcher configuration
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QGroupBox,
                             QFormLayout, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("settings_dialog")


class SettingsDialog(QDialog):
    """Dialog for launcher settings"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or {}
        self.result_data = None
        
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 600, 500)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Java tab
        java_tab = self._create_java_tab()
        tabs.addTab(java_tab, "Java")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._apply)
        button_layout.addWidget(apply_button)
        
        ok_button = QPushButton("OK")
        ok_button.setObjectName("primaryButton")
        ok_button.clicked.connect(self._accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Game directory
        game_dir_layout = QHBoxLayout()
        self.game_dir_input = QLineEdit()
        self.game_dir_input.setText(self.config.get("game_directory", str(Path.home() / ".minecraft")))
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_game_dir)
        game_dir_layout.addWidget(self.game_dir_input)
        game_dir_layout.addWidget(browse_button)
        layout.addRow("Game Directory:", game_dir_layout)
        
        # Theme
        theme_layout = QHBoxLayout()
        self.theme_input = QLineEdit()
        self.theme_input.setText(self.config.get("theme", "dark"))
        self.theme_input.setReadOnly(True)
        theme_layout.addWidget(self.theme_input)
        layout.addRow("Theme:", theme_layout)
        
        tab.setLayout(layout)
        return tab
    
    def _create_java_tab(self):
        """Create Java settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Java path
        java_path_layout = QHBoxLayout()
        self.java_path_input = QLineEdit()
        self.java_path_input.setText(self.config.get("java_path", ""))
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_java)
        java_path_layout.addWidget(self.java_path_input)
        java_path_layout.addWidget(browse_button)
        layout.addRow("Java Path:", java_path_layout)
        
        # Default RAM
        from PyQt6.QtWidgets import QSpinBox
        ram_spin = QSpinBox()
        ram_spin.setMinimum(512)
        ram_spin.setMaximum(8192)
        ram_spin.setValue(self.config.get("ram_allocation", 2048))
        self.ram_spin = ram_spin
        layout.addRow("Default RAM (MB):", ram_spin)
        
        tab.setLayout(layout)
        return tab
    
    def _browse_game_dir(self):
        """Browse for game directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Game Directory")
        if directory:
            self.game_dir_input.setText(directory)
    
    def _browse_java(self):
        """Browse for Java executable"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Java Executable", "", "Java (java, java.exe)")
        if file_path:
            self.java_path_input.setText(file_path)
    
    def _apply(self):
        """Apply settings"""
        self.result_data = {
            "game_directory": self.game_dir_input.text(),
            "java_path": self.java_path_input.text() or None,
            "ram_allocation": self.ram_spin.value(),
            "theme": self.theme_input.text()
        }
    
    def _accept(self):
        """Accept settings"""
        self._apply()
        self.accept()
    
    def get_result(self):
        """Get settings result"""
        return self.result_data
