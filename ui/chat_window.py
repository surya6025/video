"""
Main chat window for JarvisX
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, 
    QPushButton, QLabel, QFrame, QSplitter, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QHBoxLayout, QVBoxLayout, QWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor, QPalette, QColor
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect

class MessageWidget(QFrame):
    """Individual message widget"""
    
    def __init__(self, content: str, role: str, timestamp: str = None, meta: Dict[str, Any] = None):
        super().__init__()
        self.content = content
        self.role = role
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self.meta = meta or {}
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the message UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Avatar
        avatar_label = QLabel()
        avatar_label.setFixedSize(32, 32)
        avatar_label.setScaledContents(True)
        
        if self.role == "user":
            avatar_label.setText("👤")
            avatar_label.setStyleSheet("font-size: 20px; text-align: center;")
        else:
            avatar_label.setText("🤖")
            avatar_label.setStyleSheet("font-size: 20px; text-align: center;")
        
        layout.addWidget(avatar_label)
        
        # Message content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Header with timestamp
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        role_label = QLabel(self.role.title())
        role_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        role_label.setStyleSheet("color: #666;")
        
        timestamp_label = QLabel(self.timestamp)
        timestamp_label.setFont(QFont("Segoe UI", 8))
        timestamp_label.setStyleSheet("color: #999;")
        
        header_layout.addWidget(role_label)
        header_layout.addStretch()
        header_layout.addWidget(timestamp_label)
        
        content_layout.addLayout(header_layout)
        
        # Message text
        message_text = QTextEdit()
        message_text.setPlainText(self.content)
        message_text.setReadOnly(True)
        message_text.setMaximumHeight(200)
        message_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        message_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set fixed width for better layout
        message_text.setFixedWidth(400)
        
        content_layout.addWidget(message_text)
        
        # Add meta information if available
        if self.meta and self.meta.get("skill"):
            skill_label = QLabel(f"Skill: {self.meta['skill']}")
            skill_label.setFont(QFont("Segoe UI", 8))
            skill_label.setStyleSheet("color: #2196f3; font-style: italic;")
            content_layout.addWidget(skill_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Set frame properties
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    
    def apply_theme(self):
        """Apply theme styling"""
        if self.role == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
            """)

class ChatInputWidget(QWidget):
    """Chat input widget with send button and file drop support"""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the input UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(8)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(80)
        self.text_input.setPlaceholderText("Type your message here... (Ctrl+Enter to send)")
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(80, 40)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # File drop area
        self.file_drop_label = QLabel("Drop files here for context (or click to browse)")
        self.file_drop_label.setAlignment(Qt.AlignCenter)
        self.file_drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 16px;
                background-color: #fafafa;
                color: #666;
            }
            QLabel:hover {
                border-color: #2196f3;
                background-color: #f0f8ff;
            }
        """)
        self.file_drop_label.setMinimumHeight(60)
        
        # Enable file drop
        self.file_drop_label.setAcceptDrops(True)
        self.file_drop_label.dragEnterEvent = self.dragEnterEvent
        self.file_drop_label.dropEvent = self.dropEvent
        self.file_drop_label.mousePressEvent = self.mousePressEvent
        
        layout.addWidget(self.file_drop_label)
        
        # Connect keyboard shortcuts
        self.text_input.textChanged.connect(self.on_text_changed)
    
    def send_message(self):
        """Send the current message"""
        text = self.text_input.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.text_input.clear()
            self.text_input.setFocus()
    
    def on_text_changed(self):
        """Handle text input changes"""
        text = self.text_input.toPlainText().strip()
        self.send_button.setEnabled(bool(text))
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.file_drop_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #2196f3;
                    border-radius: 8px;
                    padding: 16px;
                    background-color: #e3f2fd;
                    color: #1976d2;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.file_drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 16px;
                background-color: #fafafa;
                color: #666;
            }
            QLabel:hover {
                border-color: #2196f3;
                background-color: #f0f8ff;
            }
        """)
    
    def dropEvent(self, event):
        """Handle file drop event"""
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                # TODO: Handle file processing
                print(f"File dropped: {file_path}")
        
        self.file_drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 16px;
                background-color: #fafafa;
                color: #666;
            }
            QLabel:hover {
                border-color: #2196f3;
                background-color: #f0f8ff;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press for file browsing"""
        if event.button() == Qt.LeftButton:
            # TODO: Open file browser
            print("File browser clicked")

class ConversationSidebar(QWidget):
    """Sidebar showing conversation history and skills"""
    
    conversation_selected = pyqtSignal(str)
    skill_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("JarvisX")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2196f3; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Skills section
        skills_label = QLabel("Skills")
        skills_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        skills_label.setStyleSheet("color: #333; margin-top: 16px;")
        layout.addWidget(skills_label)
        
        self.skills_list = QListWidget()
        self.skills_list.setMaximumHeight(200)
        self.skills_list.itemClicked.connect(self.on_skill_selected)
        
        # Add default skills
        skills = [
            "NLP", "Machine Learning", "Data Science", "Data Engineering",
            "Analytics", "Automation", "Cybersecurity", "System Control",
            "Web Search", "UI/UX"
        ]
        
        for skill in skills:
            item = QListWidgetItem(skill)
            self.skills_list.addItem(item)
        
        layout.addWidget(self.skills_list)
        
        # Conversations section
        conv_label = QLabel("Conversations")
        conv_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        conv_label.setStyleSheet("color: #333; margin-top: 16px;")
        layout.addWidget(conv_label)
        
        self.conversations_list = QListWidget()
        self.conversations_list.setMaximumHeight(150)
        self.conversations_list.itemClicked.connect(self.on_conversation_selected)
        
        # Add default conversation
        default_item = QListWidgetItem("Current Chat")
        default_item.setData(Qt.UserRole, "current")
        self.conversations_list.addItem(default_item)
        
        layout.addWidget(self.conversations_list)
        
        # Status section
        status_label = QLabel("Status")
        status_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        status_label.setStyleSheet("color: #333; margin-top: 16px;")
        layout.addWidget(status_label)
        
        self.status_label = QLabel("🟢 Online")
        self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def on_skill_selected(self, item):
        """Handle skill selection"""
        skill_name = item.text()
        self.skill_selected.emit(skill_name)
    
    def on_conversation_selected(self, item):
        """Handle conversation selection"""
        conv_id = item.data(Qt.UserRole)
        self.conversation_selected.emit(conv_id)
    
    def update_status(self, status: str):
        """Update status display"""
        if status == "online":
            self.status_label.setText("🟢 Online")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif status == "thinking":
            self.status_label.setText("🟡 Thinking...")
            self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif status == "offline":
            self.status_label.setText("🔴 Offline")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")

class ChatWindow(QWidget):
    """Main chat window with messages and input"""
    
    message_sent = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.messages = []
        self.current_theme = "light"
        
        self.setup_ui()
        self.setup_theme()
    
    def setup_ui(self):
        """Setup the chat window UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for sidebar and chat
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Sidebar
        self.sidebar = ConversationSidebar()
        self.sidebar.setFixedWidth(200)
        splitter.addWidget(self.sidebar)
        
        # Chat area
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Messages area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        
        self.messages_scroll.setWidget(self.messages_widget)
        chat_layout.addWidget(self.messages_scroll)
        
        # Input area
        self.chat_input = ChatInputWidget()
        self.chat_input.message_sent.connect(self.on_message_sent)
        chat_layout.addWidget(self.chat_input)
        
        # Create chat container
        chat_container = QWidget()
        chat_container.setLayout(chat_layout)
        splitter.addWidget(chat_container)
        
        # Set splitter proportions
        splitter.setSizes([200, 600])
        
        # Connect sidebar signals
        self.sidebar.skill_selected.connect(self.on_skill_selected)
        self.sidebar.conversation_selected.connect(self.on_conversation_selected)
    
    def setup_theme(self):
        """Setup the chat theme"""
        if self.current_theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #333333;
                }
                QScrollArea {
                    border: none;
                    background-color: #ffffff;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #c0c0c0;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #a0a0a0;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QScrollArea {
                    border: none;
                    background-color: #2d2d2d;
                }
                QScrollBar:vertical {
                    background-color: #3c3c3c;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #555555;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #777777;
                }
            """)
    
    def on_message_sent(self, message: str):
        """Handle message sent from input"""
        # Add user message to chat
        self.add_user_message(message)
        
        # Emit signal for processing
        self.message_sent.emit(message)
    
    def add_user_message(self, content: str):
        """Add a user message to the chat"""
        message_widget = MessageWidget(content, "user")
        self.messages.append(message_widget)
        self.messages_layout.addWidget(message_widget)
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def add_assistant_message(self, content: str, meta: Dict[str, Any] = None):
        """Add an assistant message to the chat"""
        message_widget = MessageWidget(content, "assistant", meta=meta)
        self.messages.append(message_widget)
        self.messages_layout.addWidget(message_widget)
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll the messages area to the bottom"""
        QTimer.singleShot(100, lambda: self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        ))
    
    def load_history(self, history: List[Dict[str, Any]]):
        """Load conversation history"""
        # Clear existing messages
        self.clear_chat()
        
        # Add historical messages
        for msg in history:
            if msg["role"] == "user":
                self.add_user_message(msg["content"])
            else:
                self.add_assistant_message(msg["content"], msg.get("meta"))
    
    def clear_chat(self):
        """Clear all messages from the chat"""
        # Remove all message widgets
        for message in self.messages:
            message.setParent(None)
            message.deleteLater()
        
        self.messages.clear()
        
        # Clear layout
        while self.messages_layout.count():
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def on_skill_selected(self, skill_name: str):
        """Handle skill selection from sidebar"""
        # TODO: Show skill information or examples
        print(f"Skill selected: {skill_name}")
    
    def on_conversation_selected(self, conv_id: str):
        """Handle conversation selection from sidebar"""
        if conv_id == "current":
            # Load current conversation
            history = self.assistant.get_conversation_history()
            self.load_history(history)
        else:
            # Load specific conversation
            self.assistant.load_conversation(conv_id)
            history = self.assistant.get_conversation_history()
            self.load_history(history)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.setup_theme()
        self.theme_changed.emit(self.current_theme)
    
    def update_status(self, status: str):
        """Update the status display"""
        self.sidebar.update_status(status)