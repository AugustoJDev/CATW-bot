import sys
import codecs
import instaloader
import json
import re
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Load environment variables from .env file
load_dotenv()

# Set encoding to UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Initialize Instaloader
loader = instaloader.Instaloader()

# Get Instagram credentials from environment variables
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Function to open the challenge URL in a browser using Selenium
def open_challenge_url(url):
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
    driver.get(url)
    print("Please complete the challenge in the browser window that opened.")
    while True:
        time.sleep(10)  # Wait for the user to complete the challenge
        if "checkpoint" not in driver.current_url:
            break
    driver.quit()

# Login to Instagram
try:
    loader.load_session_from_file(USERNAME)
    print("🚧 Debug: Session loaded successfully", file=sys.stderr)
except FileNotFoundError:
    try:
        loader.login(USERNAME, PASSWORD)
        loader.save_session_to_file()
        print("🚧 Debug: Logged in and session saved successfully", file=sys.stderr)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("🚧 Debug: Two-factor authentication required. Please complete the challenge.", file=sys.stderr)
        challenge_url = f"https://www.instagram.com/accounts/login/?next=/challenge/"
        open_challenge_url(challenge_url)
        sys.exit(1)
    except instaloader.exceptions.LoginRequiredException as e:
        print(f"🚧 Debug: Login failed: {e}", file=sys.stderr)
        challenge_url = f"https://www.instagram.com{e.url}"
        open_challenge_url(challenge_url)
        sys.exit(1)
    except Exception as e:
        print(f"🚧 Debug: Login failed: {e}", file=sys.stderr)
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
        print(f"🚧 Debug: Received URL: {url}", file=sys.stderr)
        print(f"🚧 Debug: Identified type: {type}", file=sys.stderr)
        
        if type == "story":
            match = re.search(r'instagram\.com/stories/[^/]+/([^/?]+)', url)
            if not match:
                print("🚧 Debug: No match found for URL", file=sys.stderr)
                return json.dumps({"error": "Invalid URL"})
            
            user = re.search(r'instagram\.com/stories/([^/]+)/', url).group(1)
            story_id = match.group(1)
            print(f"🚧 Debug: Extracted user: {user}, story_id: {story_id}", file=sys.stderr)

            profile = instaloader.Profile.from_username(loader.context, user)
            for story in loader.get_stories(userids=[profile.userid]):
                for item in story.get_items():
                    if item.mediaid == int(story_id):
                        data = {
                            "type": type,
                            "author": profile.username,
                            "description": item.caption or "",
                            "author_image": profile.profile_pic_url or "",
                            "thumbnail": item.url or ""
                        }
                        return json.dumps(data, ensure_ascii=False)
            return json.dumps({"error": "Story not found"})
        else:
            match = re.search(r'instagram\.com/(?:p|tv|reels|reel)/([^/?]+)', url)
            if not match:
                print("🚧 Debug: No match found for URL", file=sys.stderr)
                return json.dumps({"error": "Invalid URL"})

            shortcode = match.group(1)  # Post/reel code
            print(f"🚧 Debug: Extracted shortcode: {shortcode}", file=sys.stderr)

            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            data = {
                "type": type,
                "author": post.owner_profile.username,
                "description": post.caption or "",
                "author_image": post.owner_profile.profile_pic_url or "",
                "thumbnail": post.url or ""
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