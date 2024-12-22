from googleapiclient.discovery import build
from datetime import timedelta
import isodate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from the environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Make sure it's set in the .env file.")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_duration(video_id):
    """Fetch the duration of a single YouTube video."""
    request = youtube.videos().list(
        part='contentDetails',
        id=video_id
    )
    response = request.execute()

    if response['items']:
        duration = response['items'][0]['contentDetails']['duration']
        return parse_duration(duration)
    else:
        raise ValueError("Invalid Video ID or Video not found.")

def get_playlist_videos_duration(playlist_id):
    """Fetch the total duration of all videos in a YouTube playlist."""
    total_duration = timedelta()

    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        video_ids = [item['contentDetails']['videoId'] for item in response['items']]

        videos_request = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()

        for item in videos_response['items']:
            duration = item['contentDetails']['duration']
            total_duration += parse_duration(duration)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return total_duration

def get_playlist_info(playlist_id):
    """Fetch the title and number of videos in a YouTube playlist."""
    total_videos = 0
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        # Count the number of items (videos) in this response
        total_videos += len(response['items'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    # Fetch playlist title
    playlist_request = youtube.playlists().list(
        part='snippet',
        id=playlist_id
    )
    playlist_response = playlist_request.execute()
    if playlist_response['items']:
        playlist_title = playlist_response['items'][0]['snippet']['title']
        return playlist_title, total_videos
    else:
        raise ValueError("Invalid Playlist ID or Playlist not found.")

def parse_duration(duration):
    """Convert ISO 8601 duration format to timedelta."""
    return isodate.parse_duration(duration)

def extract_video_id_from_url(url):
    """Extract the video ID from a YouTube video URL."""
    if "v=" not in url:
        raise ValueError("Invalid URL. Make sure the video URL is correct.")
    return url.split("v=")[1].split("&")[0]

def extract_playlist_id_from_url(url):
    """Extract the playlist ID from a YouTube playlist URL."""
    if "list=" not in url:
        raise ValueError("Invalid Playlist URL. Make sure the URL contains 'list='.")
    return url.split("list=")[1].split("&")[0]

if __name__ == "__main__":
    print("YouTube Duration Calculator")
    print("1. Get the duration of a single video")
    print("2. Get the total duration of a playlist")
    print("3. Get playlist information (title and number of videos)")
    choice = input("Enter your choice (1, 2, or 3): ")

    try:
        if choice == "1":
            video_url = input("Enter the YouTube Video URL: ")
            video_id = extract_video_id_from_url(video_url)
            duration = get_video_duration(video_id)
            print(f"The duration of the video is: {duration}")
        elif choice == "2":
            playlist_url = input("Enter the YouTube Playlist URL: ")
            playlist_id = extract_playlist_id_from_url(playlist_url)
            total_time = get_playlist_videos_duration(playlist_id)
            print(f"The total duration of the playlist is: {total_time}")
        elif choice == "3":
            playlist_url = input("Enter the YouTube Playlist URL: ")
            playlist_id = extract_playlist_id_from_url(playlist_url)
            title, total_videos = get_playlist_info(playlist_id)
            print(f"Playlist Title: {title}")
            print(f"Total Number of Videos: {total_videos}")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    except Exception as e:
        print(f"Error: {e}")
