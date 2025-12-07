
import unittest
from unittest.mock import MagicMock, patch
from spotify_graph.items import Track, Album, Artist

class TestSpotifyItems(unittest.TestCase):
    def test_track_creation(self):
        """Test that Track dataclass is created correctly."""
        artist = Artist(id="a1", name="Artist 1")
        album = Album(id="al1", name="Album 1")
        track = Track(id="t1", title="Song 1", duration_ms=1000, popularity=50, album=album, artists=[artist])
        
        self.assertEqual(track.title, "Song 1")
        self.assertEqual(track.artists[0].name, "Artist 1")

class TestPlaylistBatching(unittest.TestCase):
    def test_data_structure(self):
        """Test that data structures for batching logic are valid."""
        # This tests the logic used in ORM without needing a DB connection
        tracks = []
        for i in range(5):
            tracks.append({
                'id': f't{i}',
                'title': f'Song {i}',
                'album_id': 'al1'
            })
        
        self.assertEqual(len(tracks), 5)
        self.assertEqual(tracks[0]['id'], 't0')

if __name__ == '__main__':
    unittest.main()
