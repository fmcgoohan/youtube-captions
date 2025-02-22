import json
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Supports formats like:
    - https://www.youtube.com/watch?v=video_id
    - https://youtu.be/video_id
    - https://www.youtube.com/v/video_id
    Returns None if the URL is invalid or not a YouTube URL.
    """
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """
    Retrieves English captions for a given video ID using youtube-transcript-api.
    Returns the concatenated text or None if no captions are available.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return ' '.join([item['text'] for item in transcript])
    except Exception:
        return None

def handler(request):
    """
    Handles the incoming POST request, processes the YouTube URL, and returns a JSON response.
    Expects a JSON body with a 'url' field containing the YouTube URL.
    """
    try:
        data = json.loads(request['body'])
        url = data.get('url')
        if not url:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': False, 'message': 'No URL provided'})
            }
        video_id = extract_video_id(url)
        if not video_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': False, 'message': 'Invalid URL'})
            }
        transcript = get_transcript(video_id)
        if transcript:
            return {
                'statusCode': 200,
                'body': json.dumps({'status': True, 'captions': transcript})
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'status': False, 'message': 'No captions available'})
            }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': False, 'message': 'Invalid JSON'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'status': False, 'message': 'Internal server error'})
        }