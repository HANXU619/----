import os
import sys

class Config:
    APP_NAME = "智能语音助手"
    APP_VERSION = "1.0.0"

    # 使用更大的模型提高识别准确率
    # 可选: tiny, base, small, medium, large
    # tiny: 39M - 最快，精度较低
    # base: 74M - 快速，精度适中
    # small: 244M - 较慢，精度较高 (推荐)
    # medium: 769M - 慢，精度高
    # large: 1550M - 最慢，精度最高
    WHISPER_MODEL = "small"

    SUPPORTED_COMMANDS = [
        "打开",
        "搜索",
        "关闭",
        "启动",
        "查找",
        "播放",
        "暂停",
        "停止"
    ]

    BROWSER_PATHS = {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
    }

    DEFAULT_BROWSER = "chrome"

    LOG_FILE = "voice_assistant.log"
    CONFIG_DIR = "config"
    COMMANDS_FILE = "commands.json"
