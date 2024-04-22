import base64
import io
import os
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import streamlit as st
from tensorflow.keras.applications import VGG16

# Load the VGG16 model
model = VGG16(weights="imagenet", include_top=False)

# Function for video sentiment analysis
def video_sentiment_analysis(video_file):
    # Initialize the video capture object
    cap = cv2.VideoCapture(video_file)

    # Process the video frame-by-frame
    frame_count = 0
    total_features = np.zeros((1, 4096))

    while cap.isOpened():
        # Read the frame
        ret, frame = cap.read()

        # Break the loop if the frame is not read correctly
        if not ret:
            break

        # Resize the frame
        frame = cv2.resize(frame, (224, 224))

        # Normalize the frame
        frame = frame / 255.0

        # Expand the dimensions to match the model's input shape
        frame = np.expand_dims(frame, axis=0)

        # Extract features from the frame
        features = model.predict(frame)

        # Add the features to the total features
        total_features += features.reshape((1, -1))

        # Display the frame count
        frame_count += 1
        st.write(f"Frame Count: {frame_count}")

    # Release the video capture object
    cap.release()

    # Average the features to get the final sentiment
    sentiment = total_features / frame_count

    # Display the sentiment
    st.write(f"Sentiment: {sentiment}")

# Streamlit app
def show_video_sentiment():
    st.title("Video Sentiment Analysis")

    # Video upload
    uploaded_video = st.file_uploader("Upload a video", type="mp4")

    if uploaded_video:
        # Save the uploaded video temporarily
        with open("temp.mp4", "wb") as f:
            f.write(uploaded_video.read())

        # Perform video sentiment analysis
        video_sentiment_analysis("temp.mp4")

# Run the Streamlit app
if __name__ == "__main__":
    show_video_sentiment()