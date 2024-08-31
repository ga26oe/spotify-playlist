import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Load environment variables
load_dotenv()

# Spotify API setup
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)

# YouTube API setup
youtube_api_key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

def get_track_info(spotify_link):
    # Extract track ID from Spotify link
    track_id = spotify_link.split('/')[-1].split('?')[0]
    
    # Get track information from Spotify
    track = sp.track(track_id)
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    
    return f"{track_name} {artist_name}"

def get_youtube_comments(video_id):
    comments = []
    try:
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            order="relevance",
            maxResults=100
        ).execute()
        
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([
                comment['authorDisplayName'],
                comment['publishedAt'],
                comment['updatedAt'],
                comment['likeCount'],
                comment['textDisplay']
            ])
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return comments

def main():
    spotify_link = input("Enter Spotify song link: ")
    track_info = get_track_info(spotify_link)
    
    print(f"Searching YouTube for: {track_info}")
    
    # Search YouTube for the track
    search_response = youtube.search().list(
        q=track_info,
        type="video",
        part="id,snippet",
        maxResults=1
    ).execute()
    
    if search_response['items']:
        video_id = search_response['items'][0]['id']['videoId']
        video_title = search_response['items'][0]['snippet']['title']
        print(f"Found YouTube video: {video_title}")
        
        comments = get_youtube_comments(video_id)
        df = pd.DataFrame(comments, columns=['author', 'published_at', 'updated_at', 'like_count', 'text'])
        
        print("\nTop YouTube comments:")
        print(df.to_string(index=False))
    else:
        print("No YouTube video found for this track.")

if __name__ == "__main__":
    main()