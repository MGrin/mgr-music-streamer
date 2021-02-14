from streamers.streamer import Streamer

HELP = "help"
LIST_PROVIDERS = "list:providers"
LIST_PREDEFINED_PLAYLISTS = "list:pl"
PLAYLIST_ACTION_PREFIX = "pl:"
SEARCH_ACTION_PREFIX = "q:"
PLAY = "play"
PAUSE = "pause"
NEXT = "next"
PREV = "prev"
STOP = "stop"


def cli_handler(streamers: dict[str, Streamer]):
    streamers_names = list(streamers.keys())
    if len(streamers_names) == 0:
        raise Exception('No streamers provided')

    streamer = streamers[streamers_names[0]]

    print('Type help to see available commands')
    print()
    while True:
        action = input(f"{streamer.title} > ")
        try:
            if action == HELP:
                print("CLI Music Streamer controller.")
                print("Available commands:")
                print(f' {HELP} - shows this help')
                print(f' {LIST_PROVIDERS} - shows all available music providers')
                print(
                    f' {LIST_PREDEFINED_PLAYLISTS} - shows list of predefined playlists')
                print(
                    f' {PLAYLIST_ACTION_PREFIX}<PLAYLIST NAME> - plays the provided playlist')
                print(
                    f' {SEARCH_ACTION_PREFIX}<QUERY> - plays the best match of the given query')
                print(f' {PLAY}')
                print(f' {PAUSE}')
                print(f' {NEXT}')
                print(f' {PREV}')
                print(f' {STOP}')
            elif action == LIST_PREDEFINED_PLAYLISTS:
                predefined_playlists = streamer.fetch_predefinded_playlists()
                print('Available predefined playlists:')
                for pl in predefined_playlists:
                    print(f' - {pl}')
                print('To play one of them just type pl:<NAME OF THE PLAYLIST>')
            elif action == LIST_PROVIDERS:
                print('Available providers:')
                for st in streamers.values():
                    is_selected = "✅" if st.title == streamer.title else ' '
                    print(f' [{is_selected}] {st.title}')
                print(
                    'To change active provider just type provider:<NAME OF THE PROVIDER>')
            elif action.startswith(PLAYLIST_ACTION_PREFIX):
                streamer.play_predefined_playlist(
                    action[len(PLAYLIST_ACTION_PREFIX):])
            elif action.startswith(SEARCH_ACTION_PREFIX):
                streamer.play_from_query(action[len(SEARCH_ACTION_PREFIX):])
            elif action == PLAY:
                streamer.play()
            elif action == PAUSE:
                streamer.pause()
            elif action == NEXT:
                streamer.next()
            elif action == PREV:
                streamer.prev()
            elif action == STOP:
                streamer.stop()
            else:
                raise Exception(f'Unknown action {action}')

            print()
        except Exception as e:
            print(f'Error: {e}')
