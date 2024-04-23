import io
import numpy as np
import streamlit as st
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import matplotlib.pyplot as plt
import asyncio

# Configure Google Cloud clients
speech_client = speech.SpeechClient()
language_client = language_v1.LanguageServiceClient()


class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(figsize=(10, 2))

    def recv(self, frame):
        audio_data = np.array(frame.to_ndarray(format="f32"))

        # Visualization
        self.ax.clear()
        self.ax.plot(audio_data, color='blue')
        self.ax.set_title("Real-time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")

        # Convert audio data to the format needed for Google Speech API (if you're processing it)
        # Convert to text, then sentiment analysis (ensure these are not async or handle them properly if they are)

        # Dummy sentiment values for demonstration
        sentiment_score = 0.5  # Example score
        sentiment_magnitude = 0.1  # Example magnitude

        # Use st.session_state to store data if needed
        st.session_state['last_frame'] = frame
        st.session_state['sentiment_score'] = sentiment_score
        st.session_state['sentiment_magnitude'] = sentiment_magnitude

        # Update UI
        st.write("Sentiment Score:", sentiment_score)
        st.write("Sentiment Magnitude:", sentiment_magnitude)
        st.pyplot(self.figure)

        return frame

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
