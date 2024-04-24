import streamlit as st
import base64
import streamlit.components.v1 as components
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client

def show_audio_sentiment():
    st.title('Real-time Audio Recorder and Sentiment Analysis')

    record_btn = st.button('Record Audio')
    stop_btn = st.button('Stop and Process')

    # Component to handle real-time audio data
    audio_data = st.empty()

    # HTML and JS for handling audio recording
    components.html("""
            <script>
                const recordButton = document.querySelector('button[data-testid="stButton"][aria-label="Record Audio"]');
                const stopButton = document.querySelector('button[data-testid="stButton"][aria-label="Stop and Process"]');
                var recorder, stream;

                async function startRecording() {
                    stream = await navigator.mediaDevices.getUserMedia({audio: true});
                    recorder = new MediaRecorder(stream);
                    var chunks = [];
                    recorder.ondataavailable = e => {
                        chunks.push(e.data);
                    };
                    recorder.onstop = e => {
                        var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
                        chunks = [];
                        var reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onloadend = function() {
                            var base64data = reader.result;
                            streamlit.setComponentValue(base64data);
                        }
                    };
                    recorder.start();
                }

                function stopRecording() {
                    recorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                }

                window.onload = () => {
                    recordButton.onclick = startRecording;
                    stopButton.onclick = stopRecording;
                }
            </script>
            """, height=0)

    if 'audio_data' in st.session_state:
        audio_data = st.session_state.audio_data
        if audio_data:
            audio_bytes = base64.b64decode(audio_data.split(',')[1])
            # Process the audio data with your backend functions
            # Example: transcript = transcribe_audio(audio_bytes)
            # Example: sentiment analysis etc.
            # Clear the audio data after processing
            del st.session_state['audio_data']

    # Use an uploader as a fallback
    audio_file = st.file_uploader("Upload audio for analysis", type=["wav"])
    if audio_file is not None:

    # Process the uploaded file
    # Example: transcript = transcribe_audio(audio_file)
    # Display results, etc.

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