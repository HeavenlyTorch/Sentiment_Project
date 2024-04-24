import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# Environment variables and constants
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'
SPEECH_CLIENT = speech.SpeechClient()
LANGUAGE_CLIENT = language_v1.LanguageServiceClient()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(figsize=(10, 2))
        self.init_plot()

    def init_plot(self):
        self.ax.set_title("Real-time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")

    def recv_queued(self, frames):
        frame_list = [np.array(frame.to_ndarray(format="f32")) for frame in frames]
        for audio_data in frame_list:
            self.update_plot(audio_data)
            self.analyze_and_display_sentiment(audio_data)
        return frames

    def update_plot(self, audio_data):
        self.ax.clear()
        self.ax.plot(audio_data, color='blue')
        st.pyplot(self.figure)

    def analyze_and_display_sentiment(self, audio_data):
        text = self.speech_to_text(audio_data)
        sentiment = self.analyze_sentiment(text)
        st.write(f"Sentiment Score: {sentiment.score}, Magnitude: {sentiment.magnitude}")

    def speech_to_text(self, audio_data):
        audio = speech.RecognitionAudio(content=audio_data.tobytes())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US")
        response = SPEECH_CLIENT.recognize(request={"audio": audio, "config": config})
        return ' '.join(result.alternatives[0].transcript for result in response.results)

    def analyze_sentiment(self, text):
        response = LANGUAGE_CLIENT.analyze_sentiment(request={"document": {"content": text, "type": "PLAIN_TEXT"}})
        return response.document_sentiment

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