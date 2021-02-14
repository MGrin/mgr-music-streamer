from __future__ import annotations

from pathlib import Path
from yandex_music.track.track import Track
from yandex_music.track_short import TrackShort
import yaml
from collections import namedtuple


CACHE_FOLDER = './cache'


def cast_to_track(item: Track | TrackShort):
    track: Track = item if isinstance(
        item, Track) else item.track or item.fetchTrack()

    return track


def cache_track(track: Track):
    artist_dir = Path(f'{track.artists[0].name}_{track.artists[0].id}')
    album_dir = Path(f'{track.albums[0].title}_{track.albums[0].id}')
    file_path = CACHE_FOLDER / artist_dir / \
        album_dir / f'{track.title}_{track.id}.mp3'

    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        track.download(str(file_path))

    return str(file_path)


DEFAULT_CONFIGS = {
    "debug": False,
    "providers": [],
    "controllers": [{
        "cli": True
    }]
}


def get_configs():
    configs = DEFAULT_CONFIGS.copy()

    config_path = Path('./config.yaml')
    if not config_path.exists():
        return namedtuple('Configurations', configs.keys())(**configs)

    with open("config.yaml", "r") as config_file:
        provided_configs = yaml.load(config_file, Loader=yaml.FullLoader)

    configs['debug'] = provided_configs.get(
        'debug') if provided_configs.get('debug') is not None else configs['debug']
    configs['providers'] = provided_configs.get(
        'providers') or configs['providers']
    configs['controllers'] = provided_configs.get(
        'controllers') or configs['controllers']

    return namedtuple('Configurations', configs.keys())(**configs)
