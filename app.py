import streamlit as st
from googleapiclient.discovery import build
from datetime import timedelta
import isodate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from the environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY")
# if not API_KEY:
#     raise ValueError("API key not found. Make sure it's set in the .env file.")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_duration(video_id):
    """Fetch the duration and title of a single YouTube video."""
    request = youtube.videos().list(
        part='snippet,contentDetails',
        id=video_id
    )
    response = request.execute()

    if response['items']:
        video = response['items'][0]
        title = video['snippet']['title']
        duration = video['contentDetails']['duration']
        return title, parse_duration(duration)
    else:
        raise ValueError("Invalid Video ID or Video not found.")

def get_playlist_videos_duration(playlist_id):
    """Fetch the total duration and video titles of all videos in a YouTube playlist."""
    total_duration = timedelta()
    video_details = []

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
            part='snippet,contentDetails',
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()

        for item in videos_response['items']:
            title = item['snippet']['title']
            duration = item['contentDetails']['duration']
            video_details.append((title, parse_duration(duration)))
            total_duration += parse_duration(duration)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return total_duration, video_details

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

# Streamlit App UI
st.title("YouTube Video/Playlist Duration Calculator")
st.write("This app allows you to get the total duration of a playlist or a single video, as well as playlist info.")

choice = st.radio("Choose an option:", ["Get the duration of a single video", "Get the total duration of a playlist", "Get playlist information"])

if choice == "Get the duration of a single video":
    video_url = st.text_input("Enter YouTube Video URL:")
    if video_url:
        video_id = extract_video_id_from_url(video_url)
        try:
            title, duration = get_video_duration(video_id)
            st.write(f"Video Title: {title}")
            st.write(f"The duration of the video is: {duration}")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "Get the total duration of a playlist":
    playlist_url = st.text_input("Enter YouTube Playlist URL:")
    if playlist_url:
        playlist_id = extract_playlist_id_from_url(playlist_url)
        try:
            total_time, video_details = get_playlist_videos_duration(playlist_id)
            st.write(f"The total duration of the playlist is: {total_time}")
            st.write("Video Titles and Durations:")
            for title, duration in video_details:
                st.write(f"{title} - {duration}")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "Get playlist information":
    playlist_url = st.text_input("Enter YouTube Playlist URL:")
    if playlist_url:
        playlist_id = extract_playlist_id_from_url(playlist_url)
        try:
            title, total_videos = get_playlist_info(playlist_id)
            st.write(f"Playlist Title: {title}")
            st.write(f"Total Number of Videos: {total_videos}")
        except Exception as e:
            st.error(f"Error: {e}")