import pyttsx3
import threading
from queue import Queue

class VoiceFeedback:
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self.is_initialized = False
        self.speech_queue = Queue()
        self.speech_thread = None

    def initialize(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)

            self.is_initialized = True
            return True
        except Exception as e:
            print(f"语音合成初始化失败: {e}")
            return False

    def speak(self, text, blocking=True):
        if not self.is_initialized:
            self.initialize()

        if not text:
            return

        if blocking:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"语音播放失败: {e}")
        else:
            self.speech_queue.put(text)
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self._speech_worker)
                self.speech_thread.daemon = True
                self.speech_thread.start()

    def _speech_worker(self):
        while not self.speech_queue.empty():
            try:
                text = self.speech_queue.get()
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"语音播放错误: {e}")

    def stop(self):
        if self.engine:
            self.engine.stop()

    def set_rate(self, rate):
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        self.volume = volume
        if self.engine:
            self.engine.setProperty('volume', volume)

    def cleanup(self):
        self.stop()
        self.is_initialized = False
