"""
Main CLI Entry Point.

Orchestrates the entire Spotify -> Database -> YouTube pipeline.
Supports both interactive and command-line arguments.
"""
import argparse
import sys
import run_api
import sync_youtube

def main():
    parser = argparse.ArgumentParser(description="Spotify to YouTube Playlist Converter")
    parser.add_argument("url", nargs="?", help="Spotify Playlist URL")
    parser.add_argument("--name", "-n", help="Name for the YouTube Playlist")
    
    args = parser.parse_args()
    
    # 1. Ingest from Spotify
    print("\n" + "="*40)
    print(" 🎵 STEP 1: IMPORT FROM SPOTIFY")
    print("="*40)
    
    playlist_name = run_api.ingest_playlist(args.url)
    
    if not playlist_name:
        print("❌ Spotify Import failed or was cancelled.")
        sys.exit(1)
        
    print(f"\n✅ Playlist '{playlist_name}' ready for export.")
    
    # 2. Sync to YouTube
    print("\n" + "="*40)
    print(" 📺 STEP 2: EXPORT TO YOUTUBE")
    print("="*40)
    
    # Determine YouTube Playlist Name
    yt_name = args.name if args.name else playlist_name
    
    # Check if user wants to override name if not provided via CLI
    if not args.name:
        confirm = input(f"Use name '{yt_name}' for YouTube? [Y/n]: ").strip().lower()
        if confirm == 'n':
            yt_name = input("Enter new name: ").strip()
    
    # Run Sync
    songs = sync_youtube.fetch_songs()
    if songs:
        youtube = sync_youtube.get_authenticated_service()
        # We need to expose create_pl and sync_songs or call shared logic
        # Ideally sync_youtube should interpret 'yt_name'
        
        # Calling logic from sync_youtube directly:
        pl_id = sync_youtube.create_pl(youtube, yt_name)
        sync_youtube.sync_songs(youtube, pl_id, songs)
        print("\n🎉 MISSION ACCOMPLISHED!")
    else:
        print("❌ No songs found to sync.")

if __name__ == "__main__":
    main()
