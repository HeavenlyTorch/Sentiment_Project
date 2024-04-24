import os
import base64
import streamlit as st
from google.cloud import speech, language_v1
import io

# Set up Google Cloud API clients
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'
speech_client = speech.SpeechClient()
language_client = language_v1.LanguageServiceClient()


def analyze_sentiment(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = language_client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score, sentiment.magnitude


def transcribe_audio(audio_file):
    audio_content = audio_file.read()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # Make sure this matches the recording rate of the audio
        language_code='en-US'
    )

    response = speech_client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    return transcript


def show_audio_sentiment():
    st.title('Real-time Audio Capture and Sentiment Analysis')

    # Frontend: Audio recording
    record_btn = st.button('Record Audio')
    stop_btn = st.button('Stop Recording')

    if record_btn:
        js_code = """
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            const audioChunks = [];
            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });
            window.mediaRecorder = mediaRecorder;
            window.audioStream = stream;
        });
        """
        st.components.v1.html(f"<script>{js_code}</script>")

    if stop_btn:
        js_code = """
        window.mediaRecorder.stop();
        window.mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(window.audioChunks);
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();

            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onload = () => {
                const base64AudioMessage = reader.result.split(',')[1];
                fetch("/upload_audio", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: base64AudioMessage})
                }).then(res => {
                    console.log("Request complete! response:", res);
                });
            };
        });
        window.audioStream.getTracks().forEach(track => track.stop());
        """
        st.components.v1.html(f"<script>{js_code}</script>")

    # Backend: Process audio file
    audio_file = st.file_uploader("Upload audio for analysis", type=["wav"])
    if audio_file is not None:
        text = transcribe_audio(audio_file)
        if text:
            score, magnitude = analyze_sentiment(text)
            st.write(f"Transcript: {text}")
            st.write(f"Sentiment Score: {score}, Magnitude: {magnitude}")
        else:
            st.error("Could not transcribe the audio.")


if __name__ == '__main__':
    show_audio_sentiment()
