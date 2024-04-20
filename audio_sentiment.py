import streamlit as st
from audio_recorder_streamlit import audio_recorder
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
import base64
import io

def load_audio(audio_file):
    """Load audio file with librosa."""
    data, sample_rate = librosa.load(audio_file, sr=None)
    return data, sample_rate

def plot_waveform(data, sample_rate):
    """Plot waveform of the audio data."""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(data, sr=sample_rate, alpha=0.5)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    st.pyplot(plt)

def analyze_sentiment(audio_data):
    """Placeholder function to analyze sentiment."""
    sentiment_score = np.random.rand()  # Random sentiment score
    return sentiment_score

def show_audio_sentiment():
    st.title("Audio Sentiment Analysis App")

    # Audio recorder
    st.subheader("Record your audio")
    audio_data = st.audio(recording_time=300, record=True, display_streamlit_player=True)

    if audio_data:
        bytes_data = base64.b64decode(audio_data.split(',')[1])
        audio_buffer = io.BytesIO(bytes_data)
        data, rate = librosa.load(audio_buffer, sr=22050)  # Make sure to set the appropriate sample rate
        st.audio(bytes_data)
        plot_waveform(data, rate)
        sentiment = analyze_sentiment(data)
        st.write(f"Sentiment score: {sentiment:.2f}")

    # Single audio file uploader
    st.subheader("Or upload an audio file")
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "ogg"])
    if uploaded_file is not None:
        data, rate = load_audio(uploaded_file)
        st.audio(uploaded_file)
        plot_waveform(data, rate)
        sentiment = analyze_sentiment(data)
        st.write(f"Sentiment score: {sentiment:.2f}")

if __name__ == '__main__':
    show_audio_sentiment()
