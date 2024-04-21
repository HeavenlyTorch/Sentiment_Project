import streamlit as st
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import tempfile
import librosa
from threading import Thread
from queue import Queue

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

def record_audio(queue):
    """Records audio from the default microphone."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    st.write("Recording...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    st.write("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Put the recorded frames as a byte array into the queue
    queue.put(b''.join(frames))

def load_audio(audio_file):
    """Load audio file with librosa."""
    data, sample_rate = librosa.load(audio_file, sr=None)
    return data, sample_rate

def analyze_sentiment(audio_data):
    """Placeholder function to analyze sentiment."""
    # You would integrate your sentiment analysis model here
    sentiment_score = np.random.rand()  # Random sentiment score
    return sentiment_score

def plot_waveform(data, sample_rate):
    """Plots waveform of the recorded audio."""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(data, sr=sample_rate, alpha=0.5)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.show()
    st.pyplot(plt)


def save_audio(audio_data):
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wf = wave.open(tfile.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()
    return tfile.name


def show_audio_sentiment(audio_queue):
    st.title('Live Audio Recording and Analysis')

    if st.button('Record Audio'):
        # Run recording in a thread to avoid blocking
        record_thread = Thread(target=record_audio, args=(audio_queue,))
        record_thread.start()
        record_thread.join()  # Wait for the thread to finish recording
        if not audio_queue.empty():
            audio_data = audio_queue.get()
            plot_waveform(audio_data)
            audio_file_path = save_audio(audio_data)
            st.audio(audio_file_path)

    # Multiple audio files processing
    uploaded_files = st.file_uploader("Upload multiple audio files for dataset analysis",
                                          accept_multiple_files=True)
    if uploaded_files:
        sentiment_scores = []
        for audio_file in uploaded_files:
            data, rate = load_audio(audio_file)
            sentiment = analyze_sentiment(data)
            sentiment_scores.append(sentiment)


if __name__ == "__main__":
    show_audio_sentiment()
