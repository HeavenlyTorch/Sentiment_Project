import streamlit as st
import cv2
import tempfile
import tensorflow as tf
#from tensorflow.keras.models import load_model
import numpy as np

# Load your pre-trained model (make sure to provide the correct path)
#model = load_model('model.h5')

def extract_frames(video_file):
    # Extract frames from the video file
    frames = []
    vidcap = cv2.VideoCapture(video_file)
    success, image = vidcap.read()
    while success:
        frames.append(image)
        success, image = vidcap.read()
    vidcap.release()
    return frames

def analyze_sentiment(frames):
    # Analyze sentiment for each frame
    results = []
    for frame in frames:
        # Preprocess frame (resize, normalize, etc.)
        frame = cv2.resize(frame, (224, 224))  # Example resize to model expected size
        frame = frame / 255.0  # Normalize pixel values
        frame = np.expand_dims(frame, axis=0)  # Expand dims to fit model input
        #pred = model.predict(frame)
        #results.append(pred)
    return results

# Streamlit user interface
st.title('Video Sentiment Analysis App')

uploaded_file = st.file_uploader("Choose a video...", type=['mp4', 'avi'])
if uploaded_file is not None:
    # Use a temporary file to store the uploaded video
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_frames = extract_frames(tmp_file.name)

    # Perform sentiment analysis
    sentiments = analyze_sentiment(video_frames)

    # Display results
    for i, sentiment in enumerate(sentiments):
        st.write(f"Frame {i + 1}: Sentiment - {np.argmax(sentiment)}")
