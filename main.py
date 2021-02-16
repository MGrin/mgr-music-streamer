from __future__ import annotations
from streamers.streamer import Streamer
from utils import get_configs
from time import sleep
from streamers.ymstreamer import YMStreamer
from threading import Thread


def runController(handler, streamers, args=None):
    thread_args = (streamers, args) if args is not None else (streamers,)
    t = Thread(target=handler, daemon=True, args=thread_args)
    t.start()


def keep_main_thread_alive():
    while True:
        sleep(10)


def main():
    configs = get_configs()
    streamers: dict[str, Streamer] = {}
    providers_names = list(configs.providers.keys())

    if len(providers_names) == 0:
        raise Exception('No streamers provided')

    if 'yandex_music' in configs.providers is not None:
        ym_configs = configs.providers['yandex_music']
        streamers['yandex_music'] = YMStreamer(
            ym_configs['username'], ym_configs['password'], ym_configs['title'], debug=configs.debug)

    streamers[providers_names[0]].run()

    if 'http' in configs.controllers:
        from controllers.http import http_handler
        runController(http_handler, streamers, configs.controllers['http'])

    if 'cli' in configs.controllers:
        from controllers.cli import cli_handler
        runController(cli_handler, streamers)

    keep_main_thread_alive()


if __name__ == '__main__':
    main()
