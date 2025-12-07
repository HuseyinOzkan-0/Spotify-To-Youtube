import os

def load_env_file(filepath=".env"):
    """
    Simple dependency-free .env parser.
    """
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Load environment variables when this module is imported
load_env_file()

# Configuration Variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

FALKORDB_HOST = os.getenv("FALKORDB_HOST")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", 6379))
FALKORDB_USERNAME = os.getenv("FALKORDB_USERNAME")
FALKORDB_PASSWORD = os.getenv("FALKORDB_PASSWORD")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("⚠️ WARNING: Spotify API keys are missing in .env")

if not FALKORDB_PASSWORD:
    print("⚠️ WARNING: FalkorDB password missing in .env")
