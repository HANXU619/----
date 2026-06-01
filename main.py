import sys
import os
from PyQt5.QtWidgets import QApplication
from voice_assistant import VoiceAssistant
from gui import VoiceAssistantGUI

def main():
    app = QApplication(sys.argv)

    app.setApplicationName("智能语音助手")
    app.setOrganizationName("VoiceAssistant")

    assistant = VoiceAssistant()
    gui = VoiceAssistantGUI(assistant)

    def on_transcription(text):
        gui.add_log(f"🎤 识别: {text}", "command")

    def on_wake():
        gui.update_status("● 我在，请说话...")

    def on_awake_mode(awake):
        if awake:
            gui.update_status("● 唤醒模式 - 等待命令")
        else:
            gui.update_status("● 监听中...")

    def on_result(result, response):
        if result['success']:
            gui.add_log(f"✅ {result['message']}", "success")
        else:
            gui.add_log(f"❌ {result['message']}", "error")

    assistant.set_callback('on_transcription', on_transcription)
    assistant.set_callback('on_wake', on_wake)
    assistant.set_callback('on_awake_mode', on_awake_mode)
    assistant.set_callback('on_result', on_result)

    if not assistant.initialize():
        print("初始化失败，请检查依赖是否正确安装")
        print("请运行: pip install -r requirements.txt")

    import threading
    def start_listening_thread():
        import time
        time.sleep(1)
        assistant.start_listening()

    threading.Thread(target=start_listening_thread, daemon=True).start()

    gui.show()

    gui.add_log("🎉 智能语音助手已启动", "success")
    gui.add_log(f"💡 唤醒词: {assistant.wake_words[0]}", "info")
    gui.add_log("💡 说'助手'唤醒，然后说出命令", "info")
    gui.add_log("💡 使用文本输入或快捷命令", "info")

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
