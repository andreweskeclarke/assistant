from __future__ import annotations

import concurrent.futures
import logging
import os
import pathlib
import pickle
import random
import re
import shutil
import subprocess
import uuid

import azure.cognitiveservices.speech as speechsdk
import soundfile as sf
import torch
import torch.nn.functional as F
import torchaudio
import torchaudio.transforms as T

# from datasets import load_dataset
from pydub.playback import get_player_name
from speechbrain.pretrained import EncoderClassifier
from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor

from assistant.message import Message
from assistant.output import Output

LOG = logging.getLogger(__name__)

CACHED_EMBEDDINGS = pathlib.Path("/home/andrew/tmp/embeddings.pkl")


class HuggingFaceTTS:
    def __init__(self):
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-xvect-voxceleb"
        )
        # self.embeddings = sum(
        #     [
        #         self._get_embeddings(
        #             "/home/andrew/data/voice/andrew_samples/harvard_sentences_1.wav"
        #         ),
        #         self._get_embeddings(
        #             "/home/andrew/data/voice/andrew_samples/harvard_sentences_2.wav"
        #         ),
        #         self._get_embeddings(
        #             "/home/andrew/data/voice/andrew_samples/harvard_sentences_3.wav"
        #         ),
        #     ]
        # )
        # self.embeddings = torch.Tensor(
        #     load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")[7306][
        #         "xvector"
        #     ]
        # ).unsqueeze(0)
        # pickle.dump(self.embeddings, CACHED_EMBEDDINGS.open("wb"))
        self.embeddings = pickle.load(CACHED_EMBEDDINGS.open("rb"))

    def _get_embeddings(self, filename):
        signal, rate = torchaudio.load(filename)  # pylint: disable=no-member
        if rate != 16000:
            signal = T.Resample(rate, 16000)(signal)
        signal = torch.Tensor.mean(signal, dim=0, keepdim=True)
        with torch.no_grad():
            embeddings = self.classifier.encode_batch(signal)
            embeddings = F.normalize(embeddings, dim=2)[0]
        return embeddings

    def run(self, phrase: str, logger: logging.Logger) -> str:
        wav_file = pathlib.Path(f"/tmp/assistant_output.{uuid.uuid4()}.wav")
        logger.info("Running TTS to %s for '%s'", wav_file, phrase)

        # Custom processing and predicting for microsoft/sp[eecht5_tts...
        inputs = self.processor(text=phrase, return_tensors="pt")
        speech = self.model.generate_speech(
            inputs["input_ids"], self.embeddings, vocoder=self.vocoder
        )
        speech = (speech.numpy() * (2**15 - 1)).astype("<h")
        sf.write(wav_file, speech, samplerate=16000)
        return wav_file


class AzureTTS:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("AZURE_SPEECH_KEY"),
            region=os.environ.get("AZURE_SPEECH_REGION"),
        )
        self.speech_config.speech_synthesis_voice_name = "en-AU-KimNeural"
        self.output_file = pathlib.Path(f"/tmp/azuretts.{uuid.uuid4()}.wav")
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=speechsdk.audio.AudioOutputConfig(
                filename=str(self.output_file)
            ),
        )

    def run(self, phrase: str, logger: logging.Logger) -> str:
        wav_file = pathlib.Path(f"/tmp/assistant_output.{uuid.uuid4()}.wav")
        logger.info("TTS '%s' (%s)", phrase, wav_file)
        result = self.speech_synthesizer.speak_text(phrase)
        shutil.copy(self.output_file, wav_file)
        self.output_file.open("wb").close()
        finished_latency = int(
            result.properties.get_property(
                speechsdk.PropertyId.SpeechServiceResponse_SynthesisFinishLatencyMs
            )
        )
        logger.info("Azure TTS Time: %fs", finished_latency / 1000.0)
        return wav_file


LOCAL_TTS = None


def init_tts():
    global LOCAL_TTS  # pylint: disable=global-statement
    # LOCAL_TTS = HuggingFaceTTS()
    LOCAL_TTS = AzureTTS()


def run_tts(phrase: str, logger: logging.Logger) -> str:
    assert LOCAL_TTS is not None, "Call init_tts() first"
    return LOCAL_TTS.run(phrase, logger)


def startup_message():
    messages = [
        "Ready for action Ryder sir!",
        "Green means go!",
        "Chase is on the case!",
        "I'm fired up!",
    ]
    return random.choice(messages)


class SpeakOutput(Output):
    def __init__(self, connection):
        super().__init__(connection)
        self.pool_executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=1, initializer=init_tts
        )
        self.play(self.pool_executor.submit(run_tts, startup_message(), LOG).result())

    async def handle_message(self, msg: Message) -> None:
        phrases = list(
            x.strip() for x in re.split(r"([^\n?!]*[\n?!][^d])", msg.text) if x.strip()
        )
        wav_files_futures = map(
            lambda p: self.pool_executor.submit(run_tts, p, LOG),
            phrases,
        )
        for wav_file in wav_files_futures:
            self.play(wav_file.result())

    def play(self, wav_file: pathlib.Path):
        subprocess.call(
            [
                get_player_name(),
                "-loglevel",
                "quiet",
                "-nodisp",
                "-autoexit",
                "-hide_banner",
                str(wav_file),
            ]
        )
