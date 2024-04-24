import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import streamlit.components.v1 as components
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client
import base64

def plot_waveform(data, rate):
    """Plot waveform from audio data."""
    plt.figure(figsize=(10, 3))
    times = np.arange(len(data)) / float(rate)
    plt.fill_between(times, data, color='skyblue')
    plt.xlim(times[0], times[-1])
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Waveform')
    return plt

def show_audio_sentiment():
    st.title('Live Audio Capture and Sentiment Analysis')

    # Placeholder for the waveform plot
    waveform_placeholder = st.empty()

    # JavaScript to capture audio and send it to the server
    audio_capture_js = """
    <script>
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    let mediaRecorder;
    let audioChunks = [];

    recordButton.onclick = () => {
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            audioChunks = [];

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks);
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64data = reader.result;
                    window.parent.postMessage({type: 'audio-data', data: base64data}, '*');
                };
            });
        });
    };

    stopButton.onclick = () => {
        mediaRecorder.stop();
    };
    </script>
    <button id="recordButton">Record</button>
    <button id="stopButton">Stop</button>
    """

    st.markdown(audio_capture_js, unsafe_allow_html=True)

    # Listen for audio data sent from the frontend
    audio_data = st.session_state.get('audio_data', None)
    if audio_data:
        # Decode the base64 data to bytes
        header, encoded = audio_data.split(",", 1)
        data = base64.b64decode(encoded)

        # Convert bytes to numpy array and plot waveform
        rate, audio_array = wavfile.read(io.BytesIO(data))
        plt = plot_waveform(audio_array, rate)
        waveform_placeholder.pyplot(plt)

    # Callback to handle messages from the frontend
    st.write(st.session_state.audio_data if 'audio_data' in st.session_state else 'No data received')

    # Listen for messages from the frontend
    components.html(
        """
        <script>
        window.addEventListener("message", (event) => {
            if (event.data.type === 'audio-data') {
                const audio_data = event.data.data;
                window.parent.postMessage({type: 'audio-data', data: audio_data}, '*');
            }
        }, false);
        </script>
        """,
        height=0,
    )


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
