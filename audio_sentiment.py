import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import pandas as pd
import os
from glob import glob

# Function to display the waveform of an audio file
def show_audio_function(audio_file):
    # Load the audio file
    audio, sr = librosa.load(audio_file, sr=None)

    # Display waveform
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(audio, sr=sr)
    plt.title(f'Waveform of {audio_file}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    st.pyplot(plt)

    # Display audio file (interactive player)
    st.audio(audio_file)

# Streamlit interface setup
def main():
    st.title('Audio Sentiment Analysis App')

    # Single audio file analysis
    st.header('Analyze Single Audio File')
    audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'aac'])
    if audio_file is not None:
        show_audio_function(audio_file)

    # Batch audio analysis
    st.header('Batch Audio Analysis')
    uploaded_files = st.file_uploader("Upload Multiple Audio Files", type=['wav', 'mp3', 'aac'], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            show_audio_function(file)

if __name__ == "__main__":
    main()
