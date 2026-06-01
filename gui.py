import sys
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QScrollArea, QFrame, QGraphicsDropShadowEffect,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QBrush, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta

class Communicator(QObject):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    transcription_signal = pyqtSignal(str)

class ModernButton(QPushButton):
    def __init__(self, icon=None, text="", parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 10px;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #264f78;
            }
        """)

        layout.addWidget(self.log_list)
        self.setLayout(layout)

    def add_log(self, text, log_type="info"):
        item = QListWidgetItem(text)

        if log_type == "error":
            item.setForeground(QColor("#f44336"))
        elif log_type == "success":
            item.setForeground(QColor("#4CAF50"))
        elif log_type == "warning":
            item.setForeground(QColor("#ff9800"))
        elif log_type == "command":
            item.setForeground(QColor("#2196F3"))
        else:
            item.setForeground(QColor("#d4d4d4"))

        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

class VoiceAssistantGUI(QMainWindow):
    def __init__(self, voice_assistant):
        super().__init__()
        self.assistant = voice_assistant
        self.communicator = Communicator()
        self.is_listening = False

        self.communicator.log_signal.connect(self.add_log)
        self.communicator.status_signal.connect(self.update_status)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("智能语音助手")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = self.create_header()
        main_layout.addWidget(header)

        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        content_layout.addWidget(left_panel, 2)
        content_layout.addWidget(right_panel, 1)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        central_widget.setLayout(main_layout)

    def create_header(self):
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-radius: 15px;
                padding: 20px;
            }
        """)

        header_layout = QVBoxLayout()

        title_label = QLabel("🎤 智能语音助手")
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("基于Transformer的语音识别系统")
        subtitle_label.setFont(QFont("Microsoft YaHei", 10))
        subtitle_label.setStyleSheet("color: #888;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("● 就绪")
        self.status_label.setFont(QFont("Consolas", 10))
        self.status_label.setStyleSheet("color: #4CAF50;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(self.status_label)

        header_widget.setLayout(header_layout)
        return header_widget

    def create_left_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("📝 命令日志")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")

        self.log_widget = LogWidget()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.text_input_button = ModernButton(
            qta.icon('fa5s.keyboard', color='white'),
            "文本输入"
        )
        self.text_input_button.clicked.connect(self.show_text_input_dialog)

        self.clear_button = ModernButton(
            qta.icon('fa5s.trash', color='white'),
            "清空"
        )
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_logs)

        button_layout.addWidget(self.text_input_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        layout.addWidget(title_label)
        layout.addWidget(self.log_widget)
        layout.addLayout(button_layout)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("⚡ 快捷命令")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff;")

        commands = [
            ("🌐", "打开浏览器", "打开浏览器"),
            ("📝", "打开记事本", "打开记事本"),
            ("🧮", "打开计算器", "打开计算器"),
            ("📁", "我的电脑", "打开文件管理器"),
            ("🖼️", "截图", "截图")
        ]

        command_buttons = []
        for icon, text, command in commands:
            btn = QPushButton(f"{icon} {text}")
            btn.setFont(QFont("Microsoft YaHei", 10))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #1d1d1d;
                }
            """)
            btn.clicked.connect(lambda checked, cmd=command: self.execute_quick_command(cmd))
            command_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def show_text_input_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(
            self, '文本输入', '请输入命令:'
        )
        if ok and text:
            self.process_text_command(text)

    def process_text_command(self, text):
        self.add_log(f"📝 文本输入: {text}", "command")

        result = self.assistant.process_command(text)

        if result['success']:
            self.add_log(f"✅ {result['message']}", "success")
        else:
            self.add_log(f"❌ {result['message']}", "error")

        self.update_status("● 就绪")

    def execute_quick_command(self, command):
        self.add_log(f"⚡ 快捷命令: {command}", "command")
        result = self.assistant.process_command(command)

        if result['success']:
            self.add_log(f"✅ {result['message']}", "success")
        else:
            self.add_log(f"❌ {result['message']}", "error")

    def clear_logs(self):
        self.log_widget.log_list.clear()
        self.add_log("🗑️ 日志已清空", "info")

    def add_log(self, text, log_type="info"):
        self.log_widget.add_log(text, log_type)

    def update_status(self, status):
        self.status_label.setText(status)
        if "唤醒" in status:
            self.status_label.setStyleSheet("color: #ff9800;")
        elif "聆听" in status or "处理" in status:
            self.status_label.setStyleSheet("color: #2196F3;")
        elif "我在" in status:
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setStyleSheet("color: #4CAF50;")

    def closeEvent(self, event):
        self.assistant.cleanup()
        event.accept()
