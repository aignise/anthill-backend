import tkinter as tk
from tkinter import filedialog
import praw
from openai import OpenAI
import time
import json
import re
from nltk.corpus import stopwords
import requests
import httpx


reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret,
                     username=reddit_username,
                     password=reddit_password,
                     user_agent=reddit_user_agent)

openai_client = OpenAI(api_key=openai_api_key)

client = OpenAI(api_key='#your apikey')

file_path = filedialog.askopenfilename()  

with open(file_path, "rb") as file:
    file = client.files.create(
        file=file,
        purpose='assistants'
    )

top_keywords= []

def setup():
    assistant = client.beta.assistants.create(
        name="Reddit Marketing Automation",
        instructions="You are a bot to manage reddit marketing for a firm",
        model="gpt-4-turbo-preview",
        file_ids=[file.id],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_new_post",
                    "description": "creates a new post on the reddit page of the company",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string", 
                                "description": "Title of the post"
                            },
                            "content": {
                                "type": "string", 
                                "description": "Content of the post"
                            },
                            "subreddit_name": {
                                "type": "string", 
                                "description": "Category of subreddit to post"
                            }
                        },
                        "required": ["title","content","subreddit_name"]
                    }
                }
            },
            {
                    "name": "extract_keywords",
                    "description": "extract the 5 most important keywords from the given string or file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "Text to which keywords need to be extracted from"
                        }
                        },
                        "required": [
                        "file_content"
                        ]
                    }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_posts_from_subreddit",
                    "description": "Extracts posts from the specified subreddit based on top keywords.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subreddit_name": {
                                "type": "string",
                                "description": "Name of the subreddit to extract posts from."
                            },
                            "top_keywords": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of top keywords to search for."
                            }
                        },
                        "required": ["subreddit_name", "top_keywords"]
                        }
                    }
                },
        ]
    )

    return assistant.id

def create_thread():
    thread = client.beta.threads.create()
    return thread.id

assistant_id = "#yourassistantid"
thread_id = "thread_oWVUlvrYVJitWFoP6w59FtQ"
prompt ="Extract keywords and subreddits from the document and create a reddit post on the keywords"

def start(thread_id , prompt):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

def get_response(thread_id, assistant_id):
    
    run = client.beta.threads.runs.create(
      thread_id=thread_id,
      assistant_id=assistant_id,
      tools=[{"type": "retrieval"}],
      instructions="Answer user questions using custom functions available to you.",
    )
    
    # Wait for the run to complete
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    while run_status.status != "completed":
        
        if run_status.status == 'requires_action':
            
            def get_outputs_for_tool_call(tool_call):
                print(type(tool_call.function.arguments))
                if tool_call.function.name == "extract_keywords":
                    file_content = tool_call.function.arguments["file_content"]
                    output = extract_keywords(file_content)
                elif tool_call.function.name == "extract_posts_from_subreddit":
                    subreddit_name = tool_call.function.arguments["subreddit_name"]
                    top_keywords = tool_call.function.arguments["top_keywords"]
                    output = extract_posts_from_subreddit(subreddit_name, top_keywords)
                elif tool_call.function.name == "create_new_post":
                    title = tool_call.function.arguments["title"]
                    content = tool_call.function.arguments["content"]
                    subreddit_name = tool_call.function.arguments["subreddit_name"]
                    output = create_new_post(title, content, subreddit_name)
                elif tool_call.function.name == "file_retrieval":
                    file_path_url = tool_call.function.arguments["file_path_url"]
                    output = retrieve_file_content(file_path_url)
                    
                if "subreddit doesn't exist" in output:
                        # Ask for another subreddit name
                        new_subreddit_name = input("The specified subreddit doesn't exist. Please enter another subreddit name: ")
                        output = create_new_post(title, content, new_subreddit_name)
                else:
                    output = None

                return {
                    "tool_call_id": tool_call.id,
                    "output": output
                }


            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
            tool_outputs = map(get_outputs_for_tool_call, tool_calls)
            tool_outputs = list(tool_outputs)

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        time.sleep(1)
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Retrieve the latest message from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    return response

############# ALL CUSTOM FUNCTIONS HERE
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

def extract_posts_from_subreddit(subreddit_name, top_keywords):
    try:
        target_subreddit = reddit.subreddit(subreddit_name)
        post_results = list(target_subreddit.search(top_keywords, sort='new', limit=5))
        post_info = [{'title': post.title, 'url': post.url} for post in post_results]
        return post_info
    except Exception as e:
        return f"Failed to extract posts from the subreddit. Error: {str(e)}"
    
def create_new_post(title, content, subreddit_name):
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


thread_id = create_thread()
start(thread_id, prompt)

print(get_response(thread_id, assistant_id))
