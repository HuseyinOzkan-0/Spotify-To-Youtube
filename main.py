import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spotify_graph.spiders.playlist_spider import PlaylistSpider
import sync_youtube
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def main():
    print("🚀 Spotify to YouTube Playlist Creator 🚀")
    
    # 1. Ask for Spotify Playlist URL
    # default for testing
    default_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    playlist_url = input(f"Enter Spotify Playlist URL [default: {default_url}]: ").strip()
    if not playlist_url:
        playlist_url = default_url

    print(f"🕷️  Starting Scrapy Spider for {playlist_url}...")
    
    # Configure Scrapy settings programmatically to ensure they are loaded
    # referencing the settings module we created
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'spotify_graph.settings')
    settings = get_project_settings()
    
    process = CrawlerProcess(settings)
    process.crawl(PlaylistSpider, url=playlist_url)
    process.start() # This blocks until spider finishes

    print("✅ Scraping and Database saving complete.")

    # 2. Ask for YouTube Playlist Name
    yt_name = input("Enter name for the new YouTube Playlist: ").strip()
    if not yt_name:
        print("❌ No name provided. Exiting.")
        return

    # 3. Sync to YouTube
    # We essentially run the logic from sync_youtube.py
    songs = sync_youtube.fetch_songs_from_db()
    
    if not songs:
        print("⚠️  No songs found in FalkorDB to sync.")
        return

    print(f"🎵 Found {len(songs)} songs to sync.")
    
    try:
        youtube = sync_youtube.get_authenticated_service()
        pl_id = sync_youtube.create_playlist(youtube, yt_name)
        sync_youtube.search_and_add(youtube, pl_id, songs)
        print("🎉 All done! Enjoy your playlist.")
    except Exception as e:
        print(f"❌ An error occurred during YouTube sync: {e}")

if __name__ == "__main__":
    main()
