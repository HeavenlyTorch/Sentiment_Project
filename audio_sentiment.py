import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import logging

# Environment variables and constants
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'
SPEECH_CLIENT = speech.SpeechClient()
LANGUAGE_CLIENT = language_v1.LanguageServiceClient()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.buffer = []

    def recv_queued(self, frames):
        frame_list = [np.array(frame.to_ndarray(format="f32")) for frame in frames]
        if frame_list:
            self.buffer.extend(frame_list)  # Buffering the audio data

    def process_buffer(self):
        if self.buffer:
            audio_data = np.concatenate(self.buffer)
            self.visualize_audio(audio_data)
            self.process_audio(audio_data)
            self.buffer = []  # Clear buffer after processing

    def visualize_audio(self, audio_data):
        plt.figure(figsize=(10, 2))
        plt.plot(audio_data, color='blue')
        plt.title("Real-time Audio Waveform")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.grid(True)
        st.pyplot(plt)

    def process_audio(self, audio_data):
        # Convert audio to text
        audio = speech.RecognitionAudio(content=audio_data.tobytes())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US")
        response = SPEECH_CLIENT.recognize(request={"audio": audio, "config": config})
        text = ' '.join(result.alternatives[0].transcript for result in response.results)

        # Analyze sentiment
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = LANGUAGE_CLIENT.analyze_sentiment(document=document).document_sentiment
        st.write(f"Sentiment Score: {sentiment.score}, Magnitude: {sentiment.magnitude}")


def show_audio_sentiment():
    st.title("Audio Sentiment Analysis")
    try:
        audio_processor = AudioProcessor()
        ctx = webrtc_streamer(key="audio_processor",
                              mode=WebRtcMode.SENDRECV,
                              audio_processor_factory=lambda: audio_processor,
                              media_stream_constraints={"video": False, "audio": True},
                              rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
        if st.button("Analyze Buffered Audio"):
            audio_processor.process_buffer()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logging.exception("Caught an error in the main processing loop")


if __name__ == '__main__':
    show_audio_sentiment()
