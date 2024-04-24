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
        self.buffer = []

    def recv_queued(self, frames):
        frame_list = [np.array(frame.to_ndarray(format="f32")) for frame in frames]
        self.buffer.extend(frame_list)
        return frames

def process_audio():
    if 'audio_processor' in st.session_state and st.session_state.audio_processor.buffer:
        audio_data = np.concatenate(st.session_state.audio_processor.buffer)
        st.session_state.audio_processor.buffer = []

        # Visualize audio waveform
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(audio_data, color='blue')
        ax.set_title("Real-time Audio Waveform")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)

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
    st.session_state.audio_processor = AudioProcessor()
    webrtc_streamer(key="audio_processor",
                    mode=WebRtcMode.SENDRECV,
                    audio_processor_factory=lambda: st.session_state.audio_processor,
                    media_stream_constraints={"video": False, "audio": True},
                    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    st.button("Process Audio", on_click=process_audio)

if __name__ == '__main__':
    show_audio_sentiment()
