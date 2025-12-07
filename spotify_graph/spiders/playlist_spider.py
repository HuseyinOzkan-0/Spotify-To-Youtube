import scrapy
from ..items import Playlist, Track, Album, Artist
import json

class PlaylistSpider(scrapy.Spider):
    name = "playlist_spider"
    
    def __init__(self, url=None, *args, **kwargs):
        super(PlaylistSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            # Default fallback for testing if no URL provided
            self.start_urls = ['https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M']

    def parse(self, response):
        # Extract Playlist Info
        playlist_name = response.xpath('//h1/text()').get() or response.meta.get('playlist_name', "Unknown Playlist")
        # On mobile view, h1 might be the title.
        if not playlist_name:
            playlist_name = response.css('title::text').get().replace(' | Spotify Playlist', '')

        # Description
        description = response.xpath('//meta[@name="description"]/@content').get()

        # Playlist ID from URL
        playlist_id = response.url.split('/')[-1].split('?')[0]

        tracks = []
        
        # Select track rows
        # data-testid="track-row" is present in the HTML dump
        for row in response.css('div[data-testid="track-row"]'):
            # Title
            title_node = row.css('a[href^="/track/"] p::text')
            if not title_node: # Try finding inside span if p is not direct
                title_node = row.css('a[href^="/track/"] span::text') # The HTML showed p > span
            
            # The HTML dump showed:
            # <p ... class="... ListRowTitle__ListRowText..."> <span ...> Title </span> </p>
            title = row.css('p[data-encore-id="listRowTitle"] span::text').get() or \
                    row.css('a[href^="/track/"]::text').get() or \
                    row.css('p::text').get() # Fallback

            # Track ID
            track_link = row.css('a[href^="/track/"]::attr(href)').get()
            track_id = track_link.split('/')[-1] if track_link else None
            
            if not track_id:
                continue

            # Artists
            # Usually in the subtitle div
            # HTML: <div class="..."><span ...>Artist Name</span></div>
            # It seems to be the div AFTER the title div or similar.
            # Let's try to capture all text in the row and filter? No that's messy.
            # The artist seems to be in a span with 'encore-internal-color-text-subdued' class inside the interactive area.
            
            # Simplified selector for Artist (might get more than one, combined by comma usually)
            artist_name = row.css('span.encore-internal-color-text-subdued::text').get()
            
            # Image
            image_url = row.css('img::attr(src)').get()

            # Duration - often not in mobile view list, might be missing.
            duration_ms = 0 # Default

            # Popularity - not visible.
            popularity = 0

            # Album - not visible in mobile list.
            album = Album(id="unknown", name="Unknown Album", image_url=image_url)

            # Artist Object
            # If multiple artists are comma separated in text:
            artists = []
            if artist_name:
                # Naive split by comma, might break for "Tyler, The Creator"
                # But for this scope it's okay or we keep as one string in name.
                # Let's clean it.
                artists = [Artist(id=f"artist_{name.strip()}", name=name.strip()) for name in artist_name.split(',')]
            else:
                artists = [Artist(id="unknown", name="Unknown Artist")]

            tracks.append(Track(
                id=track_id,
                title=title or "Unknown Title",
                duration_ms=duration_ms,
                popularity=popularity,
                album=album,
                artists=artists
            ))

        self.log(f"Extracted {len(tracks)} tracks")

        if tracks:
            # Construct Playlist
            playlist = Playlist(
                id=playlist_id,
                name=playlist_name,
                description=description,
                tracks=tracks
            )
            yield playlist
