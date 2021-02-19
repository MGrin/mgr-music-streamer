from __future__ import annotations
from player.state import PlayerState, Source
from models.Track import Track
import vlc


class Player:
    def __init__(self, callbacks: dict = {}):
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

        self._state = PlayerState()
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
        media = self._vlc.media_new(track_path)
        self._player.set_media(media)
        self._player.play()

    def __on_player_time_changed(self, event):
        self._state.set_ellapsed_ms(self._player.get_time())
        self._state.set_remaining_ms(
            self._state.track.duration_ms - self._state.ellapsed_ms)

    def read_state(self) -> PlayerState:
        return self._state

    def set_playlist(self, playlist: list[Track], source: Source):
        self._state.set_source(source)
        self.playlist = playlist
        self.now_playing_idx = -1

    def play(self):
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
