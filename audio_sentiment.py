import io
import numpy as np
import streamlit as st
from google.cloud import speech, language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import matplotlib.pyplot as plt

# Configure Google Cloud clients
speech_client = speech.SpeechClient()
language_client = language_v1.LanguageServiceClient()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(figsize=(10, 2))
        print("AudioProcessor initialized")  # Debug statement

    def recv(self, frame):
        print("Frame received")  # Debug statement
        audio_data = np.array(frame.to_ndarray(format="f32"))
        if audio_data.size == 0:
            print("No audio data received")  # Debug statement
            return frame
        print("Processing audio data")  # Debug statement

        # Visualization
        self.ax.clear()
        self.ax.plot(audio_data, color='blue')
        self.ax.set_title("Real-time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        st.pyplot(self.figure)

        # Convert audio to appropriate format (16-bit PCM)
        audio_data = (audio_data * 32767).astype(np.int16).tobytes()
        audio_buffer = io.BytesIO(audio_data)

        # Prepare request for Speech-to-Text
        audio = speech.RecognitionAudio(content=audio_buffer.getvalue())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )

        # Perform speech recognition
        response = speech_client.recognize(config=config, audio=audio)
        if response.results:
            transcript = response.results[0].alternatives[0].transcript

            # Perform sentiment analysis on the transcript
            document = language_v1.Document(content=transcript, type_=language_v1.Document.Type.PLAIN_TEXT)
            sentiment_response = language_client.analyze_sentiment(request={'document': document})
            sentiment_score = sentiment_response.document_sentiment.score
            sentiment_magnitude = sentiment_response.document_sentiment.magnitude

            st.write("Transcript:", transcript)
            st.write("Sentiment Score:", sentiment_score)
            st.write("Sentiment Magnitude:", sentiment_magnitude)

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
