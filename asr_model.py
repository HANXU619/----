import torch
import numpy as np
import warnings
import os
warnings.filterwarnings('ignore')

class TransformerASR:
    def __init__(self, model_name="small"):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False

    def load_model(self):
        try:
            print(f"正在加载 Whisper {self.model_name} 模型...")
            print(f"使用设备: {self.device}")

            from transformers import WhisperProcessor, WhisperForConditionalGeneration

            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
            model_base = f"models--openai--whisper-{self.model_name}"
            snapshots_dir = os.path.join(cache_dir, model_base, "snapshots")

            if os.path.exists(snapshots_dir):
                for root, dirs, files in os.walk(snapshots_dir):
                    if os.path.exists(os.path.join(root, "model.safetensors")):
                        print(f"✓ 找到本地模型: {root}")
                        try:
                            self.processor = WhisperProcessor.from_pretrained(root, local_files_only=True)
                            self.model = WhisperForConditionalGeneration.from_pretrained(root, local_files_only=True)
                        except:
                            self.processor = WhisperProcessor.from_pretrained(root)
                            self.model = WhisperForConditionalGeneration.from_pretrained(root)
                        break
                else:
                    print("本地模型未找到，从网络加载...")
                    self.processor = WhisperProcessor.from_pretrained(f"openai/whisper-{self.model_name}")
                    self.model = WhisperForConditionalGeneration.from_pretrained(f"openai/whisper-{self.model_name}")
            else:
                print("本地模型未找到，从网络加载...")
                self.processor = WhisperProcessor.from_pretrained(f"openai/whisper-{self.model_name}")
                self.model = WhisperForConditionalGeneration.from_pretrained(f"openai/whisper-{self.model_name}")

            self.model = self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            print("Whisper 模型加载成功！")
            return True

        except Exception as e:
            print(f"模型加载失败: {e}")
            self.is_loaded = False
            return False

    def transcribe(self, audio_data, sample_rate=16000):
        if not self.is_loaded:
            print("模型未加载，尝试加载...")
            if not self.load_model():
                return None

        try:
            return self._whisper_transcribe(audio_data, sample_rate)
        except Exception as e:
            print(f"转录错误: {e}")
            return None

    def _whisper_transcribe(self, audio_data, sample_rate=16000):
        if isinstance(audio_data, np.ndarray):
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            if audio_data.max() > 1.0:
                audio_data = audio_data / 32768.0

        input_features = self.processor(
            audio_data,
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).input_features.to(self.device)

        try:
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(language="chinese", task="transcribe")
            predicted_ids = self.model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        except:
            predicted_ids = self.model.generate(input_features)

        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    def transcribe_from_file(self, audio_path):
        import librosa
        try:
            audio, sr = librosa.load(audio_path, sr=16000)
            return self.transcribe(audio, sr)
        except Exception as e:
            print(f"文件转录错误: {e}")
            return None
