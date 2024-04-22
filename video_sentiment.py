import streamlit as st
import cv2
import tempfile
import os
from keras.models import load_model


# Load your sentiment analysis model (ensure the model is compatible and trained for video sentiment analysis)
model = load_model('path_to_model.h5')

def get_frame(cap):
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to grab frame.")
        return None
    return frame


def analyze_frame(frame, model):
    # This function should preprocess the frame and perform sentiment analysis using your model
    # Placeholder function: replace with actual analysis code
    return "Positive"  # Example: return the sentiment detected

def show_video_sentiment():
    st.title("Video Sentiment Analysis App")

    # Real-time video analysis
    if st.button('Start Camera'):
        FRAME_WINDOW = st.image([])
        cap = cv2.VideoCapture(0)  # Use 0 for default camera

        while True:
            frame = get_frame(cap)
            if frame is not None:
                sentiment = analyze_frame(frame, model)
                FRAME_WINDOW.image(frame, caption=f"Sentiment: {sentiment}", use_column_width=True)
            else:
                break

        cap.release()

    # Handling large video datasets
    uploaded_files = st.file_uploader("Upload video files", accept_multiple_files=True, type=["mp4", "avi", "mov"])
    for uploaded_file in uploaded_files:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        video_path = tfile.name
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            frame = get_frame(cap)
            if frame is not None:
                sentiment = analyze_frame(frame, model)
                st.write(f"Video: {uploaded_file.name}, Sentiment: {sentiment}")
            else:
                break

        cap.release()
        os.unlink(tfile.name)  # Remove the tempfile

    st.button("Clear Results", on_click=lambda: st.caching.clear_cache())

