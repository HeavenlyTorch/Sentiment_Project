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

# Set up the Streamlit app
st.set_page_config(page_title="Audio Sentiment Analysis", page_icon=":headphones:", layout="wide")
st.title("Audio Sentiment Analysis")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(figsize=(10, 2))
        self.sentiment_score = 0
        self.sentiment_magnitude = 0
        print("Audio Processor Initialized")  # Debug statement

    def recv_queued(self, frames):
        print("Frames received")  # Debug statement
        frame_list = [np.array(frame.to_ndarray(format="f32")) for frame in frames]
        if len(frame_list) == 0:
            print("Received empty frames.")  # Debug statement
        else:
            print("Processing non-empty audio frames.")  # Debug statement

        # Proceed to visualize and analyze if data is present
        for audio_data in frame_list:
            self.visualize_audio(audio_data)
            self.analyze_sentiment(audio_data)
        return frames

    def visualize_audio(self, audio_data):
        self.ax.clear()
        self.ax.plot(audio_data, color='blue')
        self.ax.set_title("Real-time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        st.pyplot(self.figure)

    def analyze_sentiment(self, audio_data):
        # Convert the audio data to text using the Google Cloud Speech API
        text = self.speech_to_text(audio_data)

        # Perform sentiment analysis on the text using the Google Cloud Natural Language API
        sentiment_score, sentiment_magnitude = self.language_client.analyze_sentiment(request={"document": {"content": text, "type": "PLAIN_TEXT"}})
        return sentiment_score.value, sentiment_magnitude.value

    def speech_to_text(self, audio_data):
        # Configure the Google Cloud Speech API request
        audio = speech.RecognitionAudio(content=audio_data.tobytes())
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=16000, language_code="en-US")

        # Perform speech-to-text conversion
        response = speech_client.recognize(request={"audio": audio, "config": config})

        # Extract the text from the response
        text = ""
        for result in response.results:
            text += result.alternatives.transcript
        return text

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
