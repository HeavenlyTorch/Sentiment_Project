import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

def plot_waveform(data, sample_rate):
    """Plot waveform of the audio data."""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(data, sr=sample_rate, alpha=0.5)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    st.pyplot(plt)

def show_audio_sentiment():
    st.title("Audio Sentiment Analysis App")
    st.markdown("## Record your audio")

    # JavaScript to handle audio recording
    audio_html = """
    <button onclick="startRecording(this)">Start recording</button>
    <button onclick="stopRecording(this)" disabled>Stop recording</button>
    <script>
    var button = document.querySelector('button');
    var recorder, stream;
    async function startRecording(button) {
      stream = await navigator.mediaDevices.getUserMedia({audio: true});
      recorder = new MediaRecorder(stream);
      const chunks = [];
      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.start();
      button.disabled = true;
      button.nextElementSibling.disabled = false;
    }
    function stopRecording(button) {
      recorder.onstop = async () => {
        const completeBlob = new Blob(chunks, {type: 'audio/wav'});
        var reader = new FileReader();
        reader.readAsDataURL(completeBlob);
        reader.onloadend = function() {
          var base64String = reader.result;
          Streamlit.setComponentValue(base64String);
        };
        recorder.stop();
        stream.getTracks().forEach(track => track.stop());
        button.disabled = false;
        button.nextElementSibling.disabled = true;
      };
      recorder.stop();
    }
    </script>
    """

    st.components.v1.html(audio_html, height=150)

    audio_data = st.session_state.get("audio_data")
    if audio_data:
        header, b64_data = audio_data.split(',')
        audio_bytes = base64.b64decode(b64_data)
        audio_buffer = io.BytesIO(audio_bytes)
        data, rate = librosa.load(audio_buffer, sr=22050)  # Make sure to set the appropriate sample rate
        st.audio(audio_data, format='audio/wav')
        plot_waveform(data, rate)
        sentiment = np.random.rand()  # Placeholder for actual sentiment analysis
        st.write(f"Sentiment score: {sentiment:.2f}")

    # Handle messages from JavaScript
    st.components.v1.html('<script> window.addEventListener("message", event => Streamlit.setComponentValue(event.data)); </script>', height=0)

if __name__ == '__main__':
    show_audio_sentiment()
