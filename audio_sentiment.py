import io
import os
import numpy as np
import streamlit as st
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import matplotlib.pyplot as plt
import asyncio

# Set the path to the service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'

# Configure Google Cloud clients
speech_client = speech.SpeechClient()
language_client = language_v1.LanguageServiceClient()


class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(figsize=(10, 2))
        print("Audio Processor Initialized")  # Debug statement

    def recv(self, frame):
        print("Frame received")  # Debug statement
        audio_data = np.array(frame.to_ndarray(format="f32"))
        if audio_data.size == 0:
            print("Received empty frame.")  # Debug statement
        else:
            print("Processing non-empty audio frame.")  # Debug statement

        # Proceed to visualize and analyze if data is present
        self.visualize_audio(audio_data)
        return frame

    def visualize_audio(self, audio_data):
        self.ax.clear()
        self.ax.plot(audio_data, color='blue')
        self.ax.set_title("Real-time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        st.pyplot(self.figure)


def show_audio_sentiment():
    st.title("Audio Sentiment Analysis")
    webrtc_streamer(
        key="audio_processor",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )

if __name__ == '__main__':
    show_audio_sentiment()
