import streamlit as st
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import tempfile

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

def record_audio():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index= 1)

    st.write("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    st.write("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    return b''.join(frames)


def plot_waveform(audio_data):
    # Convert byte data to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    plt.figure(figsize=(10, 4))
    plt.plot(audio_array)
    plt.title('Live Audio Waveform')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
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


def show_audio_sentiment():
    st.title('Live Audio Recording and Analysis')

    if st.button('Record Audio'):
        audio_data = record_audio(1)  # Pass the device index to the recording function
        plot_waveform(audio_data)
        audio_file_path = save_audio(audio_data)
        st.audio(audio_file_path)


if __name__ == "__main__":
    show_audio_sentiment()
