import time
import logging
logging.basicConfig(level=logging.INFO)

from voice_assistant import VoiceAssistant

def main():
    print("=" * 50)
    print("持续监听测试")
    print("=" * 50)

    assistant = VoiceAssistant()

    def on_transcription(text):
        print(f"🎤 识别: {text}")

    def on_wake():
        print("🔔 唤醒回调触发")

    def on_result(result, response):
        print(f"📋 结果: {result}")

    assistant.set_callback('on_transcription', on_transcription)
    assistant.set_callback('on_wake', on_wake)
    assistant.set_callback('on_result', on_result)

    print("正在初始化...")
    if not assistant.initialize():
        print("❌ 初始化失败")
        return

    print("\n开始持续监听...")
    print("说'语音助手'唤醒\n")
    assistant.start_listening()

    try:
        while True:
            time.sleep(1)
            status = assistant.get_status()
            print(f"\r状态: listening={status['is_listening']}, awake={status['is_awake']}, processing={assistant.is_processing}", end="", flush=True)
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        assistant.cleanup()
        print("测试结束")

if __name__ == '__main__':
    main()
