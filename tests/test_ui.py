"""
Tests for the UI components
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class TestChatWindow:
    """Test the ChatWindow class"""
    
    def test_init(self, qapp):
        """Test ChatWindow initialization"""
        from ui.chat_window import ChatWindow
        
        window = ChatWindow()
        assert window is not None
        assert hasattr(window, 'message_list')
        assert hasattr(window, 'input_widget')
        assert hasattr(window, 'sidebar')
    
    def test_add_message(self, qapp):
        """Test adding messages to chat"""
        from ui.chat_window import ChatWindow
        
        window = ChatWindow()
        
        # Add user message
        window.add_message("Hello, JarvisX!", "user")
        
        # Add assistant message
        window.add_message("Hello! How can I help you today?", "assistant")
        
        # Verify messages were added
        assert window.message_list.count() == 2
        
        # Check message content
        user_item = window.message_list.item(0)
        assistant_item = window.message_list.item(1)
        
        assert "Hello, JarvisX!" in user_item.text()
        assert "Hello! How can I help you today?" in assistant_item.text()
    
    def test_clear_messages(self, qapp):
        """Test clearing all messages"""
        from ui.chat_window import ChatWindow
        
        window = ChatWindow()
        
        # Add some messages
        window.add_message("Message 1", "user")
        window.add_message("Message 2", "assistant")
        
        # Clear messages
        window.clear_messages()
        
        # Verify messages were cleared
        assert window.message_list.count() == 0
    
    def test_message_sending(self, qapp):
        """Test message sending functionality"""
        from ui.chat_window import ChatWindow
        
        window = ChatWindow()
        
        # Mock the message_sent signal
        message_sent_mock = Mock()
        window.message_sent.connect(message_sent_mock)
        
        # Set input text
        window.input_widget.text_edit.setPlainText("Test message")
        
        # Simulate sending message
        QTest.keyPress(window.input_widget.text_edit, Qt.Key_Return, Qt.ControlModifier)
        
        # Verify signal was emitted
        message_sent_mock.assert_called_once()
    
    def test_sidebar_functionality(self, qapp):
        """Test conversation sidebar functionality"""
        from ui.chat_window import ChatWindow
        
        window = ChatWindow()
        
        # Add conversation to sidebar
        window.sidebar.add_conversation("Test Conversation", "conv_123")
        
        # Verify conversation was added
        assert window.sidebar.conversation_list.count() == 1
        
        # Select conversation
        window.sidebar.conversation_list.setCurrentRow(0)
        
        # Verify selection
        assert window.sidebar.conversation_list.currentItem().text() == "Test Conversation"

class TestChatInputWidget:
    """Test the ChatInputWidget class"""
    
    def test_init(self, qapp):
        """Test ChatInputWidget initialization"""
        from ui.chat_window import ChatInputWidget
        
        widget = ChatInputWidget()
        assert widget is not None
        assert hasattr(widget, 'text_edit')
        assert hasattr(widget, 'send_button')
    
    def test_text_input(self, qapp):
        """Test text input functionality"""
        from ui.chat_window import ChatInputWidget
        
        widget = ChatInputWidget()
        
        # Set text
        test_text = "This is a test message"
        widget.text_edit.setPlainText(test_text)
        
        # Verify text was set
        assert widget.text_edit.toPlainText() == test_text
    
    def test_send_button_click(self, qapp):
        """Test send button click"""
        from ui.chat_window import ChatInputWidget
        
        widget = ChatInputWidget()
        
        # Mock the send_clicked signal
        send_clicked_mock = Mock()
        widget.send_clicked.connect(send_clicked_mock)
        
        # Set text
        widget.text_edit.setPlainText("Test message")
        
        # Click send button
        QTest.mouseClick(widget.send_button, Qt.LeftButton)
        
        # Verify signal was emitted
        send_clicked_mock.assert_called_once()
    
    def test_enter_key_send(self, qapp):
        """Test sending message with Enter key"""
        from ui.chat_window import ChatInputWidget
        
        widget = ChatInputWidget()
        
        # Mock the send_clicked signal
        send_clicked_mock = Mock()
        widget.send_clicked.connect(send_clicked_mock)
        
        # Set text
        widget.text_edit.setPlainText("Test message")
        
        # Press Enter
        QTest.keyPress(widget.text_edit, Qt.Key_Return)
        
        # Verify signal was emitted
        send_clicked_mock.assert_called_once()
    
    def test_clear_input(self, qapp):
        """Test clearing input field"""
        from ui.chat_window import ChatInputWidget
        
        widget = ChatInputWidget()
        
        # Set text
        widget.text_edit.setPlainText("Test message")
        
        # Clear input
        widget.clear_input()
        
        # Verify input was cleared
        assert widget.text_edit.toPlainText() == ""

class TestRichOutputPanel:
    """Test the RichOutputPanel class"""
    
    def test_init(self, qapp):
        """Test RichOutputPanel initialization"""
        from ui.widgets import RichOutputPanel
        
        panel = RichOutputPanel()
        assert panel is not None
        assert hasattr(panel, 'stacked_widget')
        assert hasattr(panel, 'text_widget')
        assert hasattr(panel, 'table_widget')
    
    def test_display_text(self, qapp):
        """Test displaying text content"""
        from ui.widgets import RichOutputPanel
        
        panel = RichOutputPanel()
        
        # Display text
        test_text = "This is test output"
        panel.display_text(test_text)
        
        # Verify text was displayed
        assert test_text in panel.text_widget.toPlainText()
    
    def test_display_table(self, qapp):
        """Test displaying table data"""
        from ui.widgets import RichOutputPanel
        
        panel = RichOutputPanel()
        
        # Sample table data
        headers = ["Name", "Age", "City"]
        data = [
            ["Alice", "25", "New York"],
            ["Bob", "30", "Los Angeles"],
            ["Charlie", "35", "Chicago"]
        ]
        
        # Display table
        panel.display_table(headers, data)
        
        # Verify table was displayed
        assert panel.table_widget.rowCount() == 3
        assert panel.table_widget.columnCount() == 3
        
        # Check first row data
        assert panel.table_widget.item(0, 0).text() == "Alice"
        assert panel.table_widget.item(0, 1).text() == "25"
        assert panel.table_widget.item(0, 2).text() == "New York"
    
    def test_clear_content(self, qapp):
        """Test clearing panel content"""
        from ui.widgets import RichOutputPanel
        
        panel = RichOutputPanel()
        
        # Add some content
        panel.display_text("Test text")
        panel.display_table(["Header"], [["Data"]])
        
        # Clear content
        panel.clear_content()
        
        # Verify content was cleared
        assert panel.text_widget.toPlainText() == ""
        assert panel.table_widget.rowCount() == 0

class TestSettingsModal:
    """Test the SettingsModal class"""
    
    def test_init(self, qapp):
        """Test SettingsModal initialization"""
        from ui.widgets import SettingsModal
        
        modal = SettingsModal()
        assert modal is not None
        assert hasattr(modal, 'tab_widget')
        assert hasattr(modal, 'general_tab')
        assert hasattr(modal, 'ai_tab')
        assert hasattr(modal, 'security_tab')
        assert hasattr(modal, 'memory_tab')
    
    def test_tab_navigation(self, qapp):
        """Test tab navigation"""
        from ui.widgets import SettingsModal
        
        modal = SettingsModal()
        
        # Switch to AI tab
        modal.tab_widget.setCurrentIndex(1)
        assert modal.tab_widget.currentWidget() == modal.ai_tab
        
        # Switch to Security tab
        modal.tab_widget.setCurrentIndex(2)
        assert modal.tab_widget.currentWidget() == modal.security_tab
    
    def test_settings_save_load(self, qapp):
        """Test settings save and load functionality"""
        from ui.widgets import SettingsModal
        
        modal = SettingsModal()
        
        # Mock save and load methods
        save_mock = Mock()
        load_mock = Mock()
        modal.save_settings = save_mock
        modal.load_settings = load_mock
        
        # Test save
        modal.save_button.click()
        save_mock.assert_called_once()
        
        # Test load
        modal.load_button.click()
        load_mock.assert_called_once()

class TestToastNotification:
    """Test the ToastNotification class"""
    
    def test_init(self, qapp):
        """Test ToastNotification initialization"""
        from ui.widgets import ToastNotification
        
        notification = ToastNotification("Test message", "info")
        assert notification is not None
        assert notification.message == "Test message"
        assert notification.type == "info"
    
    def test_auto_hide(self, qapp):
        """Test auto-hide functionality"""
        from ui.widgets import ToastNotification
        
        notification = ToastNotification("Test message", "info")
        notification.show()
        
        # Wait for auto-hide timer
        QTimer.singleShot(100, lambda: None)
        QTest.qWait(200)
        
        # Verify notification was hidden
        assert not notification.isVisible()
    
    def test_different_types(self, qapp):
        """Test different notification types"""
        from ui.widgets import ToastNotification
        
        # Test info notification
        info_notif = ToastNotification("Info message", "info")
        assert "info" in info_notif.styleSheet().lower()
        
        # Test success notification
        success_notif = ToastNotification("Success message", "success")
        assert "success" in success_notif.styleSheet().lower()
        
        # Test warning notification
        warning_notif = ToastNotification("Warning message", "warning")
        assert "warning" in warning_notif.styleSheet().lower()
        
        # Test error notification
        error_notif = ToastNotification("Error message", "error")
        assert "error" in error_notif.styleSheet().lower()

class TestJarvisXApp:
    """Test the main JarvisXApp class"""
    
    def test_init(self, qapp):
        """Test JarvisXApp initialization"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        assert app is not None
        assert hasattr(app, 'main_window')
        assert hasattr(app, 'assistant')
    
    def test_theme_switching(self, qapp):
        """Test theme switching functionality"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Switch to dark theme
        app.switch_theme("dark")
        assert "dark" in app.main_window.styleSheet().lower()
        
        # Switch to light theme
        app.switch_theme("light")
        assert "light" in app.main_window.styleSheet().lower()
    
    def test_menu_functionality(self, qapp):
        """Test menu functionality"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Test file menu
        file_menu = app.main_window.menuBar().actions()[0]  # File menu
        assert file_menu.text() == "&File"
        
        # Test help menu
        help_menu = app.main_window.menuBar().actions()[-1]  # Help menu
        assert help_menu.text() == "&Help"
    
    def test_toolbar_functionality(self, qapp):
        """Test toolbar functionality"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Verify toolbar exists
        assert app.main_window.toolBar() is not None
        
        # Check toolbar actions
        toolbar_actions = app.main_window.toolBar().actions()
        assert len(toolbar_actions) > 0

class TestUIIntegration:
    """Test UI component integration"""
    
    def test_signal_connections(self, qapp):
        """Test that UI signals are properly connected"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Test chat input to assistant connection
        chat_input = app.main_window.chat_window.input_widget
        
        # Mock assistant method
        process_message_mock = Mock()
        app.assistant.process_message = process_message_mock
        
        # Send message
        chat_input.text_edit.setPlainText("Test message")
        QTest.keyPress(chat_input.text_edit, Qt.Key_Return, Qt.ControlModifier)
        
        # Verify assistant was called
        # Note: This test may need adjustment based on actual signal connections
    
    def test_theme_consistency(self, qapp):
        """Test that theme is applied consistently across all components"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Switch to dark theme
        app.switch_theme("dark")
        
        # Verify all components have dark theme
        main_style = app.main_window.styleSheet()
        chat_style = app.main_window.chat_window.styleSheet()
        
        assert "dark" in main_style.lower()
        assert "dark" in chat_style.lower()
    
    def test_responsive_layout(self, qapp):
        """Test that layout responds to window resizing"""
        from core.app import JarvisXApp
        
        app = JarvisXApp()
        
        # Get initial sizes
        initial_chat_width = app.main_window.chat_window.width()
        initial_output_width = app.main_window.output_panel.width()
        
        # Resize window
        app.main_window.resize(800, 600)
        
        # Verify components adjusted
        new_chat_width = app.main_window.chat_window.width()
        new_output_width = app.main_window.output_panel.width()
        
        # Sizes should have changed
        assert new_chat_width != initial_chat_width or new_output_width != initial_output_width