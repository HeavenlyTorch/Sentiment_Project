import streamlit as st
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import os
import tempfile

# Global settings
fs = 44100  # Sample rate
duration = 5  # seconds


def record_audio():
    st.write("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float64')
    sd.wait()  # Wait until recording is finished
    st.write("Recording stopped.")
    return audio


def plot_waveform(audio):
    plt.figure(figsize=(10, 4))
    plt.plot(np.linspace(0, duration, len(audio)), audio)
    plt.title('Live Audio Waveform')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    st.pyplot(plt)


def save_audio(audio):
    # Save the recorded audio to a temporary file to be used by the audio player
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sd.write(tfile.name, audio, fs)
    return tfile.name


def main():
    st.title('Live Audio Recording and Analysis')

    if st.button('Record Audio'):
        audio_data = record_audio()
        plot_waveform(audio_data)
        audio_file = save_audio(audio_data)
        st.audio(audio_file)

    # Add more analysis functionalities here
    # For example, feature extraction, sentiment analysis, etc.


if __name__ == "__main__":
    main()
