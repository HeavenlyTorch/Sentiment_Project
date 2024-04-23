import asyncio
import json
import streamlit as st
import websockets
from streamlit_lottie import st_lottie
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
    def __init__(self, websocket_url, auth_key):
        self.ws = None
        self.websocket_url = websocket_url
        self.auth_key = auth_key

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
    st.title('Live audio sentiment')
    voice_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_owkzfxim.json")

    if voice_animation:
        st_lottie(voice_animation, height=200)

    webrtc_ctx = setup_webrtc()
    if webrtc_ctx.state.playing:
        st.text("Listening...")
    else:
        st.text("Click start above to start listening.")


# Display the app
if __name__ == "__main__":
    show_audio_sentiment()
