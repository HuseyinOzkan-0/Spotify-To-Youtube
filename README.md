# Spotify to YouTube Playlist Creator 🎵 -> 📺

This advanced Python project scrapes a Spotify playlist using **Scrapy**, stores the data in a **FalkorDB** graph database, and then syncs the songs to a new **YouTube** playlist.

## Features
- **Scrapy Spider**: Custom spider to parse Spotify playlist pages.
- **FalkorDB Integration**: Uses a Graph ORM to model relationships (Playlist -> Track -> Artist/Album).
- **Type Checking**: Full python type hinting and Dataclasses.
- **Robustness**: Includes unit tests and error handling.
- **Complexity**: Demonstrates advanced usage of scraping pipelines and graph databases.

## Prerequisites
1.  **Python 3.8+**
2.  **FalkorDB**: A running instance (Docker or Cloud).
    -   Update credentials in `spotify_graph/orm.py`.
3.  **YouTube API**: `client_secret.json` must be present in the root.

## Installation
```bash
pip install -r requirements.txt
```
*(Ensure you have `scrapy`, `falkordb`, `google-auth-oauthlib`, `google-api-python-client`, `spotipy` (legacy), `tqdm` installed)*

## Usage
Run the main entry point:
```bash
python main.py
```
1.  Enter the **Spotify Playlist URL** when prompted.
2.  The scraper will fetch track data and save it to the Graph Database.
3.  Enter the name for the new **YouTube Playlist**.
4.  Authenticate with Google (if first time).
5.  Watch as songs are added to YouTube!

## Project Structure
- `spotify_graph/`: Main package.
    - `spiders/`: Scrapy spiders.
    - `items.py`: Dataclasses for Playlist, Track, etc.
    - `orm.py`: Object Relational Mapper for FalkorDB.
    - `pipelines.py`: Scrapy pipeline to save data.
- `main.py`: CLI entry point.
- `sync_youtube.py`: YouTube API logic.
- `tests/`: Unit tests.

## Running Tests
```bash
python -m unittest discover tests
```

## Known Issues
- Spotify's dynamic content requires a robust user-agent (configured).
- YouTube API quotas are limited (approx 10,000 units/day).
