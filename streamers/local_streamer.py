from models.SubList import SubList
from models.Track import Track
from streamers.streamer import Streamer
from pathlib import Path
from os import listdir
from os.path import isfile, join

LIBRARY = '/tmp'


class LocalTrack(Track):
    def fetch(self):
        pass

    def cache(self):
        return '/Users/mgrin/Projects/sandbox/mgr-music-streamer/cache/Jain/Hope - EP/Makeba_24109025.mp3'


class LocalStreamer(Streamer):
    def __init__(self, title: str, debug=False, library="/tmp/local"):
        super().__init__(title, debug)
        self.library = Path(library)
        global LIBRARY
        LIBRARY = library

    def play_predefined_playlist(self, playlist_name: str):
        raise Exception(
            'Predefined playlists are not supported in Local streamers')

    def play_playlist(self, artis_name: str):
        super().play_playlist(artis_name)
        playlist: list[Track] = [LocalTrack()]
        self.set_playlist(playlist)
        self.play()

        raise Exception('Not implemented')

    def play_from_query(self, query: str):
        raise Exception('Not implemented')

    def fetch_predefinded_playlists(self):
        return []
        raise Exception(
            'Predefined playlists are not supported in Local streamers')
