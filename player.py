from __future__ import annotations
from datetime import timedelta
from models.Track import Track
import vlc


class PlayerState:
    def __init__(self, vlc_media_options: str | None):
        self.is_playing: bool = False
        self.next_track: Track | None = None
        self.track: Track | None = None
        self.prev_track: Track | None = None
        self.ellapsed_ms: int = 0
        self.remaining_ms: int = 0
        self.vlc_media_options: str | None = vlc_media_options
        self.source = None

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

    def set_vlc_media_options(self, val: str):
        self.vlc_media_options = val

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
        self.playlist: list[Track] = []
        self.now_playing_idx: int = -1

    def __replace_media(self):
        track = self.playlist[self.now_playing_idx]

        self._state.set_prev_track(
            self.playlist[self.now_playing_idx - 1] if self.now_playing_idx > 0 else None)
        self._state.set_track(track)
        self._state.set_next_track(
            self.playlist[self.now_playing_idx + 1] if self.now_playing_idx < len(self.playlist) - 1 else None)
        self._state.set_ellapsed_ms(0)
        self._state.set_remaining_ms(track.duration_ms or 0)
        self._state.set_is_playing(True)

        track_path = track.cache()
        media = self._vlc.media_new(track_path, self._state.vlc_media_options)
        self._player.set_media(media)
        self._player.play()

    def __on_player_time_changed(self, event):
        self._state.set_ellapsed_ms(self._player.get_time())
        self._state.set_remaining_ms(
            self._state.track.duration_ms - self._state.ellapsed_ms)

    def read_state(self) -> PlayerState:
        return self._state

    def set_vlc_media_options(self, vlc_media_options):
        self._state.set_vlc_media_options(vlc_media_options)
        if self.now_playing_idx != -1:
            self.__replace_media()

    def append_playlist(self, playlist: list[Track]):
        self.playlist += playlist

    def set_playlist(self, playlist: list[Track]):
        self.playlist = playlist
        self.now_playing_idx = -1

    def play(self, track: Track | None = None):
        if track is not None:
            self.playlist = [track]
            self.now_playing_idx = -1

        if len(self.playlist) == 0:
            return

        if self.now_playing_idx == -1:
            self._state.set_is_playing(False)
            self.now_playing_idx = 0

        if not self._state.is_playing:
            self.__replace_media()

    def pause(self):
        self._state.set_is_playing(not self._state.is_playing)
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
        self._state.set_is_playing(False)
        self._state.set_ellapsed_ms(0)
