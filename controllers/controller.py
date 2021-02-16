from __future__ import annotations
from functools import wraps

from streamers.streamer import Streamer
from typing import Any


class Response:
    def __init__(self, status: int = 200, message: str = None, data: Any = None):
        self.status = status
        self.message = message
        self.data = data


def success_response(data: dict[str, Any] | list[Any] | Any = None, message: str = None):
    return Response(message=message, data=data)


def catch(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            res = f(*args, **kwds)
            return res
        except Exception as e:
            return Response(status=500, message=str(e), data=e)

    return wrapper


class Controller:
    def __init__(self, streamers: dict[str, Streamer]):
        self.streamers = streamers
        self.active_streamer: Streamer = [
            st for st in streamers.values() if st.is_running][0]

    def help(self):
        raise Exception('Not implemented')

    @catch
    def state(self):
        state = self.active_streamer.get_state()
        message = 'Stopped'
        if state.is_playing:
            message = str(state)

        return success_response(state, message)

    @catch
    def list_streamers(self):
        providers = []
        for st in self.streamers.values():
            providers.append({
                "title": st.title,
                "is_active": st.is_running,
            })
        return success_response(providers, "List of available providers")

    @catch
    def select_provider(self, provider: str):
        self.active_streamer.kill()
        for st in self.streamers.values():
            if st.title == provider:
                self.active_streamer = st
                break
        self.active_streamer.run()
        return success_response({"active_streamer": self.active_streamer.title}, f"Active streamer: {self.active_streamer.title}")

    @catch
    def list_playlists(self):
        playlists = self.active_streamer.fetch_predefinded_playlists()
        return success_response(playlists, "Available playlists")

    @catch
    def select_predefined_playlist(self, playlist: str):
        playlists = self.active_streamer.fetch_predefinded_playlists()
        if playlist in playlists:
            self.active_streamer.play_predefined_playlist(playlist)
        else:
            self.active_streamer.play_playlist(playlist)
        return success_response(self.active_streamer.get_state(), f"Playing {playlist} playlist")

    @catch
    def select_search(self, query):
        self.active_streamer.play_from_query(query)
        return success_response(self.active_streamer.get_state(), f"Playing best result for {query} search")

    @catch
    def play(self):
        self.active_streamer.play()
        return success_response(self.active_streamer.get_state())

    @catch
    def pause(self):
        self.active_streamer.pause()
        return success_response(self.active_streamer.get_state())

    @catch
    def next(self):
        self.active_streamer.next()
        return success_response(self.active_streamer.get_state())

    @catch
    def prev(self):
        self.active_streamer.prev()
        return success_response(self.active_streamer.get_state())

    @catch
    def stop(self):
        self.active_streamer.stop()
        return success_response(self.active_streamer.get_state())
