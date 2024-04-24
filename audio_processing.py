import os
import wave
from google.cloud import speech, language_v1

# Set up Google Cloud API clients
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'trusty-sentinel-421215-f5581358b4be.json'
speech_client = speech.SpeechClient()
language_client = language_v1.LanguageServiceClient()

def transcribe_audio(audio_file):
    # Read and close the WAV file
    with wave.open(audio_file, 'rb') as wf:
        sample_rate = wf.getframerate()  # Get the sample rate from the WAV file header

    # Rewind the file pointer to the beginning of the audio file after reading the sample rate
    audio_file.seek(0)
    audio_content = audio_file.read()

    # Prepare the audio data for the Google API
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,  # Use the actual sample rate of the audio file
        language_code='en-US'
    )

    # Perform the speech-to-text operation
    response = speech_client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    return transcript


def analyze_sentiment(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = language_client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score, sentiment.magnitude
