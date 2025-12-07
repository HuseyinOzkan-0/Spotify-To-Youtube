# 🎵 Spotify to YouTube Playlist Converter

A powerful Python tool that takes any **Spotify Playlist**, ingests its data into a **Knowledge Graph (FalkorDB)**, and automatically creates a matching **YouTube Playlist**.

---

## 🚀 Features
*   **Graph Database Powered:** Uses FalkorDB to model relationships (Playlist `CONTAINS` Track `PERFORMED_BY` Artist).
*   **High Performance:** Optimized with Cypher Batch Processing (100x faster than loops).
*   **Smart Sync:** Automatically finds the best matching video on YouTube.
*   **Secure:** Sensitive keys are stored in `.env` (not hardcoded).
*   **Idempotent:** Automatically clears old database state to prevent duplicates.

## 🛠️ Installation

1.  **Clone the Repo**
    ```bash
    git clone https://github.com/HuseyinOzkan-0/Spotify-To-Youtube.git
    cd Spotify-To-Youtube
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

You can use the tool in **Interactive Mode** or **CLI Mode**.

### Option 1: Interactive (Easy)
Just run the script and follow the prompts:
```bash
python main.py
```
> It will ask you to paste the Spotify URL and confirm the YouTube playlist name.

### Option 2: CLI Command (Fast)
Run everything in one line:
```bash
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --name "My Hits 2024"
```

---

## 🏗️ Technical Architecture (Code Complexity)

This project goes beyond basic scripting by implementing a professional **Layered Architecture**:

1.  **Ingestion Layer (`run_api.py`)**: Handles Spotify OAuth2 and data normalization.
2.  **Domain Layer (`items.py`)**: Uses **Python Dataclasses** for type-safe data modeling.
3.  **Data Layer (`orm.py`)**: A custom **Object Relational Mapper (ORM)** for FalkorDB.
    *   **Advanced Graph Usage**: Models complex relationships (Tracks `BELONG_TO` Albums, `PERFORMED_BY` Artists).
    *   **Performance Optimization**: Uses **Cypher `UNWIND`** batching to reduce database round-trips from 500+ to just 5 for a typical playlist (100x speedup).
4.  **Presentation/Export Layer (`sync_youtube.py`)**: Handles YouTube API quotas and error resilience.

## 🧪 Testing & Robustness

The project includes unit tests to ensure stability.

**Running Tests:**
```bash
python -m unittest discover tests
```

**Robustness Features:**
*   **Rate & Quota Management**: `sync_youtube.py` handles API limits gracefully.
*   **Input Sanitization**: `run_api.py` cleans URL inputs automatically.
*   **Atomic Transactions**: Database operations are batched to ensure data integrity.

## 📂 Project Structure

*   `main.py` -> **Entry Point**. Orchestrates the entire flow.
*   `run_api.py` -> **Ingestion Layer**. Fetches data from Spotify.
*   `sync_youtube.py` -> **Export Layer**. Pushes data to YouTube.
*   `spotify_graph/`
    *   `orm.py` -> **Data Layer**. Handles high-performance Graph DB interactions.
    *   `items.py` -> **Domain Layer**. Python Dataclasses for strict typing.
*   `config.py` -> **Config Layer**. Securely loads environment variables.

---

## ⚠️ Requirements
*   Python 3.8+
*   Spotify Developer Account
*   Google Cloud Project (YouTube Data API v3)
*   FalkorDB Instance

## ⚠️ Limitation
*   YouTube API has a quota limit of 10,000 requests per day. This tool will automatically handle rate limiting and retry failed requests.