import sys
import codecs
import instaloader
import json
import re

# Set encoding to UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Initialize Instaloader
loader = instaloader.Instaloader()

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
        else:
            match = re.search(r'instagram\.com/(?:p|tv|reels|reel)/([^/?]+)', url)
        
        if not match:
            print("Debug: No match found for URL", file=sys.stderr)
            return json.dumps({"error": "Invalid URL"})

        shortcode = match.group(1)  # Post/story/reel code
        print(f"Debug: Extracted shortcode: {shortcode}", file=sys.stderr)

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