import unittest
from spotify_graph.items import Track, Playlist, Album, Artist

class TestItems(unittest.TestCase):
    def test_track_creation(self):
        artist = Artist(id="1", name="Artist")
        album = Album(id="1", name="Album")
        track = Track(
            id="1", 
            title="Title", 
            duration_ms=1000, 
            popularity=50, 
            album=album, 
            artists=[artist]
        )
        self.assertEqual(track.title, "Title")
        self.assertEqual(track.artists[0].name, "Artist")

    def test_playlist_creation(self):
        pl = Playlist(id="1", name="My PL", description="Desc")
        self.assertEqual(pl.name, "My PL")
        self.assertEqual(len(pl.tracks), 0)

if __name__ == '__main__':
    unittest.main()
