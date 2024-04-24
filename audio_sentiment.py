import streamlit as st
import base64
import io
import streamlit.components.v1 as components
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client

def show_audio_sentiment():
    st.title('Real-time Audio Recorder and Sentiment Analysis')

    record_btn = st.button('Record Audio')
    stop_btn = st.button('Stop and Process')

    # Component to handle real-time audio data
    audio_data = st.empty()

    components.html("""
                    <script>
                        var recorder, stream;
                        const startButton = document.createElement('button');
                        startButton.textContent = 'Start Recording';
                        document.body.appendChild(startButton);

                        const stopButton = document.createElement('button');
                        stopButton.textContent = 'Stop Recording';
                        document.body.appendChild(stopButton);

                        let audio_data_sent = false;

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
                                    audio_data_sent = true;
                                };
                                reader.readAsDataURL(blob);
                            };
                            recorder.start();
                        };

                        stopButton.onclick = () => {
                            recorder.stop();
                            stream.getTracks().forEach(track => track.stop());
                        };

                        window.addEventListener("message", (event) => {
                            if (event.data.type === 'audio-data' && audio_data_sent) {
                                const audio_data = event.data.data;
                                Streamlit.setComponentValue(audio_data);
                                audio_data_sent = false;
                                process_audio_data();
                            }
                        }, false);

                        function process_audio_data() {
                            const audio_data = Streamlit.getComponentValue();
                            if (audio_data) {
                                const header = "data:audio/wav;base64,";
                                const base64data = audio_data.slice(header.length);
                                const audio_bytes = atob(base64data);
                                const audio_file = new Blob([audio_bytes], {type: "audio/wav"});
                                const reader = new FileReader();
                                reader.onload = () => {
                                    const audio_data_url = reader.result;
                                    window.parent.postMessage({type: 'processed-audio-data', data: audio_data_url}, '*');
                                };
                                reader.readAsDataURL(audio_file);
                            }
                        }
                    </script>
                """, height=0)

    # Listen for audio data sent from the frontend
    audio_data = st.session_state.get('processed_audio_data', None)
    if audio_data:
        # Process the audio data
        audio_file = io.StringIO(audio_data)
        transcript = transcribe_audio(audio_file)
        if transcript:
            score, magnitude = analyze_sentiment(transcript)
            st.write('Transcript:', transcript)
            st.write('Sentiment score:', score, 'Magnitude:', magnitude)

    # Callback to handle messages from the frontend
    components.html("""
                    <script>
                    window.addEventListener("message", (event) => {
                        if (event.data.type === 'processed-audio-data') {
                            const audio_data_url = event.data.data;
                            const audio = new Audio(audio_data_url);
                            audio.play();
                        }
                    }, false);
                    </script>
                """, height=0)

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