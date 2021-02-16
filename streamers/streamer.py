from __future__ import annotations
from models.Track import Track

import threading
from queue import Queue
from typing import Any

from player import Player, PlayerState
from time import sleep


def run_player(callbacks, commands: Queue, returns: Queue):
    player = Player(callbacks)
    running = True
    while running:
        sleep(0.2)
        while not commands.empty():
            call_request = commands.get()
            command = call_request[0]
            arg = None if len(call_request) == 1 else call_request[1]
            if command == 'KILL':
                running = False
                continue

            method_to_call = getattr(player, command)
            res = None
            if arg is None:
                res = method_to_call()
            else:
                res = method_to_call(arg)

            if res is not None:
                returns.put(res)


class Streamer:
    def __init__(self, title: str, debug=False):
        self.title = title
        self.is_running = False
        self.source: dict[str, str] | None = None
        self.__debug = debug

    def send_command_to_player(self, command, arg=None, await_result=False):
        data = [command]
        if arg is not None:
            data.append(arg)
        self.player_commands_queue.put(data)
        if await_result:
            while self.player_returns_queue.empty():
                pass
            return self.player_returns_queue.get()

    def play_predefined_playlist(self, playlist_name: str):
        self.source = {
            'type': 'playlist',
            'name': playlist_name,
        }

    def play_playlist(self, playlist_id: str):
        self.source = {
            'type': 'playlist',
            'id': playlist_id,
        }

    def play_from_query(self, query: str):
        self.source = {
            'type': 'query',
            'query': query,
        }

    def fetch_predefinded_playlists(self) -> list[str]:
        return []

    def on_track_ends_player_event_callback(self, event):
        self.next()

    def on_error_player_event_callback(self, event):
        print(event)

    def get_state(self) -> PlayerState | None:
        state = self.send_command_to_player('read_state', await_result=True)
        state.source = self.source
        return state

    def play(self):
        if self.__debug:
            self.__testable_play()
        else:
            self.send_command_to_player('play')

    def pause(self):
        self.send_command_to_player('pause')

    def next(self):
        self.send_command_to_player('next')

    def prev(self):
        self.send_command_to_player('prev')

    def stop(self):
        self.send_command_to_player('stop')

    def set_vlc_media_options(self, vlc_media_options: str):
        self.send_command_to_player('set_vlc_media_options', vlc_media_options)

    def append_playlist(self, playlist: list[Track]):
        self.send_command_to_player('append_playlist', playlist)

    def set_playlist(self, playlist: list[Track]):
        self.send_command_to_player('set_playlist', playlist)

    def __testable_play(self, number_of_tracks=5):
        self.play()
        sleep(5)
        for i in range(0, number_of_tracks - 1):
            self.next()
            sleep(5)
        self.stop()

    def run(self):
        self.player_commands_queue = Queue()
        self.player_returns_queue = Queue()

        self.player_callbacks = {
            "on_track_ends_cb": self.on_track_ends_player_event_callback,
            "on_player_error_cb": self.on_error_player_event_callback,
        }
        self.player_thread = threading.Thread(
            name='player', target=run_player, daemon=True, args=(self.player_callbacks, self.player_commands_queue, self.player_returns_queue))
        self.player_thread.start()
        self.is_running = True

    def kill(self):
        self.send_command_to_player(['KILL'])
        self.is_running = False
