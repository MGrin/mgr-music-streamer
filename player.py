from __future__ import annotations
from datetime import timedelta

from yandex_music.track.track import Track
from utils import cache_track, cast_to_track
from time import sleep
import vlc

from yandex_music.track_short import TrackShort


class PlayerState:
    def __init__(self, vlc_media_options: str | None):
        self.is_playing: bool = False
        self.next_track: Track | None = None
        self.track: Track | None = None
        self.prev_track: Track | None = None
        self.ellapsed_ms: int = 0
        self.remaining_ms: int = 0
        self.vlc_media_options: str | None = vlc_media_options

    def serialize(self):
        d = self.__dict__.copy()
        d['next_track'] = None if not self.next_track else self.next_track.to_dict()
        d['track'] = None if not self.track else self.track.to_dict()
        d['prev_track'] = None if not self.prev_track else self.prev_track.to_dict()
        return d

    def __repr__(self) -> str:
        message = ""
        if self.is_playing:
            message += '[Playing] '
        timedelta_ellapsed = timedelta(milliseconds=self.ellapsed_ms)
        timedelta_remaining = timedelta(milliseconds=self.remaining_ms)

        message += str(timedelta_ellapsed).split('.')[0] + ' '
        message += str(timedelta_remaining).split('.')[0] + ' '
        return message


class Player:
    def __init__(self, callbacks: dict = {}, vlc_media_options: str = None):
        self._vlc = vlc.Instance()
        self._player = self._vlc.media_player_new()
        self._player_events = self._player.event_manager()
        if "on_track_ends_cb" in callbacks:
            self._player_events.event_attach(
                vlc.EventType.MediaPlayerEndReached, callbacks.get("on_track_ends_cb"))  # type: ignore
        if "on_player_error_cb" in callbacks:
            self._player_events.event_attach(
                vlc.EventType.MediaPlayerEncounteredError, callbacks.get("on_player_error_cb"))  # type: ignore

        self._player_events.event_attach(
            vlc.EventType.MediaPlayerTimeChanged, self.__on_player_time_changed)  # type: ignore

        self._state = PlayerState(vlc_media_options)
        self.playlist: list[Track | TrackShort] = []
        self.now_playing_idx: int = -1

    def __replace_media(self):
        track = cast_to_track(self.playlist[self.now_playing_idx])

        self._state.prev_track = cast_to_track(
            self.playlist[self.now_playing_idx - 1]) if self.now_playing_idx > 0 else None
        self._state.track = track
        self._state.next_track = cast_to_track(
            self.playlist[self.now_playing_idx + 1]) if self.now_playing_idx < len(self.playlist) - 1 else None
        self._state.ellapsed_ms = 0
        self._state.remaining_ms = track.duration_ms or 0
        self._state.is_playing = True

        track_path = cache_track(track)
        media = self._vlc.media_new(track_path, self._state.vlc_media_options)
        self._player.set_media(media)
        self._player.play()

    def __on_player_time_changed(self, event):
        self._state.ellapsed_ms = self._player.get_time()
        self._state.remaining_ms = self._state.track.duration_ms - self._state.ellapsed_ms

    def read_state(self) -> PlayerState:
        return self._state

    def set_vlc_media_options(self, vlc_media_options):
        self._state.vlc_media_options = vlc_media_options
        if self.now_playing_idx != -1:
            self.__replace_media()

    def append_playlist(self, playlist: list[TrackShort] | list[Track]):
        self.playlist += playlist

    def set_playlist(self, playlist: list[TrackShort | Track]):
        self.playlist = playlist
        self.now_playing_idx = -1

    def play(self, track_short: Track | TrackShort | None = None):
        if track_short is not None:
            self.playlist = [cast_to_track(track_short)]
            self.now_playing_idx = -1

        if len(self.playlist) == 0:
            return

        if self.now_playing_idx == -1:
            self._state.is_playing = False
            self.now_playing_idx = 0

        if not self._state.is_playing:
            self.__replace_media()

    def pause(self):
        self._state.is_playing = not self._state.is_playing
        self._player.pause()

    def next(self):
        if self.now_playing_idx == 0 and len(self.playlist) == 1:
            self.stop()
        else:
            self.now_playing_idx = (
                self.now_playing_idx + 1) % len(self.playlist)
            self.__replace_media()

    def prev(self):
        if self.now_playing_idx == 0 and len(self.playlist) == 1:
            self.stop()
        else:
            self.now_playing_idx = (
                self.now_playing_idx - 1) % len(self.playlist)
            self.__replace_media()

    def stop(self):
        self.now_playing_idx = -1
        self._player.stop()
        self._state.is_playing = False
        self._state.ellapsed_ms = 0
