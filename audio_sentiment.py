import asyncio
import json
import streamlit as st
import websockets
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import requests
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import pybase64
import assemblyai as aai

aai.settings.api_key = "62525f1b2bc7436baecf9085bc076f53"

# Load animation function
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Audio processor for handling audio frames received via WebRTC
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
    def recv(self, frame):
        audio = np.array(frame.to_ndarray(format="f32"))
        self.visualize_audio(audio)
        return frame

    def visualize_audio(self, audio_data):
        # Clear the previous plot to avoid memory leak and redundant drawings
        plt.clf()

        # Create a new figure for the plot
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(audio_data, color='blue')
        ax.set_title("Real time Audio Waveform")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")

        # Ensure the plot updates in the Streamlit interface
        st.pyplot(fig)

    async def connect_websocket(self):
        self.ws = await websockets.connect(
            self.websocket_url,
            extra_headers=(("Authorization", self.auth_key),),
            ping_interval=5,
            ping_timeout=20
        )

    async def send_audio_data(self, audio_data):
        if self.ws is not None:
            try:
                await self.ws.send(json.dumps({"audio_data": audio_data}))
            except websockets.exceptions.ConnectionClosed:
                await self.connect_websocket()  # Reconnect if connection is closed

    async def recv(self, frame):
        print("Frame received")  # Debug print
        audio_data = np.array(frame.to_ndarray(format="f32"))
        pybase64_encoded_audio = pybase64.b64encode(audio_data.tobytes()).decode("utf-8")
        await self.send_audio_data(pybase64_encoded_audio)
        return frame


# Setup for WebRTC streamer
def setup_webrtc():
    webrtc_ctx = webrtc_streamer(
        key="audio_processor",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=lambda: AudioProcessor("wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000", aai.settings.api_key),
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True}
    )
    return webrtc_ctx


# Streamlit UI setup
def show_audio_sentiment():
    st.title("Real-time Voice Waveform")
    st.write("This app captures your voice and displays the waveform in real-time.")

    # Define the audio processor factory without parameters
    webrtc_ctx = webrtc_streamer(
        key="audio",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=AudioProcessor,  # Pass class directly without instantiation
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )

if __name__ == "__main__":
    show_audio_sentiment()