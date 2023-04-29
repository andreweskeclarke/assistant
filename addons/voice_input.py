import numpy as np
import torch
from mycroft.stt import STT
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from customizations.common.log_wrapper import log_start_stop


class HuggingFaceSTTPlugin(STT):
    @log_start_stop
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = Wav2Vec2Processor.from_pretrained(
            "facebook/wav2vec2-large-960h-lv60-self"
        )
        self.model = Wav2Vec2ForCTC.from_pretrained(
            "facebook/wav2vec2-large-960h-lv60-self"
        )

    @log_start_stop
    def execute(self, audio, language=None):
        # Custom processing and predicting for facebook/wave2vec2...
        sound_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(
            np.float64
        )
        input_values = self.processor(
            sound_data, return_tensors="pt", padding="longest"
        ).input_values
        logits = self.model(input_values).logits
        predicted_ids = torch.Tensor.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]
        return transcription
