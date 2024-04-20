import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import io
from streamlit.components.v1 import html

def plot_waveform(data, sample_rate):
    """Plot waveform of the audio data."""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(data, sr=sample_rate, alpha=0.5)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    st.pyplot(plt)

def analyze_sentiment(audio_data):
    """Placeholder function to analyze sentiment."""
    sentiment_score = np.random.rand()  # Random sentiment score
    return sentiment_score

def show_audio_sentiment():
    st.title("Audio Sentiment Analysis App")

    # Custom HTML/JavaScript-based audio recorder
    recorder_html = """
    <html>
        <body>
        <audio id="audio" controls></audio>
        <button onclick="startRecording(this);">Record</button>
        <button onclick="stopRecording(this);" disabled>Stop</button>
        <script>
            var audio = document.querySelector('#audio');
            var recorder, stream;
            async function startRecording(button) {
                stream = await navigator.mediaDevices.getUserMedia({audio: true});
                recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => {
                    audio.src = URL.createObjectURL(e.data);
                };
                recorder.start();
                button.disabled = true;
                button.nextElementSibling.disabled = false;
            }
            function stopRecording(button) {
                recorder.stop();
                button.disabled = true;
                button.previousElementSibling.disabled = false;
                stream.getAudioTracks()[0].stop();
            }
        </script>
        </body>
    </html>
    """
    html(recorder_html, height=200)

    # Uploading and displaying the audio file
    uploaded_file = st.file_uploader("Or upload an audio file", type=["wav", "mp3", "ogg"])
    if uploaded_file is not None:
        data, rate = librosa.load(uploaded_file, sr=22050)  # Adjust sample rate as necessary
        st.audio(uploaded_file)
        plot_waveform(data, rate)
        sentiment = analyze_sentiment(data)
        st.write(f"Sentiment score: {sentiment:.2f}")

if __name__ == '__main__':
    show_audio_sentiment()
