import streamlit as st

# Import the scraper_visual as a module if it's in a different file
from scraper_visual import show_scraper
from text_sentiment import show_Text_Sentiment
from audio_sentiment import show_audio_sentiment


def Audio_sentiment():
    st.title('Audio Sentiment')
    st.write('Welcome to Audio Sentiment')

def Video_Sentiment():
    st.title('Video Sentiment')
    st.write('Welcome to Video Sentiment')

# Dictionary
pages = {
    "Review Scraper": show_scraper,
    "Text Sentiment": show_Text_Sentiment,
    "Audio Sentiment": show_audio_sentiment,
    "Video Sentiment": Video_Sentiment
}

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Sidebar for navigation
with st.sidebar:
    st.title('Navigation')
    page = st.radio("Choose a page:", ['Home'] + list(pages.keys()))

# Display the selected page using the state
if page == 'Home':
    st.title('Home Page')
    st.write('Welcome to the Home Page. Please select a page from the sidebar.')
else:
    pages[page]()   # Call the function that renders the chosen page
