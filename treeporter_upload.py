import os
import requests
import base64

# This script demonstrates uploading a file to GitHub without using Git commands,
# mimicking the core functionality of Treeporter.

# --- Configuration ---
# Replace with your GitHub Personal Access Token (PAT)
# Ensure your PAT has the 'repo' scope enabled.
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Replace with the target repository owner and name
REPO_OWNER = "your_github_username"
REPO_NAME = "your_repository_name"

# Replace with the desired path and filename in the repository
FILE_PATH_IN_REPO = "path/to/your/file.txt"

# Replace with the local path to the file you want to upload
LOCAL_FILE_PATH = "local_file.txt"

# Commit message
COMMIT_MESSAGE = "Upload file via Treeporter-like script"

# --- Helper Function to get file SHA ---
def get_file_sha(token, owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['sha']
    elif response.status_code == 404:
        return None  # File doesn't exist yet
    else:
        response.raise_for_status() # Raise an exception for other errors

# --- Main Upload Function ---
def upload_file_to_github(token, owner, repo, file_path_in_repo, local_file_path, commit_message):
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")

    # Read the local file content and encode it in base64
    with open(local_file_path, "rb") as f:
        file_content = f.read()
    encoded_content = base64.b64encode(file_content).decode('utf-8')

    # Get the SHA of the file if it already exists in the repository
    # This is necessary for updating an existing file.
    sha = get_file_sha(token, owner, repo, file_path_in_repo)

    # Construct the API endpoint URL
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path_in_repo}"

    # Prepare the request payload
    payload = {
        "message": commit_message,
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha # Include SHA if updating an existing file

    # Set the headers for authentication and content type
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Make the PUT request to upload/update the file
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"File '{local_file_path}' successfully uploaded to '{file_path_in_repo}' in '{owner}/{repo}'.")
    else:
        print(f"Error uploading file: {response.status_code}")
        print(response.json())

# --- Example Usage ---
if __name__ == "__main__":
    # Create a dummy local file for demonstration if it doesn't exist
    if not os.path.exists(LOCAL_FILE_PATH):
        with open(LOCAL_FILE_PATH, "w") as f:
            f.write("This is a test file to upload to GitHub without Git commands.\n")
        print(f"Created dummy file: {LOCAL_FILE_PATH}")

    try:
        upload_file_to_github(
            GITHUB_TOKEN,
            REPO_OWNER,
            REPO_NAME,
            FILE_PATH_IN_REPO,
            LOCAL_FILE_PATH,
            COMMIT_MESSAGE
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
