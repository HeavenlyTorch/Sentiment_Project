import os
import io
import streamlit as st
from google.cloud import language_v1
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import json
import websockets
import matplotlib.pyplot as plt
from pydub import AudioSegment
import base64
import time

# Set up the Google Cloud Natural Language API client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'
client = language_v1.LanguageServiceClient()

# Audio processor for handling audio frames received via WebRTC
# Define the audio processing function for the WebRTC stream
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()

    def recv(self, frame):
        # Perform sentiment analysis on the audio frame
        sentiment_score, sentiment_magnitude = analyze_audio_sentiment(frame.to_ndarray())

        # Display the sentiment score and magnitude
        st.write("Sentiment Score:", round(sentiment_score, 2))
        st.write("Sentiment Magnitude:", round(sentiment_magnitude, 2))

        # Return the frame to the WebRTC stream
        return frame

    def visualize_audio(self):
        # Create a new figure for the plot
        self.figure = plt.figure(figsize=(10, 2))
        ax = self.figure.add_subplot(111)
        ax.plot(self.audio_data, color='blue')
        ax.set_title("Real time Audio Waveform")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")

    def recv(self, frame):
        # Save the audio data for later use
        self.audio_data = frame.to_ndarray()

        # Perform sentiment analysis on the audio frame
        sentiment_score, sentiment_magnitude = analyze_audio_sentiment(self.audio_data)

        # Update the sentiment score and magnitude
        self.sentiment_score = sentiment_score
        self.sentiment_magnitude = sentiment_magnitude

        # Visualize the audio waveform
        if self.figure is None:
            self.visualize_audio()
        else:
            ax = self.figure.get_axes()[0]
            ax.clear()
            ax.plot(self.audio_data, color='blue')

        # Display the sentiment score and magnitude
        st.write("Sentiment Score:", round(self.sentiment_score, 2))
        st.write("Sentiment Magnitude:", round(self.sentiment_magnitude, 2))

        # Display the audio waveform
        st.pyplot(self.figure)

        # Return the frame to the WebRTC stream
        return frame

# Define the audio sentiment analysis function
def analyze_audio_sentiment(audio_data):
    # Convert the audio data to a buffer
    audio_buffer = io.BytesIO(audio_data)

    # Perform speech-to-text conversion on the audio data
    response = client.sync_recognize(
        request = {'config': {'encoding': language_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                              'sample_rate_hertz': 16000,
                              'language_code': 'en-US'},
                   'audio': {'content': audio_buffer.read()}}
    )

    # Extract the transcript from the speech-to-text response
    transcript = response.results[0].alternatives[0].transcript

    # Create a document object for the text
    document = language_v1.Document(content=transcript, type_=language_v1.Document.Type.PLAIN_TEXT)

    # Perform sentiment analysis on the document
    response = client.analyze_sentiment(request={'document': document, 'encoding_type': language_v1.EncodingType.UTF8})

    # Return the sentiment score and magnitude
    sentiment_score = response.document_sentiment.score
    sentiment_magnitude = response.document_sentiment.magnitude
    return sentiment_score, sentiment_magnitude

# Streamlit UI setup
def show_audio_sentiment():
    st.title("Audio Sentiment Analysis")

    # Start the WebRTC stream
    webrtc_ctx = webrtc_streamer(
        key="audio_processor",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=lambda: AudioProcessor(),
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True}
    )

# Run the Streamlit app
if __name__ == '__main__':
    show_audio_sentiment()
