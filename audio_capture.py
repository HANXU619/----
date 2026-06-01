import pyaudio
import numpy as np
import wave
import time
import threading
from queue import Queue

class AudioCapture:
    def __init__(self, chunk_size=1024, sample_rate=16000, channels=1):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = pyaudio.paInt16

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.is_listening = False

        self.audio_queue = Queue()
        self.recording_thread = None

        self.threshold = 1000
        self.silence_duration = 2.0
        self.min_speech_duration = 0.5
        self.max_listen_duration = 10.0

        self.speech_start_time = None
        self.last_speech_time = None
        self.listen_start_time = None

        self.default_device_index = None
        try:
            self.default_device_index = self.audio.get_default_input_device_info()['index']
        except:
            pass

    def list_audio_devices(self):
        device_count = self.audio.get_device_count()
        devices = []

        for i in range(device_count):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels']
                })

        return devices

    def start_stream(self):
        try:
            kwargs = {
                'format': self.format,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'frames_per_buffer': self.chunk_size,
                'start': False
            }
            
            if self.default_device_index is not None:
                kwargs['input_device_index'] = self.default_device_index
            
            self.stream = self.audio.open(**kwargs)
            self.stream.start_stream()
            return True
        except Exception as e:
            print(f"启动音频流失败: {e}")
            return False

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def calculate_volume(self, audio_data):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        return np.abs(audio_array).mean()

    def is_speech(self, volume):
        return volume > self.threshold

    def start_listening(self, callback=None):
        if self.is_listening:
            return

        self.is_listening = True
        self.listen_start_time = time.time()
        self.recording_thread = threading.Thread(
            target=self._listen_loop,
            args=(callback,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_listening(self):
        self.is_listening = False
        if self.recording_thread:
            self.recording_thread.join(timeout=1)

    def _listen_loop(self, callback):
        if not self.start_stream():
            self.is_listening = False
            return

        frames = []
        recording = False
        silence_frames = 0
        speech_frames = 0
        loop_count = 0

        while self.is_listening:
            try:
                loop_count += 1
                if loop_count % 1000 == 0:
                    self.listen_start_time = time.time()

                if not self.stream.is_active():
                    time.sleep(0.01)
                    continue

                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                volume = self.calculate_volume(data)

                if self.is_speech(volume):
                    if not recording:
                        recording = True
                        self.speech_start_time = time.time()

                    frames.append(data)
                    silence_frames = 0
                    speech_frames += 1
                    self.last_speech_time = time.time()

                elif recording:
                    silence_time = time.time() - self.last_speech_time
                    if silence_time > 0.5:
                        silence_frames += 1

                    frames.append(data)

                    if silence_frames > int(self.silence_duration * self.sample_rate / self.chunk_size):
                        if speech_frames * self.chunk_size / self.sample_rate >= self.min_speech_duration:
                            audio_data = self._process_frames(frames)
                            if callback:
                                callback(audio_data)
                        frames = []
                        recording = False
                        silence_frames = 0
                        speech_frames = 0

                time.sleep(0.001)

            except Exception as e:
                print(f"监听循环错误: {e}")
                break

        self.is_listening = False
        self.stop_stream()

    def _process_frames(self, frames):
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32768.0
        return audio_float

    def record_audio(self, duration=None):
        self.is_recording = True
        frames = []

        if not self.start_stream():
            return None

        try:
            if duration:
                num_chunks = int(self.sample_rate / self.chunk_size * duration)
                for _ in range(num_chunks):
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
            else:
                while self.is_recording:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)

        except Exception as e:
            print(f"录音错误: {e}")

        finally:
            self.stop_stream()

        if frames:
            return self._process_frames(frames)
        return None

    def stop_recording(self):
        self.is_recording = False

    def save_audio(self, audio_data, filename):
        try:
            audio_array = (audio_data * 32768).astype(np.int16)

            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_array.tobytes())

            return True
        except Exception as e:
            print(f"保存音频失败: {e}")
            return False

    def cleanup(self):
        self.stop_listening()
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
