from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')

def show_Text_Sentiment():
    analyzer = SentimentIntensityAnalyzer()
    st.header("Sentiment Analysis")

    # Analyze individual text
    with st.expander("Analyze Text"):
        text = st.text_input('Text here: ')
        if text:
            sentiment_scores = analyzer.polarity_scores(text)
            polarity = sentiment_scores['compound']
            sentiment_label = 'Positive' if polarity > 0 else ('Negative' if polarity < 0 else 'Neutral')
            st.write('Polarity:', round(polarity, 2))
            st.write('Sentiment:', sentiment_label)

    # File uploader for CSV analysis
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        data = load_csv(uploaded_file)
        if 'Comments' in data.columns:
            st.write("Preview of uploaded data:")
            st.write(data.head())

            # Processing sentiment analysis
            data = process_sentiment(data)
            st.write("Sentiment Analysis Completed. Preview:")
            st.write(data.head())

            # Plotting sentiment distribution
            plot_sentiment_distribution(data)

            # Option to download the results
            st.download_button(
                label="Download Sentiment Analysis Results",
                data=data.to_csv(index=False).encode('utf-8'),
                file_name='sentiment_analysis_results.csv',
                mime='text/csv'
            )
        else:
            st.error("CSV does not contain 'Comments' column. Please upload a CSV with the required column.")

def load_csv(uploaded_file):
    """Loads a CSV file into a DataFrame."""
    return pd.read_csv(uploaded_file)

def process_sentiment(df):
    """Processes sentiment analysis for the 'Comments' column in the DataFrame."""
    analyzer = SentimentIntensityAnalyzer()
    # Define a function to calculate sentiment
    def sentiment_score(text):
        return analyzer.polarity_scores(text)['compound']
    # Define a function to categorize sentiment
    def sentiment_category(score):
        if score > 0:
            return 'Positive'
        elif score < 0:
            return 'Negative'
        else:
            return 'Neutral'
    # Apply the sentiment_score function
    df['Sentiment Score'] = df['Comments'].apply(sentiment_score)
    # Apply the sentiment_category function
    df['Sentiment Category'] = df['Sentiment Score'].apply(sentiment_category)
    return df

def plot_sentiment_distribution(df):
    """Plots the sentiment distribution of the DataFrame."""
    sentiment_counts = df['Sentiment Category'].value_counts()
    plt.figure(figsize=(8, 4))
    plt.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'red', 'blue'])
    plt.xlabel('Sentiment Category')
    plt.ylabel('Count')
    plt.title('Distribution of Sentiments')
    st.pyplot(plt)

if __name__ == "__main__":
    show_Text_Sentiment()
