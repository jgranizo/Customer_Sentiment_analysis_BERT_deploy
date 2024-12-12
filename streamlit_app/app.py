import boto3
import json
from datetime import datetime
import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
# Count the occurrences of each sentiment
from collections import Counter
import os


# Path to your JSON file
file_name= "brand_data_with_sentiment_2024-12-12.json" 

# Open and load the JSON data


current_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the name of your data file

# Construct the full file path
file_path = os.path.join(current_dir, file_name)

# Debugging: Display the current directory and list of files



# Attempt to open and read the JSON file
try:
    with open(file_path, 'r') as file:
        reddit_data = json.load(file)
 # Display the JSON data in a formatted way
except FileNotFoundError:
    st.error(f"File not found: `{file_name}`. Please ensure it is in the same directory as `app.py`.")
except json.JSONDecodeError:
    st.error(f"Error decoding JSON in `{file_name}`. Please check the file's format.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}") # Input file with today's date

st.markdown("""
    <style>
    .title-text {
        font-weight: 900; /* Makes the text very bold */
        font-size: 1.5em;  /* Adjusts the font size */
        color: #2E86C1;    /* Optional: Changes the text color */
    }
    .small-text {
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown("[Go to Page 1](./test)")
# Extract data for visualization
# We'll create a DataFrame with columns: Company, Subreddit, Sentiment
records = []
for company, posts in reddit_data.items():
    for post_title, post_content in posts.items():
        post_info = post_content.get('Post_Info', {})
        subreddit = post_info.get('Subreddit', 'Unknown')
        comments = post_content.get('Comments', {})
        
        # Each comment: sentiment is stored under "Sentimental_Value"
        for comment_text, comment_details in comments.items():
            sentiment = comment_details.get('Sentimental_Value', 'N/A')
            records.append({
                "Company": company,
                "Subreddit": subreddit,
                "Sentiment": sentiment
            })

df = pd.DataFrame(records)

# Filter only the subreddits we care about: "technology", "gadgets", "stocks"
df = df[df["Subreddit"].isin(["technology",  "stocks"])]

st.header("Comment Sentiment Distribution by Company and Subreddit")

# Create a stacked bar chart of sentiment counts
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Company:N', title='Company'),
    y=alt.Y('count()', title='Number of Comments'),
    color=alt.Color('Sentiment:N', scale=alt.Scale(scheme='category10')),
    column=alt.Column('Subreddit:N', title='Subreddit', header=alt.Header(labelColor='darkblue'))
).properties(
    width=100,   # Reduced width
    height=200   # Reduced height
).configure_axis(
    labelFontSize=10,
    titleFontSize=12
).configure_title(
    fontSize=14
)

st.altair_chart(chart, use_container_width=True)

# The above chart creates a small multiples chart with one column per subreddit.
# Each column shows a stacked bar chart of sentiment distribution per company.
# If you'd prefer a single combined chart, remove the `column` encoding and consider 
# using `y='count()'` and a facet or other approach.
# Extract all sentiments from all companies and posts
sentiments = []
for company, posts in reddit_data.items():
    for post_title, post_data in posts.items():
        comments = post_data.get("Comments", {})
        for comment_text, comment_details in comments.items():
            sentiment = comment_details.get("Sentimental_Value", "Neutral")
            sentiments.append(sentiment)

st.header("Sentiment Distribution by Company and Subreddit")

# Define sentiment categories
categories = ["Positive", "Neutral", "Negative"]

# Get a list of unique companies and the chosen subreddits
companies = df["Company"].unique()
subreddits = ["technology", "stocks"]

for company in companies:
    st.subheader(company)
    cols = st.columns(len(subreddits))  # One column per subreddit
    
    for idx, subreddit in enumerate(subreddits):
        # Filter data for this company and subreddit
        subset = df[(df["Company"] == company) & (df["Subreddit"] == subreddit)]
        sentiments = subset["Sentiment"].values
        sentiment_counts = Counter(sentiments)

        counts = [sentiment_counts.get(cat, 0) for cat in categories]
        total_comments = sum(counts)

        with cols[idx]:
            st.markdown(f"**{subreddit.capitalize()}**")  # Label the subreddit above the chart
            if total_comments > 0:
                percentages = [count / total_comments * 100 for count in counts]
                fig, ax = plt.subplots()
                ax.pie(percentages, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Ensure the pie chart is a circle
                ax.set_title(f"{company} - {subreddit}")
                st.pyplot(fig)

                # Display raw counts
                st.write(f"Total Comments: {total_comments}")
                for cat, count in zip(categories, counts):
                    st.write(f"{cat}: {count}")
            else:
                st.write("No comments found for this subreddit.")
