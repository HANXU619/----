import time
import logging
import threading
from asr_model import TransformerASR
from audio_capture import AudioCapture
from command_parser import CommandParser
from computer_controller import ComputerController
from voice_feedback import VoiceFeedback

class VoiceAssistant:
    def __init__(self, config=None):
        self.config = config
        self.logger = self._setup_logger()

        self.asr_model = TransformerASR()
        self.audio_capture = AudioCapture()
        self.command_parser = CommandParser()
        self.controller = ComputerController()
        self.voice_feedback = VoiceFeedback()

        self.is_initialized = False
        self.is_listening = False
        self.is_awake = False
        self.is_processing = False

        self.wake_words = [
            "助手",
            "小助手",
            "小爱",
            "小爱同学",
            "天猫精灵",
            "嘿助手",
            "hey assistant",
            "assistant",
            "hey siri"
        ]

        self.callbacks = {
            'on_transcription': None,
            'on_command': None,
            'on_result': None,
            'on_error': None,
            'on_wake': None,
            'on_awake_mode': None
        }

    def _setup_logger(self):
        logger = logging.getLogger('VoiceAssistant')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def initialize(self):
        try:
            self.logger.info("正在初始化语音助手...")

            self.logger.info("正在加载语音识别模型...")
            asr_loaded = self.asr_model.load_model()
            if not asr_loaded:
                self.logger.warning("Transformer模型加载失败")

            self.logger.info("正在初始化语音合成...")
            self.voice_feedback.initialize()

            self.is_initialized = True
            self.logger.info("语音助手初始化完成！")
            self.logger.info(f"唤醒词: {self.wake_words[0]}")

            return True

        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False

    def set_callback(self, event, callback):
        if event in self.callbacks:
            self.callbacks[event] = callback

    def process_audio(self, audio_data):
        try:
            text = self.asr_model.transcribe(audio_data)

            if text is None:
                return None

            text = text.strip()
            if not text:
                return None

            self.logger.info(f"识别结果: {text}")

            if self.callbacks['on_transcription']:
                self.callbacks['on_transcription'](text)

            return text

        except Exception as e:
            self.logger.error(f"语音处理错误: {e}")
            if self.callbacks['on_error']:
                self.callbacks['on_error'](str(e))
            return None

    def process_command(self, text):
        try:
            if not text:
                return {
                    'success': False,
                    'message': '未识别到语音或文本'
                }

            self.logger.info(f"处理命令: {text}")

            parsed = self.command_parser.parse(text)

            if not parsed:
                return {
                    'success': False,
                    'message': '无法解析命令'
                }

            if self.callbacks['on_command']:
                self.callbacks['on_command'](parsed)

            valid, msg = self.command_parser.validate_command(parsed)
            if not valid:
                return {
                    'success': False,
                    'message': msg
                }

            result = self.controller.execute_command(parsed)

            if result['success']:
                self.logger.info(f"命令执行成功: {result['message']}")
            else:
                self.logger.warning(f"命令执行失败: {result['message']}")

            response = self.command_parser.generate_response(parsed, result['success'])

            if self.callbacks['on_result']:
                self.callbacks['on_result'](result, response)

            return {
                'success': result['success'],
                'message': result['message'],
                'response': response
            }

        except Exception as e:
            self.logger.error(f"命令处理错误: {e}")
            return {
                'success': False,
                'message': f"处理错误: {str(e)}"
            }

    def voice_command(self, audio_data):
        text = self.process_audio(audio_data)

        if not text:
            return None

        result = self.process_command(text)

        if result and result['success']:
            response = result.get('response', result['message'])
            self.speak(response)

        return result

    def check_wake_word(self, text):
        if not text:
            return False
        
        text_lower = text.lower()
        
        if '住手' in text or '猪手' in text:
            return False
        
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                return True
        
        return False

    def start_listening(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.logger.info("开始持续监听...")

        def audio_callback(audio_data):
            try:
                if audio_data is None or len(audio_data) == 0:
                    return
                    
                if self.is_processing:
                    return
                    
                self.is_processing = True
                try:
                    text = self.process_audio(audio_data)
                    
                    if text:
                        self.logger.info(f"识别结果: {text}")
                        
                        if self.check_wake_word(text):
                            self.is_awake = True
                            self.logger.info("检测到唤醒词！")
                            
                            if self.callbacks['on_wake']:
                                self.callbacks['on_wake']()
                            
                            self.speak("我在")
                            
                            if self.callbacks['on_awake_mode']:
                                self.callbacks['on_awake_mode'](True)
                            
                            self.logger.info("请说出您的命令...")
                        elif self.is_awake:
                            self.logger.info(f"收到命令: {text}")
                            result = self.voice_command(audio_data)
                            
                            if self.callbacks['on_result']:
                                if result:
                                    self.callbacks['on_result'](result, result.get('response', ''))
                                else:
                                    self.callbacks['on_result']({'success': False, 'message': '命令执行失败'}, '')
                            
                            self.is_awake = False
                            
                            if self.callbacks['on_awake_mode']:
                                self.callbacks['on_awake_mode'](False)
                            
                            self.logger.info("命令执行完成，继续监听...")
                        else:
                            self.logger.debug(f"未识别到唤醒词，继续监听: {text}")
                finally:
                    self.is_processing = False
                            
            except Exception as e:
                self.logger.error(f"识别错误: {e}")
                self.is_processing = False
                import traceback
                self.logger.error(traceback.format_exc())

        try:
            self.audio_capture.start_listening(callback=audio_callback)

            def monitor_thread():
                while self.is_listening:
                    time.sleep(2)
                    if self.is_listening and not self.audio_capture.is_listening:
                        self.logger.warning("检测到监听意外停止，正在重启...")
                        time.sleep(0.5)
                        if self.is_listening:
                            try:
                                self.audio_capture.start_listening(callback=audio_callback)
                                self.logger.info("监听已重启")
                            except Exception as e:
                                self.logger.error(f"重启监听失败: {e}")

            threading.Thread(target=monitor_thread, daemon=True).start()

        except Exception as e:
            self.logger.error(f"监听失败: {e}")
            self.is_listening = False
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f'监听失败: {e}')

    def stop_listening(self):
        if not self.is_listening:
            return

        self.is_listening = False
        self.is_awake = False
        self.audio_capture.stop_listening()
        self.logger.info("停止监听")

    def speak(self, text, blocking=True):
        try:
            self.voice_feedback.speak(text, blocking)
        except Exception as e:
            self.logger.error(f"语音反馈失败: {e}")

    def listen_once(self, duration=5):
        self.logger.info(f"录音 {duration} 秒...")

        audio_data = self.audio_capture.record_audio(duration)

        if audio_data is None:
            return None

        return self.voice_command(audio_data)

    def cleanup(self):
        self.logger.info("正在清理资源...")

        self.stop_listening()
        self.audio_capture.cleanup()
        self.voice_feedback.cleanup()

        self.logger.info("清理完成")

    def get_status(self):
        return {
            'is_initialized': self.is_initialized,
            'is_listening': self.is_listening,
            'is_awake': self.is_awake,
            'model_loaded': self.asr_model.is_loaded
        }

    def test_components(self):
        results = {}

        results['asr_model'] = self.asr_model.is_loaded

        try:
            devices = self.audio_capture.list_audio_devices()
            results['audio_devices'] = len(devices) > 0
            results['device_count'] = len(devices)
        except:
            results['audio_devices'] = False

        results['command_parser'] = True
        results['computer_controller'] = True
        results['voice_feedback'] = self.voice_feedback.is_initialized

        return results
