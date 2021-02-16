from __future__ import annotations
from models.SubList import SubList


class Artist:
    def __init__(self):
        self.provider: str | None = None
        self.id: str | None = None
        self.title: str | None = None

        self.albums: SubList | None = None

        self.cover_uri: str | None = None
