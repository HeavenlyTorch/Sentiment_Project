import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import logging


def show_audio_sentiment():
    st.title("WebRTC Test")
    webrtc_streamer(key="test", mode=WebRtcMode.SENDRECV)


if __name__ == '__main__':
    show_audio_sentiment()
