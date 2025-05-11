import sounddevice as sd
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Load Whisper model and processor
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
processor = WhisperProcessor.from_pretrained("openai/whisper-base")

# Recording settings
sample_rate = 16000  # Whisper expects 16kHz audio
chunk_duration = 10   # seconds per recording chunk

def normalize_audio(audio):
    """Normalize audio to prevent clipping."""
    return audio / np.max(np.abs(audio))

def record_audio_chunk():
    """Record a short chunk of audio from the microphone."""
    print("🎙️ Listening...")
    audio_chunk = sd.rec(int(chunk_duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(audio_chunk)

def transcribe_audio(audio):
    """Transcribe audio using Whisper."""
    audio = normalize_audio(audio)
    input_features = processor(audio, sampling_rate=sample_rate, return_tensors="pt").input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcription

def real_time_transcription():
    """Continuously record and transcribe audio."""
    print("🔁 Real-time transcription started. Press Ctrl+C to stop.")
    try:
        while True:
            audio_chunk = record_audio_chunk()
            transcription = transcribe_audio(audio_chunk)
            print("📝", transcription)
    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped.")

if __name__ == "__main__":
    real_time_transcription()
