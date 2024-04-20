import streamlit as st

# Import the scraper_visual as a module if it's in a different file
import scraper_visual

def scraper():
    st.title('Review Scraper')
    st.write('Welcome to Review Scraper')

def Text_Sentiment():
    st.title('Text Sentiment')
    st.write('Welcome to Text Sentiment')

def Audio_sentiment():
    st.title('Audio Sentiment')
    st.write('Welcome to Audio Sentiment')

def Video_Sentiment():
    st.title('Video Sentiment')
    st.write('Welcome to Video Sentiment')

# Correctly define your pages dictionary
pages = {
    "Review Scraper": scraper,  # Remove .show
    "Text Sentiment": Text_Sentiment,  # Remove .show
    "Audio Sentiment": Audio_sentiment,  # Remove .show
    "Video Sentiment": Video_Sentiment  # Remove .show
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
    pages[page]()  # Call the function that renders the chosen page
