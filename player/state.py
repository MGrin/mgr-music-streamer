from __future__ import annotations
from datetime import timedelta
from models.Track import Track


class Source:
    def __init__(self, type: str = None, id: str = None, name: str = None, query: str = None):
        self.type = type
        self.id = id
        self.name = name
        self.query = query


class PlayerState:
    def __init__(self):
        self.is_playing: bool = False
        self.next_track: Track | None = None
        self.track: Track | None = None
        self.prev_track: Track | None = None
        self.ellapsed_ms: int = 0
        self.remaining_ms: int = 0
        self.volume: int = 0
        self.source: Source | None = None

    def set_is_playing(self, val: bool):
        self.is_playing = val

    def set_next_track(self, val: Track | None):
        self.next_track = val
        if self.next_track is not None:
            self.next_track.fetch()

    def set_track(self, val: Track | None):
        self.track = val
        if self.track is not None:
            self.track.fetch()

    def set_prev_track(self, val: Track | None):
        self.prev_track = val
        if self.prev_track is not None:
            self.prev_track.fetch()

    def set_ellapsed_ms(self, val: int):
        self.ellapsed_ms = val

    def set_remaining_ms(self, val: int):
        self.remaining_ms = val

    def set_volume(self, val: int):
        self.volume = val

    def set_source(self, val: Source):
        self.source = val

    def __repr__(self) -> str:
        message = ""
        if self.is_playing:
            message += '[Playing] '
        timedelta_ellapsed = timedelta(milliseconds=self.ellapsed_ms)
        timedelta_remaining = timedelta(milliseconds=self.remaining_ms)

        message += f'{self.track.title} - {self.track.artists.title} '
        message += str(timedelta_ellapsed).split('.')[0] + ' <-> '
        message += str(timedelta_remaining).split('.')[0]
        return message
