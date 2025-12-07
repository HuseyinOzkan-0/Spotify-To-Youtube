"""
Domain Entities.

Defines pure Python Dataclasses for Playlist, Track, Album, and Artist.
Used to enforce type safety across the application.
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Artist:
    id: str
    name: str

@dataclass
class Album:
    id: str
    name: str
    release_date: Optional[str] = None
    image_url: Optional[str] = None

@dataclass
class Track:
    id: str
    title: str
    duration_ms: int
    popularity: int
    album: Album
    artists: List[Artist]

@dataclass
class Playlist:
    id: str
    name: str
    description: Optional[str]
    tracks: List[Track] = field(default_factory=list)