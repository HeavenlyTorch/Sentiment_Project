import streamlit as st
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client

def show_audio_sentiment():
    st.title('Real-time Audio Analysis with Sentiment')
    audio_file = st.file_uploader("Upload audio for analysis", type=["wav"])
    if audio_file is not None:
        transcript = transcribe_audio(audio_file)
        if transcript:
            score, magnitude = analyze_sentiment(transcript)
            notify_client(transcript, score, magnitude)
            st.write(f"Transcript: {transcript}")
            st.write(f"Sentiment Score: {score}, Magnitude: {magnitude}")

if __name__ == '__main__':
    show_audio_sentiment()
