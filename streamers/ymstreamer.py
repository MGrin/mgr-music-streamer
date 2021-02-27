from __future__ import annotations

from yandex_music.artist.artist import Artist
from yandex_music.playlist.playlist import Playlist
from player.state import Source
from cachetools.func import ttl_cache
from models.SubList import SubList
from pathlib import Path

import yandex_music
from yandex_music import Client

from models.Track import Track
from streamers.streamer import Streamer

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

CACHE_FOLDER = '/tmp/YMStreamer'


class YMTrack(Track):
    def __init__(self, track: yandex_music.Track | yandex_music.TrackShort):
        super().__init__()
        self.__original = track
        self.provider = 'yandex_music'
        self.id = str(self.__original.id)
        self.__fetched = False

    def fetch(self):
        if self.__fetched:
            return

        self.__original = self.__original if isinstance(
            self.__original, yandex_music.Track) else self.__original.track or self.__original.fetchTrack()

        self.title = self.__original.title
        self.cover_uri = self.__original.cover_uri
        self.duration_ms = self.__original.duration_ms

        albums_title = ', '.join(
            [a.title or 'Unkown album' for a in self.__original.albums])
        albums_ids = [
            f'{self.provider}|{a.id}' for a in self.__original.albums]
        self.albums = SubList(title=albums_title, data=albums_ids)

        artists_title = ', '.join(
            [a.name or 'Unkown Artist' for a in self.__original.artists])
        artists_ids = [
            f'{self.provider}|{a.id}' for a in self.__original.artists]
        self.artists = SubList(title=artists_title, data=artists_ids)

        self.__fetched = True

    def cache(self):
        if not self.__fetched:
            self.fetch()

        artist_dir = Path(self.artists.title)
        album_dir = Path(self.albums.title)
        file_path = CACHE_FOLDER / artist_dir / \
            album_dir / f'{self.title}_{self.id}.mp3'

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.__original.download(str(file_path))  # type: ignore

        return str(file_path)


class YMStreamer(Streamer):
    def __init__(self, title: str, username: str | None = None, password: str | None = None, token: str | None = None, cache="/tmp/YMStreamer", debug=False):
        super().__init__(title, debug)
        if token is not None:
            self.client = Client.from_token(token)
        else:
            self.client = Client.from_credentials(username, password)

        global CACHE_FOLDER
        CACHE_FOLDER = cache

    def play_predefined_playlist(self, playlist_name: str):
        (ym_playlist, original) = self.__get_playlist_by_name(playlist_name)
        playlist: list[Track] = [YMTrack(track) for track in ym_playlist]
        source = Source(type='playlist', name=playlist_name,
                        id=str(original.uid))
        self.set_playlist(playlist, source=source)
        self.play()

    def play_playlist(self, playlist_id: str):
        (ym_playlist, original) = self.__get_playlist_by_id(playlist_id)
        playlist: list[Track] = [YMTrack(track) for track in ym_playlist]
        source = Source(type='playlist', id=playlist_id, name=original.title)
        self.set_playlist(playlist, source)
        self.play()

    def play_artist(self, artist_id: str):
        artist: yandex_music.Artist = self.client.artists(
            artist_ids=[artist_id])[0]
        tracks: yandex_music.ArtistTracks | None = artist.get_tracks(
            page_size=50)
        if tracks is None:
            raise Exception('Failed to get the artis')
        playlist: list[Track] = [YMTrack(track) for track in tracks.tracks]
        source = Source(type='artist', id=artist_id, name=artist.name)
        self.set_playlist(playlist, source)
        self.play()

    def play_album(self, album_id: str):
        album: yandex_music.Album | None = self.client.albums_with_tracks(
            album_id=album_id)
        if album is None:
            raise Exception('Failed to get the album')

        tracks = None
        if tracks is None:
            raise Exception('Failed to get the artis')
        playlist: list[Track] = [YMTrack(track) for track in tracks.tracks]
        source = Source(type='album', id=album_id, name=album.title)
        self.set_playlist(playlist, source)
        self.play()

    def play_from_query(self, query: str):
        (ym_playlist, original) = self.__generate_playlist_from_query(query)
        if original is None:
            raise Exception('Fucked up')

        t = str(type(original)).split('.')[-1][:-2].lower()
        playlist: list[Track] = [YMTrack(track) for track in ym_playlist]
        source = Source(
            type=t,
            id=str(original.uid if isinstance(
                original, yandex_music.Playlist) else original.id),
            name=original.name if isinstance(
                original, yandex_music.Artist) else original.title,
            query=query
        )
        self.set_playlist(playlist, source)
        self.play()

    @ ttl_cache(maxsize=1, ttl=60 * 60)  # type: ignore
    def fetch_predefinded_playlists(self):
        PersonalPlaylistBlocks = self.client.landing(
            blocks=['personalplaylists']).blocks[0]
        playlists = []

        for x in PersonalPlaylistBlocks.entities:
            playlists.append(
                x.data.data.generated_playlist_type)  # type: ignore
        return [*playlists, 'liked']

    def __get_playlist_by_name(self, name: str):
        if name == 'liked':
            tracks = self.client.users_likes_tracks()
            if tracks is None:
                raise Exception('No tracks found')
            return (tracks.tracks, tracks)

        PersonalPlaylistBlocks = self.client.landing(
            blocks=['personalplaylists']).blocks[0]

        DailyPlaylist = next(
            x.data.data for x in PersonalPlaylistBlocks.entities if x.data.data.generated_playlist_type == name  # type: ignore
        )

        if DailyPlaylist is None:
            raise Exception()

        playlist: yandex_music.Playlist = self.client.users_playlists(
            user_id=DailyPlaylist.uid, kind=DailyPlaylist.kind)  # type: ignore

        return (playlist.tracks, playlist)

    def __get_playlist_by_id(self, id: str) -> tuple[list[yandex_music.Track | yandex_music.TrackShort], yandex_music.Playlist]:
        playlist: yandex_music.Playlist = self.client.playlists_list(
            playlist_ids=[int(id)])[0]

        return (playlist.fetch_tracks(), playlist)  # type: ignore

    def __generate_playlist_from_query(self, query):
        search_result = self.client.search(query)
        resulting_playlist: list[yandex_music.Track |
                                 yandex_music.TrackShort] = []
        best: yandex_music.Playlist | yandex_music.Track | yandex_music.Artist | yandex_music.Album | None = None
        if search_result.best:
            type_ = search_result.best.type
            best = search_result.best.result  # type: ignore

            if type_ in ['track', 'podcast_episode']:
                if isinstance(best, yandex_music.Track):
                    resulting_playlist = [best]
            elif type_ == 'artist':
                if isinstance(best, yandex_music.Artist):
                    resulting_playlist = best.get_tracks()  # type: ignore

            elif type_ in ['album', 'podcast']:
                if isinstance(best, yandex_music.Album):
                    resulting_playlist = [
                        track for volume in best.volumes for track in volume]

            elif type_ == 'playlist':
                if isinstance(best, yandex_music.Playlist):
                    resulting_playlist = best.tracks  # type: ignore
        return (resulting_playlist, best)
