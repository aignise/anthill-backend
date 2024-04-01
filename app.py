from flask import Flask, request, jsonify
from final import create_new_post, extract_keywords, extract_posts_from_subreddit

app = Flask(__name__)

@app.route('/extract-keywords', methods=['POST'])
def extract_keywords_route():
    data = request.get_json()
    file_content = data['file_content']
    top_keywords = extract_keywords(file_content)
    return jsonify({"top_keywords": top_keywords})

@app.route('/extract-posts', methods=['POST'])
def extract_posts_route():
    data = request.get_json()
    subreddit_name = data['subreddit_name']
    top_keywords = data['top_keywords']
    posts = extract_posts_from_subreddit(subreddit_name, top_keywords)
    return jsonify({"posts": posts})

@app.route('/create-post', methods=['POST'])
def create_post_route():
    data = request.get_json()
    title = data['title']
    content = data['content']
    subreddit_name = data['subreddit_name']
    post_result = create_new_post(title, content, subreddit_name)
    return jsonify({"result": post_result})

if __name__ == '__main__':
    app.run(debug=True)
