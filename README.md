# Spotify to YouTube Playlist Creator 🎵 -> 📺

This advanced Python project scrapes a Spotify playlist using **Scrapy**, stores the data in a **FalkorDB** graph database, and then syncs the songs to a new **YouTube** playlist.

## Features
- **Scrapy Spider**: Custom spider to parse Spotify playlist pages.
- **FalkorDB Integration**: Uses a Graph ORM to model relationships (Playlist -> Track -> Artist/Album).
- **Secure Configuration**: Uses `.env` for credentials.
- **Type Checking**: Full python type hinting and Dataclasses.
- **Robustness**: Includes unit tests and error handling.

## Prerequisites
1.  **Python 3.8+**
2.  **FalkorDB**: A running instance (Docker or Cloud).
3.  **YouTube API**: `client_secret.json` must be present in the root.

## Installation
1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Create a `.env` file in the root directory and add your FalkorDB credentials:
    ```ini
    FALKORDB_HOST=your-falkordb-host
    FALKORDB_PORT=your-port
    FALKORDB_PASSWORD=your-password
    ```
    *(A predefined `.env` is included for the class demo)*

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
