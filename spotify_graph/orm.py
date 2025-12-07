"""
ORM Layer for FalkorDB.

Handles the connection to the Graph Database and provides methods
to save playlists, tracks, albums, and artists using Cypher queries.
"""
import sys
import os
from falkordb import FalkorDB
import config
from .items import Playlist

# Ensure we can find config if run from subfolder
sys.path.append(os.getcwd())

class FalkorGraphORM:
    """Object Relational Mapper for storing Spotify data in FalkorDB."""

    def __init__(self):
        """Initialize database connection using config credentials."""
        # ⚠️ FALKORDB CONFIGURATION LOADED FROM CONFIG
        print(f"🔌 Connecting to FalkorDB at {config.FALKORDB_HOST} as user '{config.FALKORDB_USERNAME}'...")
        
        self.db = FalkorDB(
            host=config.FALKORDB_HOST, 
            port=config.FALKORDB_PORT, 
            username=config.FALKORDB_USERNAME,
            password=config.FALKORDB_PASSWORD
        )
        self.graph = self.db.select_graph('SpotifyGraph')

    def clear_database(self):
        """Deletes all nodes and relationships in the graph."""
        print("🧹 Clearing entire database...")
        self.graph.query("MATCH (n) DETACH DELETE n")

    def save_playlist(self, playlist: Playlist) -> None:
        """
        Saves a Playlist object and all its related entities to the Graph.
        
        Uses high-performance UNWIND batching to minimize network round-trips.
        """
        print(f"   💾 Batching {len(playlist.tracks)} tracks (High Performance)...")

        # 1. Save Playlist Node
        query_playlist = """
        MERGE (p:Playlist {id: $id})
        SET p.name = $name, p.description = $desc
        """
        self.graph.query(query_playlist, {
            'id': playlist.id, 
            'name': playlist.name, 
            'desc': playlist.description or ""
        })

        # --- PREPARE DATA FOR BATCHING ---
        unique_albums = {}
        unique_artists = {}
        track_params = []
        track_artist_relations = []
        
        for t in playlist.tracks:
            # Prepare Album Data
            if t.album.id not in unique_albums:
                unique_albums[t.album.id] = {
                    'id': t.album.id,
                    'name': t.album.name,
                    'image': t.album.image_url or ""
                }
            
            # Prepare Artist Data & Relations
            for artist in t.artists:
                if artist.id not in unique_artists:
                    unique_artists[artist.id] = {'id': artist.id, 'name': artist.name}
                
                track_artist_relations.append({'t_id': t.id, 'a_id': artist.id})

            # Prepare Track Data
            track_params.append({
                'id': t.id,
                'title': t.title,
                'duration': t.duration_ms,
                'popularity': t.popularity,
                'album_id': t.album.id
            })

        # 2. Batch Insert Albums
        if unique_albums:
            q_albums = """
            UNWIND $albums as row
            MERGE (a:Album {id: row.id})
            SET a.name = row.name, a.image = row.image
            """
            self.graph.query(q_albums, {'albums': list(unique_albums.values())})

        # 3. Batch Insert Artists
        if unique_artists:
            q_artists = """
            UNWIND $artists as row
            MERGE (a:Artist {id: row.id})
            SET a.name = row.name
            """
            self.graph.query(q_artists, {'artists': list(unique_artists.values())})

        # 4. Batch Insert Tracks & Link to Album
        # We do this in one go: Create Track, Match Album, Link
        if track_params:
            q_tracks = """
            UNWIND $tracks as row
            MERGE (t:Track {id: row.id})
            SET t.title = row.title, t.duration = row.duration, t.popularity = row.popularity
            
            WITH t, row
            MATCH (a:Album {id: row.album_id})
            MERGE (t)-[:BELONGS_TO]->(a)
            """
            self.graph.query(q_tracks, {'tracks': track_params})

        # 5. Batch Link Tracks -> Artists
        if track_artist_relations:
            q_link_artists = """
            UNWIND $rels as row
            MATCH (t:Track {id: row.t_id}), (a:Artist {id: row.a_id})
            MERGE (t)-[:PERFORMED_BY]->(a)
            """
            self.graph.query(q_link_artists, {'rels': track_artist_relations})

        # 6. Batch Link Playlist -> Tracks
        # We can just use the list of track IDs from track_params
        if track_params:
            q_link_playlist = """
            MATCH (p:Playlist {id: $p_id})
            UNWIND $track_ids as t_id
            MATCH (t:Track {id: t_id})
            MERGE (p)-[:CONTAINS]->(t)
            """
            self.graph.query(q_link_playlist, {
                'p_id': playlist.id,
                'track_ids': [t['id'] for t in track_params]
            })
            
        print("   ✅ Batch save complete!")