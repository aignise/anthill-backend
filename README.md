# Reddit Marketing Automation with OpenAI

This project utilizes the OpenAI API to automate Reddit marketing tasks. It allows users to extract keywords and subreddit names from a document, and create Reddit posts based on the extracted data.

# Extract Keywords Function

This Python function `extract_keywords` extracts the top 5 keywords from the provided text content.

## Parameters

- `file_content`: The text content from which keywords are to be extracted.

## Returns

The function returns a list of the top 5 keywords based on their frequency in the text content.

# Extract Posts from Subreddit Function

This Python function `extract_posts_from_subreddit` retrieves posts from a specified subreddit based on given keywords.

## Parameters

- `reddit`: The Reddit instance.
- `subreddit_name`: The name of the subreddit to search in.
- `top_keywords`: A list of top keywords to use for searching posts.

## Returns

The function returns a list of dictionaries containing information about the retrieved posts, including title and URL.

# Create New Post Function

This Python function `create_new_post` creates a new post on Reddit in a specified subreddit.

## Parameters

- `reddit`: The Reddit instance.
- `title`: The title of the post.
- `content`: The content of the post.
- `subreddit_name`: The name of the subreddit where the post will be created.

## Returns

The function returns a success message along with the permalink of the created post if successful. If there's an error, it returns an appropriate error message.

# Retrieve File Content Function

This Python function `retrieve_file_content` retrieves the content of a file from a given URL.

## Parameters

- `file_path_url`: The URL from which to retrieve the file content.

## Returns

The function returns the content of the file if successful. If there's an error, it returns an appropriate error message.

## Features

- Extract keywords and subreddit names from a document.
- Create Reddit posts based on the extracted keywords and subreddit names.

## Usage

1. Clone the repository:

- git clone https://github.com/your-username/reddit-marketing-automation.git

2. Install dependencies:
pip install -r requirements.txt


## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
