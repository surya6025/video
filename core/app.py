"""
PyQt5 application bootstrap for JarvisX
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from .assistant import assistant
from .logging_utils import get_logger
from ui.chat_window import ChatWindow
from ui.widgets import RichOutputPanel, SettingsModal
from typing import Any

logger = get_logger(__name__)

class JarvisXApp(QMainWindow):
    """Main JarvisX application window"""
    
    def __init__(self):
        super().__init__()
        self.assistant = assistant
        self.setup_ui()
        self.setup_theme()
        self.setup_signals()
        self.load_conversation_history()
        
        logger.info("JarvisX application initialized")
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("JarvisX - AI Assistant")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon
        icon_path = Path(__file__).parent.parent / "ui" / "assets" / "logo.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create chat window (left panel)
        self.chat_window = ChatWindow(self.assistant)
        splitter.addWidget(self.chat_window)
        
        # Create rich output panel (right panel)
        self.rich_output = RichOutputPanel()
        splitter.addWidget(self.rich_output)
        
        # Set splitter proportions (70% chat, 30% output)
        splitter.setSizes([980, 420])
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_conversation_action = file_menu.addAction("&New Conversation")
        new_conversation_action.setShortcut("Ctrl+N")
        new_conversation_action.triggered.connect(self.new_conversation)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        settings_action = edit_menu.addAction("&Settings")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_theme_action = view_menu.addAction("Toggle &Theme")
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        skills_action = tools_menu.addAction("&Skills")
        skills_action.triggered.connect(self.show_skills)
        
        system_status_action = tools_menu.addAction("&System Status")
        system_status_action.triggered.connect(self.show_system_status)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("&Help")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
    
    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # New conversation button
        new_conv_action = toolbar.addAction("New")
        new_conv_action.setToolTip("Start new conversation")
        new_conv_action.triggered.connect(self.new_conversation)
        
        toolbar.addSeparator()
        
        # Theme toggle button
        theme_action = toolbar.addAction("Theme")
        theme_action.setToolTip("Toggle light/dark theme")
        theme_action.triggered.connect(self.toggle_theme)
        
        # Settings button
        settings_action = toolbar.addAction("Settings")
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(self.show_settings)
        
        toolbar.addSeparator()
        
        # Skills button
        skills_action = toolbar.addAction("Skills")
        skills_action.setToolTip("View available skills")
        skills_action.triggered.connect(self.show_skills)
    
    def setup_theme(self):
        """Setup application theme"""
        self.current_theme = "light"
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme"""
        if self.current_theme == "light":
            self.setStyleSheet(self.get_light_theme())
        else:
            self.setStyleSheet(self.get_dark_theme())
    
    def get_light_theme(self) -> str:
        """Get light theme stylesheet"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QMenuBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
            color: #333333;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #e3f2fd;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 4px 0px;
        }
        
        QMenu::item {
            padding: 8px 24px;
        }
        
        QMenu::item:selected {
            background-color: #e3f2fd;
        }
        
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
            spacing: 8px;
            padding: 4px;
        }
        
        QToolBar::handle {
            background-color: #e0e0e0;
            width: 1px;
        }
        
        QStatusBar {
            background-color: #ffffff;
            border-top: 1px solid #e0e0e0;
            color: #666666;
        }
        
        QSplitter::handle {
            background-color: #e0e0e0;
            width: 2px;
        }
        
        QSplitter::handle:hover {
            background-color: #2196f3;
        }
        """
    
    def get_dark_theme(self) -> str:
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #2d2d2d;
        }
        
        QMenuBar {
            background-color: #3c3c3c;
            border-bottom: 1px solid #555555;
            color: #ffffff;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #1976d2;
        }
        
        QMenu {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            padding: 4px 0px;
        }
        
        QMenu::item {
            padding: 8px 24px;
        }
        
        QMenu::item:selected {
            background-color: #1976d2;
        }
        
        QToolBar {
            background-color: #3c3c3c;
            border-bottom: 1px solid #555555;
            spacing: 8px;
            padding: 4px;
        }
        
        QToolBar::handle {
            background-color: #555555;
            width: 1px;
        }
        
        QStatusBar {
            background-color: #3c3c3c;
            border-top: 1px solid #555555;
            color: #cccccc;
        }
        
        QSplitter::handle {
            background-color: #555555;
            width: 2px;
        }
        
        QSplitter::handle:hover {
            background-color: #2196f3;
        }
        """
    
    def setup_signals(self):
        """Setup signal connections"""
        # Connect chat window signals
        self.chat_window.message_sent.connect(self.on_message_sent)
        self.chat_window.theme_changed.connect(self.on_theme_changed)
        
        # Connect rich output signals
        self.rich_output.content_updated.connect(self.on_content_updated)
    
    def load_conversation_history(self):
        """Load conversation history into chat window"""
        try:
            history = self.assistant.get_conversation_history()
            self.chat_window.load_history(history)
            logger.info(f"Loaded {len(history)} messages from conversation history")
        except Exception as e:
            logger.error(f"Failed to load conversation history: {e}")
    
    def on_message_sent(self, message: str):
        """Handle user message sent from chat window"""
        try:
            self.statusBar().showMessage("Processing...")
            
            # Process message through assistant
            for result in self.assistant.process_user_message(message):
                if result["type"] == "skill_result":
                    # Update rich output panel
                    self.rich_output.update_content(result["result"])
                    
                    # Update status
                    skill_name = result["skill"]
                    confidence = result["confidence"]
                    self.statusBar().showMessage(f"Executed {skill_name} (confidence: {confidence:.1%})")
                    
                elif result["type"] == "clarification":
                    # Show clarification in chat
                    self.chat_window.add_assistant_message(result["content"])
                    self.statusBar().showMessage("Asked for clarification")
                    
                elif result["type"] == "fallback":
                    # Show fallback response
                    self.chat_window.add_assistant_message(result["content"])
                    self.statusBar().showMessage("Used fallback response")
                    
                elif result["type"] == "error":
                    # Show error message
                    self.chat_window.add_assistant_message(result["content"])
                    self.statusBar().showMessage("Error occurred")
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.statusBar().showMessage("Error processing message")
    
    def on_theme_changed(self, theme: str):
        """Handle theme change from chat window"""
        self.current_theme = theme
        self.apply_theme()
        logger.info(f"Theme changed to: {theme}")
    
    def on_content_updated(self, content_type: str, content: Any):
        """Handle content updates from rich output panel"""
        logger.info(f"Rich output updated: {content_type}")
    
    def new_conversation(self):
        """Start a new conversation"""
        try:
            self.assistant.reset_conversation()
            self.chat_window.clear_chat()
            self.rich_output.clear_content()
            self.statusBar().showMessage("Started new conversation")
            logger.info("Started new conversation")
        except Exception as e:
            logger.error(f"Failed to start new conversation: {e}")
    
    def show_settings(self):
        """Show settings modal"""
        try:
            settings_modal = SettingsModal(self)
            settings_modal.exec_()
        except Exception as e:
            logger.error(f"Failed to show settings: {e}")
    
    def show_skills(self):
        """Show skills information"""
        try:
            skills_info = self.assistant.get_available_skills()
            # TODO: Create skills info dialog
            self.statusBar().showMessage(f"Available skills: {', '.join(skills_info.keys())}")
        except Exception as e:
            logger.error(f"Failed to show skills: {e}")
    
    def show_system_status(self):
        """Show system status information"""
        try:
            status = self.assistant.get_system_status()
            # TODO: Create system status dialog
            self.statusBar().showMessage("System status displayed")
        except Exception as e:
            logger.error(f"Failed to show system status: {e}")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        
        about_text = """
        <h2>JarvisX - Advanced AI Assistant</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> A production-grade Windows desktop AI assistant with persistent memory, strong permission controls, and master-level skills.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Local AI with Ollama integration</li>
            <li>10 master skills (NLP, ML, Data Science, etc.)</li>
            <li>Persistent memory with Supabase</li>
            <li>Strict security and permission controls</li>
            <li>Beautiful PyQt5 interface</li>
        </ul>
        <p><b>Built with ❤️ using Python and modern AI technologies</b></p>
        """
        
        QMessageBox.about(self, "About JarvisX", about_text)
    
    def show_help(self):
        """Show help information"""
        from PyQt5.QtWidgets import QMessageBox
        
        help_text = """
        <h2>JarvisX Help</h2>
        <p><b>Getting Started:</b></p>
        <ul>
            <li>Type your request in the chat input</li>
            <li>I'll automatically route to the appropriate skill</li>
            <li>Results will appear in the right panel</li>
        </ul>
        
        <p><b>Example Commands:</b></p>
        <ul>
            <li>"Create a project plan for a Flask web app"</li>
            <li>"Train a model on my data.csv file"</li>
            <li>"Do EDA on sales.csv and show trends"</li>
            <li>"Open Chrome browser"</li>
            <li>"Scan this log file for errors"</li>
        </ul>
        
        <p><b>Keyboard Shortcuts:</b></p>
        <ul>
            <li>Ctrl+N: New conversation</li>
            <li>Ctrl+T: Toggle theme</li>
            <li>Ctrl+,: Settings</li>
            <li>F1: This help</li>
        </ul>
        
        <p><b>For more information, check the README.md file.</b></p>
        """
        
        QMessageBox.information(self, "JarvisX Help", help_text)
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Cleanup temporary files
            from .io import file_manager
            deleted_count = file_manager.cleanup_temp_files(older_than_hours=1)
            logger.info(f"Cleaned up {deleted_count} temporary files on exit")
            
            # Save conversation state
            # TODO: Implement conversation state saving
            
            event.accept()
            logger.info("JarvisX application closed")
            
        except Exception as e:
            logger.error(f"Error during application close: {e}")
            event.accept()

def create_app() -> QApplication:
    """Create and configure the QApplication"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JarvisX")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("JarvisX")
    app.setOrganizationDomain("jarvisx.ai")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set default font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    return app