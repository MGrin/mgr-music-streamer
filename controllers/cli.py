from controllers.controller import Response, catch, success_response
from controllers.controller import Controller
from streamers.streamer import Streamer

HELP = "help"
LIST_PROVIDERS = "list:providers"
SELECT_PROVIDER_ACTION_PREFIX = "provider:"
LIST_PREDEFINED_PLAYLISTS = "list:pl"
PLAYLIST_ACTION_PREFIX = "pl:"
SEARCH_ACTION_PREFIX = "q:"
ARTIST_ACTION_PREFIX = "ar:"
ALBUM_ACTION_PREFIX = "al:"
PLAY = "play"
PAUSE = "pause"
NEXT = "next"
PREV = "prev"
STOP = "stop"
STATE = "state"


class CliController(Controller):
    @catch
    def help(self):
        message = "CLI Music Streamer controller.\nAvailable commands:"
        data = {
            HELP: "shows this help'",
            LIST_PROVIDERS: "shows all available music providers'",
            SELECT_PROVIDER_ACTION_PREFIX: "< PROVIDER NAME > switch to PROVIDER NAME provider'",
            LIST_PREDEFINED_PLAYLISTS: "shows list of predefined playlists'",
            PLAYLIST_ACTION_PREFIX: "< PLAYLIST_NAME | PLAYLIST_ID > plays the provided playlist'",
            SEARCH_ACTION_PREFIX: "< QUERY > plays the best match of the given query'",
            ARTIST_ACTION_PREFIX: "<ARTIS_ID> plays the provided artis by id",
            STATE: "show what is playing now'",
            PLAY: "",
            PAUSE: "",
            NEXT: "",
            PREV: "",
            STOP: "",
        }
        return success_response(data=data, message=message)


def cli_handler(streamers: dict[str, Streamer]):
    controller = CliController(streamers)

    print('Type help to see available commands')
    print()
    while True:
        action = input(f"{controller.active_streamer.title} > ")

        if action == HELP:
            resp = controller.help()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                for cmd in resp.data:
                    desc = resp.data[cmd]
                    print(f' - {cmd} - {desc}')

        elif action == LIST_PREDEFINED_PLAYLISTS:
            resp = controller.list_playlists()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                for pl in resp.data:
                    print(f' - {pl}')

        elif action == LIST_PROVIDERS:
            resp = controller.list_streamers()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                for pl in resp.data:
                    print(f' - {pl}')

        elif action.startswith(SELECT_PROVIDER_ACTION_PREFIX):
            provider_title = action[len(SELECT_PROVIDER_ACTION_PREFIX):]
            resp = controller.select_provider(provider_title)
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)

        elif action.startswith(PLAYLIST_ACTION_PREFIX):
            playlist = action[len(PLAYLIST_ACTION_PREFIX):]
            resp = controller.select_playlist(playlist)
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                resp = controller.state()
                print(resp.message)

        elif action.startswith(SEARCH_ACTION_PREFIX):
            query = action[len(SEARCH_ACTION_PREFIX):]
            resp = controller.select_search(query)
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                resp = controller.state()
                print(resp.message)

        elif action.startswith(ARTIST_ACTION_PREFIX):
            artist = action[len(ARTIST_ACTION_PREFIX):]
            resp = controller.select_artist(artist)
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                resp = controller.state()
                print(resp.message)

        elif action.startswith(ALBUM_ACTION_PREFIX):
            album = action[len(ALBUM_ACTION_PREFIX):]
            resp = controller.select_artist(album)
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
                resp = controller.state()
                print(resp.message)

        elif action == PLAY:
            resp = controller.play()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                resp = controller.state()
                print(resp.message)
        elif action == PAUSE:
            resp = controller.pause()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                resp = controller.state()
                print(resp.message)
        elif action == NEXT:
            resp = controller.next()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                resp = controller.state()
                print(resp.message)
        elif action == PREV:
            resp = controller.prev()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                resp = controller.state()
        elif action == STOP:
            resp = controller.stop()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
        elif action == STATE:
            resp = controller.state()
            if resp.status != 200:
                print(f'Error [{resp.status}]: {resp.message}')
            else:
                print(resp.message)
        else:
            resp = Response(500, f"Unknown command: {action}")
            print(f'Error [{resp.status}]: {resp.message}')

        print()
