"""
YouTube Sync Module.

Handles authentication with Google/YouTube API and syncing of songs
from the FalkorDB database to a new YouTube Playlist.
"""
import os
import sys
import pickle
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from spotify_graph.orm import FalkorGraphORM

sys.path.append(os.getcwd())

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_authenticated_service():
    """Authenticates with YouTube API and returns the service object."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def fetch_songs():
    """Query the Graph Database to get all songs in the format 'Title by Artist(s)'."""
    print("🔌 Connecting to Database...")
    orm = FalkorGraphORM()
    query = "MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist) RETURN t.title, collect(a.name)"
    result = orm.graph.query(query)
    # Check if result is empty
    if not result.result_set:
        print("⚠️ Database is empty. Run run_api.py first.")
        return []
    
    songs = [f"{row[0]} by {', '.join(row[1])}" for row in result.result_set]
    print(f"✅ Found {len(songs)} songs to transfer.")
    return songs

def create_pl(youtube, name):
    """Create a private YouTube playlist and return its ID."""
    print(f"🔨 Creating Playlist: '{name}'...")
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": name, "description": "From FalkorDB", "defaultLanguage": "en"},
            "status": {"privacyStatus": "private"}
        }
    )
    return request.execute()['id']

def sync_songs(youtube, pl_id, songs):
    """
    Search for each song on YouTube and add it to the playlist.
    
    Includes error handling and rate limit prevention.
    """
    print("🔄 Adding songs to YouTube...")
    for song in songs:
        try:
            # Search
            search = youtube.search().list(q=song, part="id", type="video", maxResults=1).execute()
            if not search['items']:
                print(f"   ❌ Not found: {song}")
                continue
            
            vid_id = search['items'][0]['id']['videoId']
            
            # Add
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": pl_id,
                        "resourceId": {"kind": "youtube#video", "videoId": vid_id}
                    }
                }
            ).execute()
            print(f"   ✅ Added: {song}")
            time.sleep(1.5) # Prevent Quota Errors

        except HttpError as e:
            if e.resp.status == 403:
                print("\n🛑 QUOTA EXCEEDED! Come back tomorrow.")
                break
            print(f"   ⚠️ Error: {e}")

if __name__ == "__main__":
    songs_data = fetch_songs()
    if songs_data:
        yt_service = get_authenticated_service()
        pl_name = input("Enter YouTube Playlist Name: ")
        playlist_id = create_pl(yt_service, pl_name)
        sync_songs(yt_service, playlist_id, songs_data)
        print("🎉 Done!")