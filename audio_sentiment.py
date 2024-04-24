import streamlit as st
import io
import base64
import streamlit.components.v1 as components
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client


def show_audio_sentiment():
    st.title('Real-time Audio Recorder and Sentiment Analysis')

    components.html("""
            <script>
                var recorder, stream;
                const startButton = document.createElement('button');
                startButton.textContent = 'Start Recording';
                document.body.appendChild(startButton);

                const stopButton = document.createElement('button');
                stopButton.textContent = 'Stop Recording';
                document.body.appendChild(stopButton);

                startButton.onclick = async () => {
                    stream = await navigator.mediaDevices.getUserMedia({audio: true});
                    recorder = new MediaRecorder(stream);
                    var chunks = [];
                    recorder.ondataavailable = e => chunks.push(e.data);
                    recorder.onstop = async () => {
                        const blob = new Blob(chunks, {'type' : 'audio/wav; codec=pcm'});
                        const reader = new FileReader();
                        reader.onload = () => {
                            const base64data = reader.result;
                            window.parent.postMessage({type: 'audio-data', data: base64data}, '*');
                        };
                        reader.readAsDataURL(blob);
                    };
                    recorder.start();
                };

                stopButton.onclick = () => {
                    recorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                };
            </script>
        """, height=0)

    # Listen for audio data sent from the frontend
    audio_data = st.session_state.get('audio_data', None)
    if audio_data:
        # Decode the base64 data to bytes
        header, encoded = audio_data.split(",", 1)
        audio_bytes = base64.b64decode(encoded)

        # Use BytesIO to simulate a file
        audio_file = io.BytesIO(audio_bytes)
        audio_file.seek(0)  # Important: seek to the start of the file

        # Process the audio data
        transcript = transcribe_audio(audio_file)
        if transcript:
            score, magnitude = analyze_sentiment(transcript)
            st.write('Transcript:', transcript)
            st.write('Sentiment score:', score, 'Magnitude:', magnitude)

    # Callback to handle messages from the frontend
    components.html("""
            <script>
            window.addEventListener("message", (event) => {
                if (event.data.type === 'audio-data') {
                    const audio_data = event.data.data;
                    Streamlit.setComponentValue(audio_data);
                }
            }, false);
            </script>
        """, height=0)


if __name__ == '__main__':
    show_audio_sentiment()