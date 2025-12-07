from falkordb import FalkorDB
from .items import Playlist, Track

class FalkorGraphORM:
    def __init__(self):
        # ⚠️ REPLACE WITH YOUR FALKORDB CLOUD DETAILS
        CLOUD_HOST = 'r-6jissuruar.instance-nrapyhgxj.hc-20vidasdi.us-central1.gcp.f2e0a955bb84.cloud'  # Check your Dashboard
        CLOUD_PORT = 59832                           # Check your Dashboard
        CLOUD_PASSWORD = 'StoY_1'         # Click the Eye icon to see it
        
        # Connect
        self.db = FalkorDB(host=CLOUD_HOST, port=CLOUD_PORT, password=CLOUD_PASSWORD)
        self.graph = self.db.select_graph('SpotifyGraph')

    def save_playlist(self, playlist: Playlist) -> None:
        """Saves a playlist and all its tracks to the graph."""
        
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

        # 2. Save Tracks
        print(f"   ...Processing {len(playlist.tracks)} tracks...")
        for track in playlist.tracks:
            self._save_track_node(track)
            self._link_playlist_track(playlist.id, track.id)

    def _save_track_node(self, track: Track) -> None:
        # Create Album
        q_album = "MERGE (a:Album {id: $id}) SET a.name = $name, a.image = $img"
        self.graph.query(q_album, {
            'id': track.album.id, 
            'name': track.album.name,
            'img': track.album.image_url or ""
        })

        # Create Track
        q_track = """
        MERGE (t:Track {id: $id})
        SET t.title = $title, t.duration = $dur, t.popularity = $pop
        """
        self.graph.query(q_track, {
            'id': track.id,
            'title': track.title,
            'dur': track.duration_ms,
            'pop': track.popularity
        })

        # Link Track -> Album
        self.graph.query("""
            MATCH (t:Track {id: $tid}), (a:Album {id: $aid})
            MERGE (t)-[:BELONGS_TO]->(a)
        """, {'tid': track.id, 'aid': track.album.id})

        # Create Artists and Link
        for artist in track.artists:
            self.graph.query("MERGE (ar:Artist {id: $id}) SET ar.name = $name", 
                             {'id': artist.id, 'name': artist.name})
            
            self.graph.query("""
                MATCH (t:Track {id: $tid}), (ar:Artist {id: $aid})
                MERGE (t)-[:PERFORMED_BY]->(ar)
            """, {'tid': track.id, 'aid': artist.id})

    def _link_playlist_track(self, playlist_id: str, track_id: str) -> None:
        query = """
        MATCH (p:Playlist {id: $pid}), (t:Track {id: $tid})
        MERGE (p)-[:CONTAINS]->(t)
        """
        self.graph.query(query, {'pid': playlist_id, 'tid': track_id})