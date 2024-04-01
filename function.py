import requests
import re
import praw
from nltk.corpus import stopwords
import os
from dotenv import load_dotenv

load_dotenv()

def extract_keywords(file_content):
    words = re.findall(r'\b\w{4,}\b', file_content.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    word_frequency = {}
    for word in filtered_words:
        if word in word_frequency:
            word_frequency[word] += 1
        else:
            word_frequency[word] = 1
    sorted_keywords = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [keyword for keyword, _ in sorted_keywords[:5]]
    return top_keywords

def extract_posts_from_subreddit(reddit, subreddit_name, top_keywords):
    try:
        target_subreddit = reddit.subreddit(subreddit_name)
        post_results = list(target_subreddit.search(top_keywords, sort='new', limit=5))
        post_info = [{'title': post.title, 'url': post.url} for post in post_results]
        return post_info
    except Exception as e:
        return f"Failed to extract posts from the subreddit. Error: {str(e)}"
    
def create_new_post(reddit, title, content, subreddit_name):
    try:
        target_subreddit = reddit.subreddit(subreddit_name)
        submission = target_subreddit.submit(title, selftext=content)
        return f"Successfully created a new post: https://www.reddit.com{submission.permalink}"
    except praw.exceptions.APIException as e:
        if 'SUBREDDIT_NOEXIST' in str(e):
            return f"Failed to create a new post on Reddit. Error: Subreddit doesn't exist."
        else:
            return f"Failed to create a new post on Reddit. Error: {str(e)}"

def retrieve_file_content(file_path_url):
    try:
        response = requests.get(file_path_url)
        if response.status_code == 200:
            file_content = response.text
            return file_content
        else:
            return f"Failed to retrieve file content. Status Code: {response.status_code}"
    except Exception as e:
        return f"Failed to retrieve file content. Error: {str(e)}"
