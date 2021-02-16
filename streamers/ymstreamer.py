from __future__ import annotations
from streamers.streamer import Streamer
from yandex_music import Client
from yandex_music.album.album import Album
from yandex_music.artist.artist import Artist
from yandex_music.playlist.playlist import Playlist
from yandex_music.track.track import Track
from yandex_music.track_short import TrackShort

SEARCH_TYPE_TO_NAME = {
    'track': 'трек',
    'artist': 'исполнитель',
    'album': 'альбом',
    'playlist': 'плейлист',
    'video': 'видео',
    'user': 'пользователь',
    'podcast': 'подкаст',
    'podcast_episode': 'эпизод подкаста',
}


class YMStreamer(Streamer):
    def __init__(self, username: str, password: str, title: str, debug=False):
        super(YMStreamer, self).__init__(title, debug)
        self.client = Client.from_credentials(username, password)

    def play_predefined_playlist(self, playlist_name: str):
        playlist = self.__get_playlist(playlist_name)
        self.set_playlist(playlist)
        self.play()

    def play_from_query(self, query: str):
        playlist = self.__generate_playlist_from_query(query)
        self.set_playlist(playlist)
        self.play()

    def fetch_predefinded_playlists(self):
        PersonalPlaylistBlocks = self.client.landing(
            blocks=['personalplaylists']).blocks[0]
        playlists = []

        for x in PersonalPlaylistBlocks.entities:
            playlists.append(
                x.data.data.generated_playlist_type)  # type: ignore
        return [*playlists, 'liked']

    def __get_playlist(self, name: str):
        if name == 'liked':
            tracks = self.client.users_likes_tracks()
            if tracks is None:
                raise Exception('No tracks found')
            return tracks.tracks

        PersonalPlaylistBlocks = self.client.landing(
            blocks=['personalplaylists']).blocks[0]

        DailyPlaylist = next(
            x.data.data for x in PersonalPlaylistBlocks.entities if x.data.data.generated_playlist_type == name  # type: ignore
        )

        if DailyPlaylist is None:
            raise Exception()

        playlist: Playlist = self.client.users_playlists(
            user_id=DailyPlaylist.uid, kind=DailyPlaylist.kind)  # type: ignore

        return playlist.tracks

    def __generate_playlist_from_query(self, query) -> list[Track | TrackShort]:
        search_result = self.client.search(query)
        resulting_playlist: list[Track | TrackShort] = []

        if search_result.best:
            type_ = search_result.best.type
            best = search_result.best.result

            if type_ in ['track', 'podcast_episode']:
                if isinstance(best, Track):
                    resulting_playlist = [best]
            elif type_ == 'artist':
                if isinstance(best, Artist):
                    resulting_playlist = best.get_tracks()  # type: ignore

            elif type_ in ['album', 'podcast']:
                if isinstance(best, Album):
                    resulting_playlist = [
                        track for volume in best.volumes for track in volume]

            elif type_ == 'playlist':
                if isinstance(best, Playlist):
                    resulting_playlist = best.tracks  # type: ignore
        return resulting_playlist
