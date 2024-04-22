import asyncio
import base64
import json
import pyaudio
import streamlit as st
import websockets
from streamlit_lottie import st_lottie
import requests
from streamlit_webrtc import WebRtcMode, webrtc_streamer

if 'run' not in st.session_state:
    st.session_state['run'] = False

# Audio configuration
Frames_per_buffer = 3200
Format = pyaudio.paInt16
Channels = 1
Rate = 16000
p = pyaudio.PyAudio()

# Open the default microphone stream
stream = p.open(
    format=Format,
    channels=Channels,
    rate=Rate,
    input=True,
    frames_per_buffer=Frames_per_buffer,
    input_device_index=1
)

# WebRTC streamer configuration
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": False, "audio": True},
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load animation
voice_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_owkzfxim.json")

def start_listening():
    st.session_state['run'] = True
    st_lottie(voice_animation, height=200)

def stop_listening():
    st.session_state['run'] = False

# WebSocket connection function
async def send_receive(endpoint_url):
    print(f'Connecting websocket to url {endpoint_url}')
    async with websockets.connect(
        endpoint_url,
        extra_headers=(("Authorization", st.secrets["key"]),),
        ping_interval=5,
        ping_timeout=20
    ) as ws:
        print("Connected, sending and receiving messages...")

        async def send():
            while st.session_state['run']:
                try:
                    data = stream.read(Frames_per_buffer, exception_on_overflow=False)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})
                    await ws.send(json_data)
                except Exception as e:
                    print(f"Error sending data: {e}")
                    break

        async def receive():
            while st.session_state['run']:
                try:
                    result_str = await ws.recv()
                    if json.loads(result_str)['message_type'] == 'FinalTranscript':
                        st.markdown(json.loads(result_str)['text'])
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    break

        send_task = asyncio.create_task(send())
        receive_task = asyncio.create_task(receive())
        await asyncio.gather(send_task, receive_task)

def show_audio_sentiment():
    st.title('Real-time transcription from your microphone')
    col1, col2 = st.columns(2)
    col1.button('Start Listening', on_click=start_listening)
    col2.button('Stop Listening', on_click=stop_listening)

    # Use Streamlit's run in thread for async functions
    if st.session_state['run']:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_receive("wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"))
        loop.close()

# Display the app
show_audio_sentiment()
