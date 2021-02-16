from controllers.controller import success_response
from controllers.controller import Controller
from streamers.streamer import Streamer

HELP = "help"
LIST_PROVIDERS = "list:providers"
SELECT_PROVIDER_ACTION_PREFIX = "provider:"
LIST_PREDEFINED_PLAYLISTS = "list:pl"
PLAYLIST_ACTION_PREFIX = "pl:"
SEARCH_ACTION_PREFIX = "q:"
PLAY = "play"
PAUSE = "pause"
NEXT = "next"
PREV = "prev"
STOP = "stop"
STATE = "state"


class CliController(Controller):
    def help(self):
        message = "CLI Music Streamer controller.\nAvailable commands:"
        data = {
            HELP: "shows this help'",
            LIST_PROVIDERS: "shows all available music providers'",
            SELECT_PROVIDER_ACTION_PREFIX: "< PROVIDER NAME > switch to PROVIDER NAME provider'",
            LIST_PREDEFINED_PLAYLISTS: "shows list of predefined playlists'",
            PLAYLIST_ACTION_PREFIX: "< PLAYLIST NAME > plays the provided playlist'",
            SEARCH_ACTION_PREFIX: "< QUERY > plays the best match of the given query'",
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
        action_raw = input(f"{controller.active_streamer.title} > ")
        action = action_raw.lower()
        if action == HELP:
            resp = controller.help()
            print(resp.message)
            for cmd in resp.data:
                desc = resp.data[cmd]
                print(f' - {cmd} - {desc}')

        elif action == LIST_PREDEFINED_PLAYLISTS:
            resp = controller.list_playlists()
            print(resp.message)
            for pl in resp.data:
                print(f' - {pl}')

        elif action == LIST_PROVIDERS:
            resp = controller.list_streamers()
            print(resp.message)
            for pl in resp.data:
                print(f' - {pl}')

        elif action.startswith(SELECT_PROVIDER_ACTION_PREFIX):
            provider_title = action[len(SELECT_PROVIDER_ACTION_PREFIX):]
            resp = controller.select_provider(provider_title)
            print(resp.message)

        elif action.startswith(PLAYLIST_ACTION_PREFIX):
            playlist = action[len(PLAYLIST_ACTION_PREFIX):]
            resp = controller.select_playlist(playlist)
            print(resp.message)
            resp = controller.state()
            print(resp.message)

        elif action.startswith(SEARCH_ACTION_PREFIX):
            query = action[len(SEARCH_ACTION_PREFIX):]
            resp = controller.select_search(query)
            print(resp.message)
            resp = controller.state()
            print(resp.message)

        elif action == PLAY:
            resp = controller.play()
            resp = controller.state()
            print(resp.message)
        elif action == PAUSE:
            resp = controller.pause()
            resp = controller.state()
            print(resp.message)
        elif action == NEXT:
            resp = controller.next()
            resp = controller.state()
            print(resp.message)
        elif action == PREV:
            resp = controller.prev()
            resp = controller.state()
        elif action == STOP:
            resp = controller.stop()
            print(resp.message)
        elif action == STATE:
            resp = controller.state()
            print(resp.message)
        else:
            raise Exception(f'Unknown action {action}')

        print()
