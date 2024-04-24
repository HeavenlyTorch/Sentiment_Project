import streamlit as st
import streamlit.components.v1 as components
from audio_processing import transcribe_audio, analyze_sentiment
from pusher_config import notify_client

def show_audio_sentiment():
    st.title('Real-time Audio Recorder and Sentiment Analysis')
    record_btn = st.button('Record Audio')
    stop_btn = st.button('Stop and Process')

    if record_btn:
        st.session_state['record'] = True

    if stop_btn and 'record' in st.session_state and st.session_state['record']:
        st.session_state['record'] = False
        audio_data = st.session_state.get('audio_data', None)
        if audio_data:
            transcript = transcribe_audio(audio_data)
            score, magnitude = analyze_sentiment(transcript)
            st.write('Transcript:', transcript)
            st.write('Sentiment score:', score, 'Magnitude:', magnitude)

    components.html("""
            <script>
                const recordButton = document.querySelector('button[data-testid="stButton"][aria-label="Record Audio"]');
                const stopButton = document.querySelector('button[data-testid="stButton"][aria-label="Stop and Process"]');

                recordButton.onclick = null;
                stopButton.onclick = null;

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
                            var audio_data = base64data.split(',')[1];
                            window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'audio_data', value: audio_data}, '*');
                        }
                    };
                    recorder.start();
                }

                function stopRecording() {
                    recorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                }

                recordButton.addEventListener('click', startRecording);
                stopButton.addEventListener('click', stopRecording);
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
