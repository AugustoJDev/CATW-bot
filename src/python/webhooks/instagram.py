import sys
import json
import re
from instagrapi import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Instagram credentials from environment variables
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Initialize Instagrapi Client
client = Client()

# Path to the session file
SESSION_FILE = './session.json'

# Function to save session
def save_session(client, session_file):
    with open(session_file, 'w') as f:
        json.dump(client.get_settings(), f)

# Function to load session
def load_session(client, session_file):
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            settings = json.load(f)
        client.set_settings(settings)
        client.login(USERNAME, PASSWORD)

# Login to Instagram
try:
    load_session(client, SESSION_FILE)
    if not client.user_id:
        client.login(USERNAME, PASSWORD)
        save_session(client, SESSION_FILE)
    print("Debug: Logged in successfully", file=sys.stderr)
except Exception as e:
    print(f"Debug: Login failed: {e}", file=sys.stderr)
    sys.exit(1)

# Function to identify the type of URL
def identify_type(url):
    if "/p/" in url or "/tv/" in url:  # Post or IGTV
        return "post"
    elif "/stories/" in url:  # Stories
        return "story"
    elif "/reels/" in url or "/reel/" in url:  # Reels
        return "reel"
    else:
        return "unknown"

# Function to extract information from Instagram
def get_instagram_info(url):
    type = identify_type(url)

    try:
        print(f"Debug: Received URL: {url}", file=sys.stderr)
        print(f"Debug: Identified type: {type}", file=sys.stderr)
        
        if type == "story":
            match = re.search(r'instagram\.com/stories/[^/]+/([^/?]+)', url)
            if not match:
                print("Debug: No match found for URL", file=sys.stderr)
                return json.dumps({"error": "Invalid URL"})
            
            user = re.search(r'instagram\.com/stories/([^/]+)/', url).group(1)
            story_id = match.group(1)
            print(f"Debug: Extracted user: {user}, story_id: {story_id}", file=sys.stderr)

            user_id = client.user_id_from_username(user)
            print(f"Debug: Extracted user_id: {user_id}", file=sys.stderr)
            stories = client.user_stories(user_id)
            print(f"Debug: Retrieved stories: {stories}", file=sys.stderr)
            for story in stories:
                print(f"Debug: Checking story: {story.pk}", file=sys.stderr)
                if story.pk == int(story_id):
                    data = {
                        "type": type,
                        "author": user,
                        "description": story.caption_text or "",
                        "author_image": client.user_info(user_id).profile_pic_url,
                        "thumbnail": story.thumbnail_url
                    }
                    return json.dumps(data, ensure_ascii=False)
            return json.dumps({"error": "Story not found"})
        
        elif type == "post" or type == "reel":
            match = re.search(r'instagram\.com/(?:p|tv|reels|reel)/([^/?]+)', url)
            if not match:
                print("Debug: No match found for URL", file=sys.stderr)
                return json.dumps({"error": "Invalid URL"})

            shortcode = match.group(1)  # Post/reel code
            print(f"Debug: Extracted shortcode: {shortcode}", file=sys.stderr)

            post = client.media_info(shortcode)

            data = {
                "type": type,
                "author": post.user.username,
                "description": post.caption_text or "",
                "author_image": post.user.profile_pic_url,
                "thumbnail": post.thumbnail_url
            }
            return json.dumps(data, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = get_instagram_info(url)
        print(result)
    else:
        print(json.dumps({"error": "No URL received"}))