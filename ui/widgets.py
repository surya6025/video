"""
UI widgets for JarvisX
Rich output panel, settings modal, and other components
"""

import os
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, 
    QPushButton, QLabel, QFrame, QTabWidget, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QTextBrowser, QProgressBar, QSplitter,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor, QPalette, QColor
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

class RichOutputPanel(QWidget):
    """Right panel for displaying rich output (tables, charts, files)"""
    
    content_updated = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self.current_content = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the rich output panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Output")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #333; margin-bottom: 8px;")
        
        clear_button = QPushButton("Clear")
        clear_button.setFixedSize(60, 30)
        clear_button.clicked.connect(self.clear_content)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        
        layout.addLayout(header_layout)
        
        # Content tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Text tab
        self.text_tab = QWidget()
        self.text_layout = QVBoxLayout(self.text_tab)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_layout.addWidget(self.text_browser)
        self.tab_widget.addTab(self.text_tab, "Text")
        
        # Table tab
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.table_widget = QTableWidget()
        self.table_layout.addWidget(self.table_widget)
        self.tab_widget.addTab(self.table_tab, "Table")
        
        # Chart tab
        self.chart_tab = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_tab)
        self.chart_canvas = None
        self.chart_layout.addWidget(QLabel("Charts will appear here"))
        self.tab_widget.addTab(self.chart_tab, "Chart")
        
        # Files tab
        self.files_tab = QWidget()
        self.files_layout = QVBoxLayout(self.files_tab)
        self.files_list = QListWidget()
        self.files_layout.addWidget(self.files_list)
        self.tab_widget.addTab(self.files_tab, "Files")
        
        layout.addWidget(self.tab_widget)
        
        # Set initial content
        self.text_browser.setHtml("<h3>Welcome to JarvisX!</h3><p>Your AI assistant output will appear here.</p>")
    
    def update_content(self, result: Dict[str, Any]):
        """Update the output panel with new content"""
        try:
            self.current_content = result
            content_type = result.get("type", "text")
            
            if content_type == "text":
                self.update_text_content(result.get("content", ""))
                self.tab_widget.setCurrentIndex(0)
                
            elif content_type == "table":
                self.update_table_content(result.get("content", []))
                self.tab_widget.setCurrentIndex(1)
                
            elif content_type == "chart":
                self.update_chart_content(result.get("content", None))
                self.tab_widget.setCurrentIndex(2)
                
            elif content_type == "files":
                self.update_files_content(result.get("artifacts", []))
                self.tab_widget.setCurrentIndex(3)
            
            # Emit content updated signal
            self.content_updated.emit(content_type, result)
            
        except Exception as e:
            self.text_browser.setHtml(f"<h3>Error</h3><p>Failed to update content: {str(e)}</p>")
    
    def update_text_content(self, content: str):
        """Update text content"""
        if content.startswith("<"):
            # HTML content
            self.text_browser.setHtml(content)
        else:
            # Plain text content
            self.text_browser.setPlainText(content)
    
    def update_table_content(self, data: List[List[Any]]):
        """Update table content"""
        if not data:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        
        # Determine if first row is headers
        if len(data) > 0 and all(isinstance(cell, str) for cell in data[0]):
            headers = data[0]
            table_data = data[1:]
        else:
            headers = [f"Column {i+1}" for i in range(len(data[0]))]
            table_data = data
        
        # Set table dimensions
        self.table_widget.setRowCount(len(table_data))
        self.table_widget.setColumnCount(len(headers))
        
        # Set headers
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for row_idx, row_data in enumerate(table_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table_widget.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns
        self.table_widget.resizeColumnsToContents()
    
    def update_chart_content(self, chart_data: Any):
        """Update chart content"""
        try:
            # Clear previous chart
            if self.chart_canvas:
                self.chart_canvas.setParent(None)
                self.chart_canvas.deleteLater()
            
            if chart_data is None:
                self.chart_layout.addWidget(QLabel("No chart data available"))
                return
            
            # Create matplotlib figure
            fig = Figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            
            # Handle different chart types
            if isinstance(chart_data, dict):
                chart_type = chart_data.get("type", "line")
                
                if chart_type == "line":
                    x_data = chart_data.get("x", [])
                    y_data = chart_data.get("y", [])
                    ax.plot(x_data, y_data)
                    ax.set_xlabel(chart_data.get("xlabel", "X"))
                    ax.set_ylabel(chart_data.get("ylabel", "Y"))
                    ax.set_title(chart_data.get("title", "Chart"))
                    
                elif chart_type == "bar":
                    x_data = chart_data.get("x", [])
                    y_data = chart_data.get("y", [])
                    ax.bar(x_data, y_data)
                    ax.set_xlabel(chart_data.get("xlabel", "Categories"))
                    ax.set_ylabel(chart_data.get("ylabel", "Values"))
                    ax.set_title(chart_data.get("title", "Bar Chart"))
                    
                elif chart_type == "scatter":
                    x_data = chart_data.get("x", [])
                    y_data = chart_data.get("y", [])
                    ax.scatter(x_data, y_data)
                    ax.set_xlabel(chart_data.get("xlabel", "X"))
                    ax.set_ylabel(chart_data.get("ylabel", "Y"))
                    ax.set_title(chart_data.get("title", "Scatter Plot"))
                    
                elif chart_type == "histogram":
                    data = chart_data.get("data", [])
                    bins = chart_data.get("bins", 20)
                    ax.hist(data, bins=bins, alpha=0.7)
                    ax.set_xlabel(chart_data.get("xlabel", "Values"))
                    ax.set_ylabel(chart_data.get("ylabel", "Frequency"))
                    ax.set_title(chart_data.get("title", "Histogram"))
            
            # Create canvas and add to layout
            self.chart_canvas = FigureCanvas(fig)
            self.chart_layout.addWidget(self.chart_canvas)
            
            # Refresh canvas
            self.chart_canvas.draw()
            
        except Exception as e:
            self.chart_layout.addWidget(QLabel(f"Error creating chart: {str(e)}"))
    
    def update_files_content(self, files: List[str]):
        """Update files content"""
        self.files_list.clear()
        
        if not files:
            self.files_list.addItem("No files available")
            return
        
        for file_path in files:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                item = QListWidgetItem(f"📄 {file_name}")
                item.setData(Qt.UserRole, file_path)
                self.files_list.addItem(item)
        
        # Connect double-click to open files
        self.files_list.itemDoubleClicked.connect(self.open_file)
    
    def open_file(self, item):
        """Open a file when double-clicked"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {str(e)}")
    
    def clear_content(self):
        """Clear all content"""
        self.current_content = None
        
        # Clear text
        self.text_browser.setHtml("<h3>Output Cleared</h3><p>Ready for new content.</p>")
        
        # Clear table
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        
        # Clear chart
        if self.chart_canvas:
            self.chart_canvas.setParent(None)
            self.chart_canvas.deleteLater()
            self.chart_canvas = None
        self.chart_layout.addWidget(QLabel("Charts will appear here"))
        
        # Clear files
        self.files_list.clear()
        
        # Reset to text tab
        self.tab_widget.setCurrentIndex(0)

class SettingsModal(QDialog):
    """Settings modal dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings UI"""
        self.setWindowTitle("JarvisX Settings")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for different settings categories
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # AI settings tab
        self.ai_tab = self.create_ai_tab()
        self.tab_widget.addTab(self.ai_tab, "AI & Models")
        
        # Security settings tab
        self.security_tab = self.create_security_tab()
        self.tab_widget.addTab(self.security_tab, "Security")
        
        # Memory settings tab
        self.memory_tab = self.create_memory_tab()
        self.tab_widget.addTab(self.memory_tab, "Memory")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        layout.addRow("Theme:", self.theme_combo)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        layout.addRow("Language:", self.language_combo)
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setSuffix(" minutes")
        layout.addRow("Auto-save interval:", self.autosave_spin)
        
        # Notifications
        self.notifications_check = QCheckBox("Enable notifications")
        layout.addRow("", self.notifications_check)
        
        return widget
    
    def create_ai_tab(self):
        """Create AI settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # LLM provider
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["Ollama (Local)", "OpenAI", "Anthropic"])
        layout.addRow("LLM Provider:", self.llm_provider_combo)
        
        # Ollama settings
        self.ollama_host_edit = QLineEdit()
        self.ollama_host_edit.setPlaceholderText("http://localhost:11434")
        layout.addRow("Ollama Host:", self.ollama_host_edit)
        
        self.ollama_model_edit = QLineEdit()
        self.ollama_model_edit.setPlaceholderText("llama3")
        layout.addRow("Ollama Model:", self.ollama_model_edit)
        
        # OpenAI settings
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setPlaceholderText("Enter your OpenAI API key")
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("OpenAI API Key:", self.openai_key_edit)
        
        # Model parameters
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 100)
        self.temperature_spin.setValue(70)
        self.temperature_spin.setSuffix("%")
        layout.addRow("Temperature:", self.temperature_spin)
        
        return widget
    
    def create_security_tab(self):
        """Create security settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Default permission policy
        self.default_policy_combo = QComboBox()
        self.default_policy_combo.addItems(["Ask Every Time", "Trusted Once", "Always Deny"])
        layout.addRow("Default Permission Policy:", self.default_policy_combo)
        
        # Permission timeout
        self.permission_timeout_spin = QSpinBox()
        self.permission_timeout_spin.setRange(30, 3600)
        self.permission_timeout_spin.setSuffix(" seconds")
        layout.addRow("Permission Timeout:", self.permission_timeout_spin)
        
        # Security features
        self.sandbox_check = QCheckBox("Enable sandbox mode")
        layout.addRow("", self.sandbox_check)
        
        self.audit_log_check = QCheckBox("Enable audit logging")
        layout.addRow("", self.audit_log_check)
        
        return widget
    
    def create_memory_tab(self):
        """Create memory settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Supabase settings
        self.supabase_url_edit = QLineEdit()
        self.supabase_url_edit.setPlaceholderText("Enter your Supabase project URL")
        layout.addRow("Supabase URL:", self.supabase_url_edit)
        
        self.supabase_key_edit = QLineEdit()
        self.supabase_key_edit.setPlaceholderText("Enter your Supabase anon key")
        self.supabase_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Supabase Key:", self.supabase_key_edit)
        
        # Local cache settings
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 10000)
        self.cache_size_spin.setSuffix(" MB")
        layout.addRow("Max Cache Size:", self.cache_size_spin)
        
        self.cache_retention_spin = QSpinBox()
        self.cache_retention_spin.setRange(1, 365)
        self.cache_retention_spin.setSuffix(" days")
        layout.addRow("Cache Retention:", self.cache_retention_spin)
        
        return widget
    
    def load_settings(self):
        """Load current settings"""
        try:
            # Load from environment or config file
            # For now, set some defaults
            self.theme_combo.setCurrentText("Light")
            self.language_combo.setCurrentText("English")
            self.autosave_spin.setValue(5)
            self.notifications_check.setChecked(True)
            
            self.llm_provider_combo.setCurrentText("Ollama (Local)")
            self.ollama_host_edit.setText("http://localhost:11434")
            self.ollama_model_edit.setText("llama3")
            self.temperature_spin.setValue(70)
            
            self.default_policy_combo.setCurrentText("Ask Every Time")
            self.permission_timeout_spin.setValue(300)
            self.sandbox_check.setChecked(True)
            self.audit_log_check.setChecked(True)
            
            self.cache_size_spin.setValue(1000)
            self.cache_retention_spin.setValue(30)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Save to environment or config file
            # For now, just accept the dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_settings()

class ToastNotification(QWidget):
    """Toast notification widget"""
    
    def __init__(self, message: str, notification_type: str = "info", parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup the toast UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Icon
        icon_label = QLabel()
        if self.notification_type == "success":
            icon_label.setText("✅")
        elif self.notification_type == "warning":
            icon_label.setText("⚠️")
        elif self.notification_type == "error":
            icon_label.setText("❌")
        else:
            icon_label.setText("ℹ️")
        
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #666;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #333;
            }
        """)
        layout.addWidget(close_button)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                color: #333333;
            }
        """)
        
        # Set size policy
        self.setMaximumWidth(400)
        self.setMinimumHeight(50)
    
    def setup_animation(self):
        """Setup show/hide animations"""
        # Show animation
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(300)
        self.show_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Hide animation
        self.hide_animation = QPropertyAnimation(self, b"geometry")
        self.hide_animation.setDuration(300)
        self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self.hide_animation.finished.connect(self.deleteLater)
    
    def show_toast(self, target_rect: QRect):
        """Show the toast with animation"""
        # Set initial position (off-screen)
        start_rect = QRect(target_rect.x(), target_rect.y() - 100, target_rect.width(), target_rect.height())
        end_rect = target_rect
        
        self.setGeometry(start_rect)
        self.show()
        
        # Animate in
        self.show_animation.setStartValue(start_rect)
        self.show_animation.setEndValue(end_rect)
        self.show_animation.start()
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, self.hide_toast)
    
    def hide_toast(self):
        """Hide the toast with animation"""
        current_rect = self.geometry()
        end_rect = QRect(current_rect.x(), current_rect.y() - 100, current_rect.width(), current_rect.height())
        
        self.hide_animation.setStartValue(current_rect)
        self.hide_animation.setEndValue(end_rect)
        self.hide_animation.start()
    
    def close(self):
        """Close the toast immediately"""
        self.hide_toast()