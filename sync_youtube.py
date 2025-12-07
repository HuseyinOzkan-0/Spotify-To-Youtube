import os
import sys
import pickle
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.append(os.getcwd())
try:
    from spotify_graph.orm import FalkorGraphORM
except ImportError:
    print("❌ Error: ORM not found.")
    sys.exit(1)

# Google Config
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_authenticated_service():
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

def fetch_songs_from_db():
    print("🔌 Connecting to FalkorDB...")
    orm = FalkorGraphORM()
    query = "MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist) RETURN t.title, collect(a.name)"
    result = orm.graph.query(query)
    songs = [f"{row[0]} by {', '.join(row[1])}" for row in result.result_set]
    print(f"✅ Found {len(songs)} songs in database.")
    return songs

def create_playlist(youtube, name):
    print(f"🔨 Creating YouTube Playlist: '{name}'...")
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": name, "description": "From FalkorDB", "defaultLanguage": "en"},
            "status": {"privacyStatus": "private"}
        }
    )
    return request.execute()['id']

def search_and_add(youtube, playlist_id, songs):
    print("🔄 Transferring songs...")
    for song in songs:
        try:
            # 1. Search
            search_response = youtube.search().list(q=song, part="id", type="video", maxResults=1).execute()
            if not search_response['items']:
                print(f"   ❌ Not found: {song}")
                continue
            
            video_id = search_response['items'][0]['id']['videoId']
            
            # 2. Add
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()
            print(f"   ✅ Added: {song}")
            time.sleep(1) # Be nice to API

        except HttpError as e:
            if e.resp.status == 403:
                print("\n🛑 QUOTA EXCEEDED! Come back tomorrow.")
                break
            print(f"   ⚠️ Error: {e}")

if __name__ == "__main__":
    songs = fetch_songs_from_db()
    if songs:
        youtube = get_authenticated_service()
        pl_name = input("Enter Playlist Name: ")
        pl_id = create_playlist(youtube, pl_name)
        search_and_add(youtube, pl_id, songs)
        print("🎉 Done!")