import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from transformers import pipeline
import seaborn as sns
import matplotlib.pyplot as plt
import re

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Function to analyze sentiment of a given text
def analyze_sentiment(text):
    return sentiment_pipeline(text)[0]

# Basic Data Cleaning Function
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'#\w+', '', text)  # Remove hashtags
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()

# Function to analyze text from the text box
def analyze_text():
    text = clean_text(text_entry.get("1.0", "end-1c"))
    if not text:
        messagebox.showinfo("Info", "Please enter some text to analyze.")
        return

    result = sentiment_pipeline(text)
    messagebox.showinfo("Analysis Result", f"Text: {text}\nSentiment: {result[0]['label']} with score: {result[0]['score']:.2f}")

# Function to analyze text from a CSV file
# Function to Analyze Sentiment of Texts in a CSV File
def analyze_csv():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    # Adjust the column index as per your CSV structure; assuming the tweet text is in the fourth column
    df = pd.read_csv(file_path, usecols=[3], header=None, skiprows=1, names=['text'])

    df['clean_text'] = df['text'].apply(clean_text)
    df['sentiment'] = df['clean_text'].apply(lambda x: sentiment_pipeline(x)[0]['label'])
    df.drop(columns=['clean_text'], inplace=True)

    # Visualization
    sns.countplot(x=df['sentiment'])
    plt.title('Sentiment Distribution')
    plt.show()

# Set up the GUI
root = tk.Tk()
root.title("Sentiment Analysis")

text_frame = tk.Frame(root)
text_frame.pack(pady=20)
text_entry = tk.Text(text_frame, height=5, width=50)
text_entry.pack(side="left", padx=(0, 10))
analyze_button = tk.Button(text_frame, text="Analyze Text", command=analyze_text)
analyze_button.pack(side="left")

csv_frame = tk.Frame(root)
csv_frame.pack(pady=20)
load_csv_button = tk.Button(csv_frame, text="Load CSV File", command=analyze_csv)
load_csv_button.pack()

root.mainloop()
