import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import pyaudio
from transformers import pipeline
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import seaborn as sns
import matplotlib.pyplot as plt
from threading import Thread
import re
import numpy as np
from queue import Queue, Empty
import requests
from bs4 import BeautifulSoup
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import wave
from matplotlib.animation import FuncAnimation
import torch
import soundfile as sf
import cv2
from PIL import Image, ImageTk
import openai
import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

#____________________________LOGIN/REGISTER__________________________
def db_connection():
    """Create a database connection with context management."""
    return sqlite3.connect('users.db')

# Database Initialization
def create_db():
    with db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Modify register and login functions to accept the auth_window and close it on success

def register_user(username, password):
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(password)
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    from werkzeug.security import check_password_hash
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
    return user and check_password_hash(user[0], password)

def show_login():
    clear_frame()

    frame = tk.Frame(root)
    frame.pack()

    tk.Label(frame, text="Username:").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()

    tk.Label(frame, text="Password:").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        if login_user(username, password):
            messagebox.showinfo("Login Info", "Login successful!")
            show_dashboard()
        else:
            messagebox.showinfo("Login Info", "Login failed!")

    tk.Button(frame, text="Login", command=attempt_login).pack()
    tk.Button(frame, text="Register", command=show_register).pack()

def show_register():
    clear_frame()

    frame = tk.Frame(root)
    frame.pack()

    tk.Label(frame, text="Username:").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()

    tk.Label(frame, text="Password:").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()

    def attempt_register():
        username = username_entry.get()
        password = password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Register Info", "Registration successful! Please login.")
            show_login()
        else:
            messagebox.showinfo("Register Info", "Registration failed. User might already exist.")

    tk.Button(frame, text="Register", command=attempt_register).pack()
    tk.Button(frame, text="Back to Login", command=show_login).pack()


#_________________video sentiment_________________________

def video_analysis(main_frame):
    # Ensure the frame is cleared before adding new elements
    clear_frame(main_frame)

    cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open camera")
        return

    def show_frame():
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Can't receive frame (stream end?). Exiting ...")
            cap.release()
            return
        # Convert the image to RGB (from BGR)
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)

    lmain = tk.Label(main_frame)
    lmain.pack()
    show_frame()

#__________________Audio sentiment_______________________
# Constants for Audio Recording
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def create_audio_stream():
    p = pyaudio.PyAudio()
    return p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def start_recording(app):
    app.stream = create_audio_stream()
    app.frames = []

    fig, ax = plt.subplots()
    x = np.arange(0, 2 * CHUNK, 2)
    line, = ax.plot(x, np.zeros(CHUNK))
    ax.set_ylim(-2**15, 2**15)
    ax.set_xlim(0, CHUNK)

    def update(frame):
        if not app.stream.is_active():
            return line,
        data = np.frombuffer(app.stream.read(CHUNK), dtype=np.int16)
        app.frames.append(data)
        line.set_ydata(data)
        return line,

    ani = FuncAnimation(fig, update, interval=1, blit=True)
    plt.show()

def stop_recording(app):
    app.stream.stop_stream()
    app.stream.close()
    app.p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(app.p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(app.frames))
    wf.close()

    # Perform transcription and sentiment analysis
    transcription = transcribe(WAVE_OUTPUT_FILENAME)
    sentiment = sentiment_pipeline(transcription)
    print(f"Transcription: {transcription}")
    print(f"Sentiment: {sentiment}")

def transcribe(audio_file):
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
    speech, sampling_rate = sf.read(audio_file)
    input_values = processor(speech, return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)[0]

#__________________TEXT SENTIMENT ANALYSIS________________________

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_irrelevant(text, irrelevant_keywords):
    words = set(text.lower().split())
    return any(word in words for word in irrelevant_keywords)

def analyze_sentiment(text, irrelevant_keywords):
    if is_irrelevant(text, irrelevant_keywords):
        return 'IRRELEVANT'
    result = sentiment_pipeline(text, truncation=True, padding=True)[0]
    print(f"Text: {text[:30]}, Label: {result['label']}, Score: {result['score']}")
    if result['label'] == 'NEGATIVE' and result['score'] > 0.6:
        return 'NEGATIVE'
    elif result['label'] == 'POSITIVE' and result['score'] > 0.6:
        return 'POSITIVE'
    return 'NEUTRAL'

irrelevant_keywords = [
    'example', 'irrelevant', 'n/a', 'not applicable', 'none',
    'nothing', 'dummy', 'sample', 'lorem', 'ipsum'
]


def process_csv_in_thread(file_path, queue, irrelevant_keywords):
    try:
        df = pd.read_csv(file_path)
        sentiments = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'IRRELEVANT': 0}

        for index, row in df.iterrows():
            clean = clean_text(row['text'])
            sentiment = analyze_sentiment(clean, irrelevant_keywords)
            sentiments[sentiment] += 1
            df.at[index, 'sentiment'] = sentiment

        # After classification, print the counts of each sentiment
        print(sentiments)
        df.to_csv("sentiment_analysis_result.csv", index=False)
        queue.put('COMPLETE')
    except Exception as e:
        queue.put(f'ERROR: {str(e)}')

def analyze_csv(progress_bar, root):
    """ Handle CSV file selection and start thread for processing. """
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    queue = Queue()
    Thread(target=process_csv_in_thread, args=(file_path, queue, irrelevant_keywords), daemon=True).start()
    update_progress(queue, progress_bar, root)


def update_progress(queue, progress_bar, root):
    try:
        while True:
            item = queue.get_nowait()
            if item == 'COMPLETE':
                messagebox.showinfo("Info", "Sentiment analysis completed.")
                visualize_sentiment_distribution()
                break
            elif isinstance(item, str) and item.startswith('ERROR'):
                messagebox.showerror("Error", item)
                break
            else:
                progress_bar['value'] = item
            root.update_idletasks()
    except Empty:
        root.after(100, lambda: update_progress(queue, progress_bar, root))



def visualize_sentiment_distribution():
    try:
        df = pd.read_csv("sentiment_analysis_result.csv")
        if df.empty:
            messagebox.showinfo("Info", "No data to plot.")
            return
        plt.figure(figsize=(10, 6))
        sns.countplot(x='sentiment', data=df, order=['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'IRRELEVANT'])
        plt.title('Sentiment Distribution')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.show()
        plt.close()  # Ensure the plot is closed after displaying
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found.")
    except Exception as e:
        print("Error loading or plotting data:", str(e))
def analyze_text(text_entry, root, irrelevant_keywords):
    text = clean_text(text_entry.get("1.0", "end-1c"))
    if not text:
        messagebox.showinfo("Info", "Please enter some text to analyze.")
        return
    sentiment = analyze_sentiment(text, irrelevant_keywords)
    messagebox.showinfo("Analysis Result", f"Text: {text}\nSentiment: {sentiment}")
#__________________URL Scrapper_______________________
# Function to scrape Amazon reviews
def scrape_reviews(product_url):
    # Initialize a Selenium Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Go to the product URL
    driver.get(product_url)

    # Wait for the page to load dynamically loaded content
    time.sleep(10)  # Adjust timing as needed for your connection

    # Find the reviews on the page
    reviews = driver.find_elements(By.CSS_SELECTOR, '.review-text-content span')
    data = []
    for review in reviews:
        data.append({'Review': review.text})

    driver.quit()

    # Save data if reviews are found
    if data:
        df = pd.DataFrame(data)
        df.to_csv('amazon_reviews.csv', index=False)
        print("Reviews have been saved to 'amazon_reviews.csv'")
    else:
        print("No reviews found with the given selectors.")



def get_url_and_scrape():
    product_url = simpledialog.askstring("Input", "Enter the Amazon product review page URL:")
    if product_url:
        scrape_reviews(product_url)

# Function to create the main GUI

# Initialize the main application window
root = tk.Tk()
root.title("Sentiment Analysis Application")
root.geometry("600x400")

# Create a main frame which will contain all other widgets
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_dashboard():
    clear_frame(main_frame)
    tk.Label(main_frame, text="Welcome to the dashboard!").pack()

    # Ensure commands are set correctly
    text_analysis_button = tk.Button(main_frame, text="Text Analysis", command=text_analysis)
    text_analysis_button.pack(side="left", padx=10)

    audio_analysis_button = tk.Button(main_frame, text="Audio Analysis", command=audio_analysis)
    audio_analysis_button.pack(side="left", padx=10)

    video_analysis_button = tk.Button(main_frame, text="Video Analysis", command=lambda: video_analysis(main_frame))
    video_analysis_button.pack(side="left", padx=10)

    url_scraper_button = tk.Button(main_frame, text="URL Scraper", command=url_scraper)
    url_scraper_button.pack(side="left", padx=10)

    account_button = tk.Button(main_frame, text="Account Settings", command=show_login)
    account_button.pack(side="top", pady=5)

def show_register():
    clear_frame(main_frame)
    frame = tk.Frame(main_frame)
    frame.pack()

    tk.Label(frame, text="Username:").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()

    tk.Label(frame, text="Password:").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()

    def attempt_register():
        if register_user(username_entry.get(), password_entry.get()):
            messagebox.showinfo("Register Info", "Registration successful! Please login.")
            show_login()
        else:
            messagebox.showinfo("Register Info", "Registration failed. User might already exist.")

    tk.Button(frame, text="Register", command=attempt_register).pack()
    tk.Button(frame, text="Back to Login", command=show_login).pack()

def show_login():
    clear_frame(main_frame)
    frame = tk.Frame(main_frame)
    frame.pack()

    tk.Label(frame, text="Username:").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()

    tk.Label(frame, text="Password:").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()

    def attempt_login():
        # Assume login_user() is a function that returns True if login is successful
        if login_user(username_entry.get(), password_entry.get()):  # Just a placeholder function call
            messagebox.showinfo("Login Info", "Login successful!")
            show_dashboard()
        else:
            messagebox.showinfo("Login Info", "Login failed!")

    tk.Button(frame, text="Login", command=attempt_login).pack()
    tk.Button(frame, text="Register", command=show_register).pack()

def text_analysis():
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)
    clear_frame(main_frame)
    text_frame = tk.Frame(main_frame)

    text_entry = tk.Text(main_frame, height=5, width=50)
    text_entry.pack(side="left", padx=10)

    analyze_button = tk.Button(main_frame, text="Analyze Text",command=lambda: analyze_text(text_entry, main_frame, irrelevant_keywords))
    analyze_button.pack(side="left")

    csv_frame = tk.Frame(main_frame)
    csv_frame.pack(pady=20)

    analyze_button = tk.Button(root, text="Analyze CSV", command=lambda: analyze_csv(progress_bar, root))
    analyze_button.pack(pady=10)

    progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=400)
    progress_bar.pack(pady=20)

    home_button = tk.Button(main_frame, text="Home", command=show_dashboard)
    home_button.pack(side="top", pady=5)

def audio_analysis():
    clear_frame(main_frame)
    # This clears all the widgets in the main_frame

    # Waveform display frame setup
    waveform_frame = tk.Frame(main_frame)
    waveform_frame.pack(fill="both", expand=True, pady=20)

    # Control frame for audio recording controls
    control_frame = tk.Frame(main_frame)
    control_frame.pack()

    # Start recording button
    start_button = tk.Button(control_frame, text="Start Recording", command=lambda: start_recording(root))
    start_button.pack(side="left", padx=10)

    # Stop recording button
    stop_button = tk.Button(control_frame, text="Stop Recording", command=lambda: stop_recording(root.stream))
    stop_button.pack(side="left", padx=10)

    # Home button to return to the main menu
    home_button = tk.Button(main_frame, text="Home", command=lambda: show_dashboard())
    home_button.pack(side="bottom", pady=10)

def video_analysis(main_frame):
    clear_frame(main_frame)
    # Just a placeholder for the actual video analysis content
    label = tk.Label(main_frame, text="Video Analysis Mode")
    label.pack()

    home_button = tk.Button(main_frame, text="Home", command=show_dashboard)
    home_button.pack(side="bottom", pady=10)
def url_scraper():
    clear_frame(main_frame)  # Clear the main frame before setting up the URL scraper GUI

    # Label for the URL entry
    url_label = tk.Label(main_frame, text="Enter URL to Scrape:")
    url_label.pack(pady=5)

    # Text entry for the URL
    url_entry = tk.Entry(main_frame, width=50)
    url_entry.pack(pady=5)

    # Button to start scraping
    scrape_button = tk.Button(main_frame, text="Scrape", command=lambda: scrape_reviews(url_entry.get()))
    scrape_button.pack(pady=10)

    # Home button to return to the main menu
    home_button = tk.Button(main_frame, text="Home", command=lambda: show_dashboard())
    home_button.pack(side="bottom", pady=10)

# Initialize with the home page
show_dashboard()

def main_app():
    show_login()
    root.mainloop()

if __name__ == "__main__":
    main_app()

main_app()