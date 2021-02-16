from __future__ import annotations
from models.SubList import SubList


class Track:
    def __init__(self):
        self.provider: str | None = None
        self.id: str | None = None
        self.title: str | None = None

        self.artists: SubList | None = None
        self.albums: SubList | None = None

        self.duration_ms: int | None = None
        self.cover_uri: str | None = None

    def fetch(self):
        raise Exception('Cache is not implemented!')

    def cache(self):
        raise Exception('Cache is not implemented!')
