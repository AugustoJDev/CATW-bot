import sys
import json
import re
import instaloader
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Instagram credentials from environment variables
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Initialize Instaloader
loader = instaloader.Instaloader()

# Path to the session file
SESSION_FILE = './session.json'
COOKIES_FILE = './cookies.json'

# Function to save session
def save_session(loader, session_file):
    loader.save_session_to_file(session_file)

# Function to load session
def load_session(loader, session_file):
    if os.path.exists(session_file):
        loader.load_session_from_file(session_file)

# Function to load cookies
def load_cookies(loader, cookies_file):
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            loader.context._session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

# Login to Instagram
try:
    load_session(loader, SESSION_FILE)
    if not loader.context.is_logged_in:
        load_cookies(loader, COOKIES_FILE)
        if not loader.context.is_logged_in:
            loader.login(USERNAME, PASSWORD)
            save_session(loader, SESSION_FILE)
    print("Debug: Logged in successfully", file=sys.stderr)
except Exception as e:
    print(f"Debug: Login failed: {e}", file=sys.stderr)
    sys.exit(1)

# Function to identify the type of URL
def identify_type(url):
    if "/p/" in url or "/tv/" in url:  # Post or IGTV
        return "post"
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
        
        if type == "post" or type == "reel":
            match = re.search(r'instagram\.com/(?:p|tv|reels|reel)/([^/?]+)', url)
            if not match:
                print("Debug: No match found for URL", file=sys.stderr)
                return json.dumps({"error": "Invalid URL"})

            shortcode = match.group(1)  # Post/reel code
            print(f"Debug: Extracted shortcode: {shortcode}", file=sys.stderr)

            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            data = {
                "type": type,
                "author": post.owner_username,
                "description": post.caption or "",
                "author_image": post.owner_profile.profile_pic_url,
                "thumbnail": post.url,
                "taken_at": post.date_utc.isoformat(),
                "media_type": post.typename,
                "product_type": post.product_type
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