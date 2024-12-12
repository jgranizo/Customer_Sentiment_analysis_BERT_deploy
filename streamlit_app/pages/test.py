import boto3
import json
from datetime import datetime
import streamlit as st
import pandas as pd
import json
import os
file_name = "brand_data_with_sentiment_2024-12-12.json" 

# Open and load the JSON data


current_dir = os.path.dirname(os.path.abspath(__file__))

# Step 2: Navigate to the parent directory (streamlit/) where text.json resides
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Step 3: Construct the full path to text.json
file_path = os.path.join(parent_dir, file_name)


try:
    files_in_dir = os.listdir(current_dir)
except Exception as e:
    st.error(f"Error accessing directory: {e}")

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

st.markdown("[Go Home](./)")
# Extract data into a DataFrame
records = []
for company, posts in reddit_data.items():
    for post_title, post_content in posts.items():
        post_info = post_content.get('Post_Info', {})
        subreddit = post_info.get('Subreddit', 'Unknown')
        comments = post_content.get('Comments', {})
        
        for comment_text, comment_details in comments.items():
            sentiment = comment_details.get('Sentimental_Value', 'Neutral')
            records.append({
                "Company": company,
                "Subreddit": subreddit,
                "Sentiment": sentiment
            })

df = pd.DataFrame(records)

# Filter only the subreddits we care about: "technology", "stocks"
df = df[df["Subreddit"].isin(["technology", "stocks"])]

st.header("Comment Sentiment Distribution by Company and Subreddit")

# Multiselect for selecting companies to display
options = st.multiselect(
    "Select Companies to Display",
    ['Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla', 'Twitter']
)

# Iterate through companies and display only selected ones
for company, posts in reddit_data.items():
    # **Updated Condition:**
    # If options are selected and the current company is NOT in options, skip it
    if options and company not in options:
        continue

    st.subheader(f"Company: {company}")

    post_titles = list(posts.keys())

    # Iterate through posts in pairs to display side by side
    for i in range(0, len(post_titles), 2):
        post1_title = post_titles[i]
        post2_title = post_titles[i + 1] if i + 1 < len(post_titles) else None

        # Create two columns
        col1, col2 = st.columns(2)

        # Function to display a post and its comments
        def display_post(col, post_title):
            with col:
                st.markdown(f"<p class='title-text'>{post_title}</p>", unsafe_allow_html=True)
                comments = list(posts[post_title]["Comments"].items())

                # Show first 2 comments by default
                for comment, details in comments[:2]:
                    st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='small-text'>Sentimental Value: {details.get('Sentimental_Value', 'N/A')}</p>", unsafe_allow_html=True)

                # Add a dropdown for the remaining comments
                if len(comments) > 2:
                    with st.expander("View more comments"):
                        for comment, details in comments[2:]:
                            st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p class='small-text'>Sentimental Value: {details.get('Sentimental_Value', 'N/A')}</p>", unsafe_allow_html=True)

        # Display the first post
        display_post(col1, post1_title)

        # Display the second post if it exists
        if post2_title:
            display_post(col2, post2_title)

    st.markdown("---")  # Separator between companies

# Navigation links (if needed)
st.markdown("---")
st.markdown("[Home](/) | [Page 1](test)")