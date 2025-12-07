import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Add current folder to path so we can import spotify_graph
sys.path.append(os.getcwd())

try:
    from spotify_graph.orm import FalkorGraphORM
    from spotify_graph.items import Playlist, Track, Album, Artist
except ImportError as e:
    print(f"❌ Error importing ORM: {e}")
    sys.exit(1)

# ⚠️ PASTE YOUR SPOTIFY KEYS HERE
SPOTIPY_CLIENT_ID = '46d727888f474006ba0e9caba6b23d1f'
SPOTIPY_CLIENT_SECRET = '9e0e1ac7cc3e4f37a2a605d6a28b061f'

def run_spotify_api():
    print("🔑 Authenticating with Spotify...")
    auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # SEARCH for the playlist
    search_query = "Today's Top Hits"
    print(f"🔍 Searching for: '{search_query}'...")
    results = sp.search(q=search_query, type='playlist', limit=1)
    
    if not results['playlists']['items']:
        print("❌ Playlist not found.")
        return

    target_playlist = results['playlists']['items'][0]
    playlist_id = target_playlist['id']
    print(f"✅ Found: '{target_playlist['name']}'")

    # Fetch Tracks
    print("⬇️ Downloading track list...")
    pl_data = sp.playlist(playlist_id)
    tracks_list = []
    
    for item in pl_data['tracks']['items']:
        track = item.get('track')
        if not track or track['id'] is None: continue

        # Convert to our Objects
        alb = track['album']
        album_obj = Album(id=alb['id'], name=alb['name'], image_url=alb['images'][0]['url'] if alb['images'] else None)
        artists_obj = [Artist(id=a['id'], name=a['name']) for a in track['artists']]
        
        track_obj = Track(
            id=track['id'], title=track['name'], duration_ms=track['duration_ms'],
            popularity=track['popularity'], album=album_obj, artists=artists_obj
        )
        tracks_list.append(track_obj)

    # Save to Database
    final_playlist = Playlist(id=pl_data['id'], name=pl_data['name'], description=pl_data['description'], tracks=tracks_list)
    
    print(f"💾 Saving {len(tracks_list)} tracks to FalkorDB...")
    orm = FalkorGraphORM()
    orm.save_playlist(final_playlist)
    print("🎉 SUCCESS! Data saved.")

if __name__ == "__main__":
    run_spotify_api()