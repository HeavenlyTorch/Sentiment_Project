import streamlit as st
import os
import pybase64
from pydub import AudioSegment
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

# Function to generate a waveform
def plot_waveform(wav_file):
    rate, data = wavfile.read(wav_file)
    plt.figure(figsize=(10, 4))
    plt.plot(data, color='blue')
    st.pyplot(plt)

def show_audio_sentiment():
    # Streamlit UI
    st.title("Audio Analysis App")

    # Record audio (requires user to manually start/stop recording)
    audio_recorder = """
    <button onclick="startRecording(this);">Start Recording</button>
    <button onclick="stopRecording(this);" disabled>Stop Recording</button>
    <script>
    var button = document.querySelector('button');
    var recorder, stream;

    async function startRecording(button) {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        const chunks = [];
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = e => {
            const completeBlob = new Blob(chunks, { type: chunks[0].type });
            var reader = new FileReader();
            reader.readAsDataURL(completeBlob);
            reader.onloadend = function() {
                var base64data = reader.result;
                document.getElementById('audio_base64').value = base64data;
            }
        };
        recorder.start();
        button.nextElementSibling.disabled = false;
        button.disabled = true;
    }

    function stopRecording(button) {
        recorder.stop();
        stream.getTracks().forEach(track => track.stop());
        button.previousElementSibling.disabled = false;
        button.disabled = true;
    }
    </script>
    <input type="hidden" id="audio_base64" name="audio_base64">
    """

    st.markdown(audio_recorder, unsafe_allow_html=True)
    audio_base64 = st.text_input("Audio Base64", "", type="password")

    # File uploader for dataset analysis
    uploaded_files = st.file_uploader("Choose an audio file", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            with open(os.path.join("tempDir", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.write(f"Processed {uploaded_file.name}")
            plot_waveform(os.path.join("tempDir", uploaded_file.name))

    # Reset button
    if st.button('Reset'):
        st.caching.clear_cache()
        st.experimental_rerun()

    # Example sentiment analysis (you will need an actual model or API call here)
    if audio_base64:
        st.write("Performing sentiment analysis on the recorded audio...")
        # This is a placeholder, you should integrate actual sentiment analysis here
        st.write("Sentiment: Positive")

