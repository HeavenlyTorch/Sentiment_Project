import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import io
from audio_recorder_streamlit import audio_recorder

def load_audio_from_bytes(audio_bytes, sample_rate=22050):
    """Load audio data from bytes."""
    audio_buffer = io.BytesIO(audio_bytes)
    data, sr = librosa.load(audio_buffer, sr=sample_rate)
    return data, sr

def plot_waveform(data, sample_rate):
    """Plot waveform of the audio data."""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(data, sr=sample_rate, alpha=0.5)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    st.pyplot(plt)
    plt.show()

def analyze_sentiment(audio_data):
    """Placeholder function to analyze sentiment."""
    sentiment_score = np.random.rand()  # Random sentiment score
    return sentiment_score

def show_audio_sentiment():
    st.title("Audio Sentiment Analysis App")

    # Assuming audio_recorder returns a bytes object directly or a dictionary with the audio as a blob
    audio_data = audio_recorder(key="recorder")  # This function call is correct if audio_recorder returns the audio data directly

    if audio_data:
        # Check if audio_data is a bytes-like object or a dictionary
        if isinstance(audio_data, dict):
            # If it's a dictionary, extract the blob if it exists
            audio_bytes = audio_data.get('blob')  # Ensure 'blob' is the correct key
        else:
            # If it's not a dictionary, assume it's the bytes directly
            audio_bytes = audio_data

        if audio_bytes:
            data, rate = load_audio_from_bytes(audio_bytes)
            st.audio(audio_bytes, format='audio/wav')
            plot_waveform(data, rate)
            sentiment = analyze_sentiment(data)
            st.write(f"Sentiment score: {sentiment:.2f}")

if __name__ == '__main__':
    show_audio_sentiment()
