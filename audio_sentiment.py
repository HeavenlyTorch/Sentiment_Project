import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import logging
from aioice import ice


async def show_audio_sentiment():
    st.title("WebRTC Test")
    connection = ice.Connection(ice_controlling=True)
    try:
        await connection.gather_candidates()
    except Exception as e:
        print(f"Error gathering ICE candidates: {e}")
    finally:
        await connection.close()


if __name__ == '__main__':
    show_audio_sentiment()
