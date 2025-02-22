import json
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Supports formats like:
    - https://www.youtube.com/watch?v=video_id
    - https://www.youtube.com/v/video_id
    - https://youtu.be/video_id
    """
    patterns = [
        r'v=([\w-]+)',          # Matches v=video_id
        r'/v/([\w-]+)',         # Matches /v/video_id
        r'youtu\.be/([\w-]+)',  # Matches youtu.be/video_id
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(vid_id):
    """
    Retrieves English captions for a given video ID using youtube-transcript-api.
    Returns the concatenated text or None if no captions are available.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
        transcript_text = ' '.join([item['text'] for item in transcript])
        return transcript_text
    except (Exception):
        # Handles cases like TranscriptsDisabled or NoTranscriptFound
        return None

def handle_request(request):
    """
    Handles the incoming POST request, processes the URL, and returns a JSON response.
    """
    try:
        # Parse the JSON body from the request
        data = json.load(request.body)
        url = data.get('url')
        
        # Check if URL is provided
        if not url:
            return {
                'status': 400,
                'body': json.dumps({'status': False, 'message': 'No URL provided'})
            }
        
        # Extract video ID
        vid_id = extract_video_id(url)
        if not vid_id:
            return {
                'status': 400,
                'body': json.dumps({'status': False, 'message': 'Invalid URL'})
            }
        
        # Fetch captions
        captions = get_transcript(vid_id)
        if captions:
            return {
                'status': 200,
                'body': json.dumps({'status': True, 'captions': captions})
            }
        else:
            return {
                'status': 200,
                'body': json.dumps({'status': False, 'message': 'No captions available'})
            }
    
    except json.JSONDecodeError:
        # Handle malformed JSON in the request body
        return {
            'status': 400,
            'body': json.dumps({'status': False, 'message': 'Invalid JSON'})
        }
    except Exception as e:
        # Catch unexpected errors
        return {
            'status': 500,
            'body': json.dumps({'status': False, 'message': 'Internal server error'})
        }

# Vercel expects a function to be wrapped with create_app for the Python runtime
from vercel_runtime import create_app
app = create_app(handle_request)