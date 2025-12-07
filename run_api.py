"""
Spotify Ingestion Module.

This module handles the authentication with Spotify and fetching of playlist,
track, album, and artist data. It prepares objects for insertion into the Graph DB.
"""
import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
from spotify_graph.orm import FalkorGraphORM
from spotify_graph.items import Playlist, Track, Album, Artist

# Ensure we can import local modules
sys.path.append(os.getcwd())

# Configuration
SPOTIPY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET

def extract_playlist_id(url_or_id):
    """Cleans the input to find the real Playlist ID."""
    # If user pastes a full URL like: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    if "spotify.com" in url_or_id:
        # Split by '/' and get the last part, then remove any query parameters '?'
        return url_or_id.split("playlist/")[-1].split("?")[0]
    return url_or_id

def ingest_playlist(url=None):
    print("🧹 Preparing Database...")
    try:
        # Initialize ORM early to clear old data
        orm_init = FalkorGraphORM()
        orm_init.clear_database()
    except Exception as e:
        print(f"⚠️ Warning: Could not clear database (is it running?): {e}")

    print("🔑 Authenticating with Spotify...")
    try:
        auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        return None

    # --- INPUT: ASK USER FOR URL ---
    if not url:
        url = input("\n🔗 Paste the Spotify Playlist URL here: ").strip()
    
    if not url:
        print("❌ No URL provided.")
        return None

    playlist_id = extract_playlist_id(url)
    print(f"🔍 Looking up Playlist ID: {playlist_id}...")

    # FETCH TRACKS
    try:
        pl_data = sp.playlist(playlist_id)
    except Exception as e:
        print(f"❌ Could not find playlist. Is the link correct?\nError: {e}")
        return

    print(f"✅ Found: '{pl_data['name']}'")
    print("⬇️ Fetching tracks...")

    tracks_list = []
    # Loop through tracks
    for item in pl_data['tracks']['items']:
        t = item.get('track')
        if not t or not t.get('id'): continue

        # Build Album
        alb = t.get('album', {})
        img = alb['images'][0]['url'] if alb.get('images') else None
        
        album_obj = Album(
            id=alb.get('id', 'unknown'), 
            name=alb.get('name', 'Unknown'), 
            image_url=img
        )

        # Build Artists
        artists_obj = [
            Artist(id=a.get('id', 'u'), name=a.get('name', 'Unknown')) 
            for a in t.get('artists', [])
        ]
        
        # Build Track
        tracks_list.append(Track(
            id=t.get('id'), 
            title=t.get('name', 'Unknown'), 
            duration_ms=t.get('duration_ms', 0),
            popularity=t.get('popularity', 0), 
            album=album_obj, 
            artists=artists_obj
        ))

    if not tracks_list:
        print("⚠️ Playlist found, but no tracks could be extracted.")
        return

    # Save to Database
    final_pl = Playlist(
        id=pl_data['id'], 
        name=pl_data['name'], 
        description=pl_data.get('description', ''), 
        tracks=tracks_list
    )
    
    print(f"💾 Saving {len(tracks_list)} tracks to Database...")
    try:
        orm = FalkorGraphORM()
        orm.save_playlist(final_pl)
        print("🎉 SUCCESS! Data saved to FalkorDB.")
        return pl_data['name']
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return None

if __name__ == "__main__":
    if 'PASTE_YOUR' in SPOTIPY_CLIENT_ID:
        print("❌ STOP! You forgot to paste your API Keys in the script.")
    else:
        ingest_playlist()