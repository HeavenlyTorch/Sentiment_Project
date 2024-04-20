import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os

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
    # You would integrate your sentiment analysis model here
    sentiment_score = np.random.rand()  # Random sentiment score
    return sentiment_score

def show_audio_sentiment():
    st.title("Audio Sentiment Analysis App")

    # Single audio file uploader
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    if uploaded_file is not None:
        data, rate = load_audio(uploaded_file)
        st.audio(uploaded_file)
        plot_waveform(data, rate)
        sentiment = analyze_sentiment(data)
        st.write(f"Sentiment score: {sentiment:.2f}")

    # Multiple audio files processing
    uploaded_files = st.file_uploader("Upload multiple audio files for dataset analysis", accept_multiple_files=True)
    if uploaded_files:
        sentiment_scores = []
        for audio_file in uploaded_files:
            data, rate = load_audio(audio_file)
            sentiment = analyze_sentiment(data)
            sentiment_scores.append(sentiment)

        # Display graph of sentiment scores
        st.write("Sentiment Analysis for Dataset:")
        fig, ax = plt.subplots()
        ax.plot(sentiment_scores, marker='o')
        ax.set_title('Sentiment Analysis of Audio Files')
        ax.set_xlabel('File Index')
        ax.set_ylabel('Sentiment Score')
        st.pyplot(fig)

if __name__ == '__main__':
    main()
