import streamlit as st
from streamlit_card import card
import praw
from datetime import datetime, timedelta
from transformers import BertForSequenceClassification, BertTokenizer
import torch
from datetime import timezone

# Load the model and tokenizer
model_name = "jgranizo/SentimentalModel"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=3,  # Ensure the model supports 3 labels
    ignore_mismatched_sizes=True  # Handle size mismatch in the classifier
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Label mapping
label_mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}  # Adjust as needed

# Function to predict sentiment
def predict_sentence(sentence, model, tokenizer, label_mapping, max_len=128):
    inputs = tokenizer.encode_plus(
        sentence,
        add_special_tokens=True,
        max_length=max_len,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    model.eval()
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

    return label_mapping[predicted_class]

# Streamlit Page Navigation
st.page_link("app.py", label="Home", icon="🏠")
st.page_link("pages/test.py", label="Page 1")



# Dropdown for multiple selections
selected_brands = st.multiselect(
    'Choose your favorite brands',
    ['Apple', 'Microsoft', 'Google', 'Amazon','Tesla'],
    default=['Tesla']
)

# Display the selected brand(s)
if len(selected_brands) == 1:
    st.write(f'You selected: {selected_brands[0]}')  # Single selection
elif len(selected_brands) > 1:
    st.write(f'You selected: {', '.join(selected_brands)}')  # Multiple selections
else:
    st.write("You didn't select any brand.")
# Initialize Reddit API client
reddit = praw.Reddit(
    client_id='ZPr2EshdHCAQUHQ1B4LRdQ',
    client_secret='D_pSNQdQpLFu0xkme74Sket1zGUorg',
    user_agent='BrandDataCollector/1.0 by u/jgran'
)

# Define criteria
brand_name = "Apple"
min_score = 50
min_comments = 20
days_limit = 14
date_limit = datetime.now(timezone.utc) - timedelta(days=days_limit)
timestamp_limit = date_limit.timestamp()

# Search for posts
subreddits = ["technology", "gadgets", "stocks"]
subreddit_dictionary = {}
for brand in selected_brands: 
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.search(brand, limit=100):
            if (post.score >= min_score and
                post.num_comments >= min_comments and
                post.created_utc >= timestamp_limit):

                post_info = {
                "Title": post.title,
                "Score": post.score,
                "Comments": post.num_comments,
                "Created": datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "Subreddit": post.subreddit.display_name,
                "Author": post.author,
                "URL": post.url,
                "Content": post.selftext
                     }

                post.comment_sort = 'top'
                post.comments.replace_more(limit=0)
                top_comments = [comment.body for comment in post.comments if "[deleted]" not in comment.body][:5]

                if post_info['Title'] not in subreddit_dictionary:
                    subreddit_dictionary[post_info['Title']] = {"Comments": {}}

                for comment in top_comments:
                    sentiment = predict_sentence(comment, model, tokenizer, label_mapping)  # Predict sentiment
                    subreddit_dictionary[post_info['Title']]["Comments"][comment] = {"Sentimental_Value": sentiment}

# Display Results in Streamlit
st.markdown(
    """
    <style>
    .title-text {
        font-size: 1.1rem;
        font-weight: bold;
        overflow-wrap: break-word;
        word-wrap: break-word;
        white-space: normal;
    }
    .small-text {
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
post_titles = list(subreddit_dictionary.keys())

for i in range(0, len(post_titles), 2):
    post1_title = post_titles[i]
    post2_title = post_titles[i + 1] if i + 1 < len(post_titles) else None

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<p class='title-text'>{post1_title}</p>", unsafe_allow_html=True)
        comments = list(subreddit_dictionary[post1_title]["Comments"].items())

        # Show first 2 comments by default
        for comment, details in comments[:2]:
            st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-text'>Sentimental Value: {details['Sentimental_Value']}</p>", unsafe_allow_html=True)

        # Add a dropdown for the remaining comments
        if len(comments) > 2:
            with st.expander("View more comments"):
                for comment, details in comments[2:]:
                    st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='small-text'>Sentimental Value: {details['Sentimental_Value']}</p>", unsafe_allow_html=True)

    if post2_title:
        with col2:
            st.markdown(f"<p class='title-text'>{post2_title}</p>", unsafe_allow_html=True)
            comments = list(subreddit_dictionary[post2_title]["Comments"].items())

            # Show first 2 comments by default
            for comment, details in comments[:2]:
                st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='small-text'>Sentimental Value: {details['Sentimental_Value']}</p>", unsafe_allow_html=True)

            # Add a dropdown for the remaining comments
            if len(comments) > 2:
                with st.expander("View more comments"):
                    for comment, details in comments[2:]:
                        st.markdown(f"<p class='small-text'><strong>Comment:</strong> {comment}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='small-text'>Sentimental Value: {details['Sentimental_Value']}</p>", unsafe_allow_html=True)
