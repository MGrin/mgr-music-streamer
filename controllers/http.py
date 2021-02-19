from __future__ import annotations
from functools import wraps
from player.state import PlayerState
from gevent.pywsgi import WSGIServer

from controllers.controller import Controller, Response as ControllerResponse
from copy import deepcopy
from typing import Any
from streamers.streamer import Streamer
from flask import Flask, request, Response
import logging
import jsonpickle


ENDPOINTS = {
    '/help': {
        'method': 'GET',
        'title': 'Help',
        'description': 'Show all available endpoints',
    },
    '/providers': [{
        'method': 'GET',
        'title': 'Providers',
        'description': 'See a list of available music providers',
    }, {
        'method': 'POST',
        'title': 'Select provider',
        'description': 'Select/switch a provider',
        'body': '{ "provider": <PROVIDER_NAME> }'
    }],
    '/playlists': [{
        'method': 'GET',
        'title': 'Playlists',
        'description': 'List available predefined playlists',
    }, {
        'method': 'POST',
        'title': 'Play playlist',
        'description': 'Switches the player to a provided playlist\nNote, if passing the playlist id, it should be in for owner_id:playlist_id',
        'body': '{ "playlist": <PLAYLIST_NAME | PLAYLIST_ID> }'
    }],
    '/search': {
        'method': 'POST',
        'title': 'Play from query',
        'description': 'Plays the best result for a provided query',
        'body': '{ "query": <QUERY> }'
    },
    '/play': {
        'method': 'PUT',
        'title': 'Play',
        'description': 'Play',
    },
    '/pause': {
        'method': 'PUT',
        'title': 'Pause',
        'description': 'Toggle the pause on/off',
    },
    '/next': {
        'method': 'PUT',
        'title': 'Next track',
        'description': 'Next track',
    },
    '/prev': {
        'method': 'PUT',
        'title': 'Previous track',
        'description': 'Previous track',
    },
    '/stop': {
        'method': 'PUT',
        'title': 'Stop',
        'description': 'Stop the music',
    },
    '/state': {
        'method': 'GET',
        'title': 'Get state',
        'description': 'Returns a current player state',
    },
}


class HTTPController(Controller):
    def __init__(self, streamers: dict[str, Streamer], auth_token: str):
        super().__init__(streamers)
        self.token = auth_token

    def is_authorized(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return ControllerResponse(status=401, message="Unauthorized")
        auth_token = auth_header.split(" ")[1]
        if auth_token != self.token:
            return ControllerResponse(status=401, message="Unauthorized")
        return None

    def help(self):
        return ControllerResponse(status=200, message='Help', data=ENDPOINTS)


def json_response(response: ControllerResponse):
    copied_response = deepcopy(response)
    if isinstance(copied_response.data, PlayerState):
        if copied_response.data.prev_track is not None:
            del copied_response.data.prev_track._YMTrack__original  # type: ignore
            del copied_response.data.prev_track._YMTrack__fetched  # type: ignore
        if copied_response.data.track is not None:
            del copied_response.data.track._YMTrack__original  # type: ignore
            del copied_response.data.track._YMTrack__fetched  # type: ignore
        if copied_response.data.next_track is not None:
            del copied_response.data.next_track._YMTrack__original  # type: ignore
            del copied_response.data.next_track._YMTrack__fetched  # type: ignore

    return Response(
        jsonpickle.encode(copied_response, unpicklable=False),
        mimetype='application/json'
    )


def http_handler(streamers: dict[str, Streamer], args: dict[str, Any]):
    controller = HTTPController(streamers, args['token'])
    app = Flask(__name__)
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True

    def authorized(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            auth_error = controller.is_authorized()
            if auth_error is not None:
                return json_response(auth_error)
            return f(*args, **kwds)
        return wrapper

    @app.route('/help')
    @authorized
    def help():
        return json_response(controller.help())

    @app.route('/providers', methods=['GET'])
    @authorized
    def list_providers():
        return json_response(controller.list_streamers())

    @app.route('/providers', methods=['POST'])
    @authorized
    def select_provider():
        provider = request.get_json()['provider']
        return json_response(controller.select_provider(provider))

    @app.route('/playlists', methods=['GET'])
    @authorized
    def list_playlists():
        return json_response(controller.list_playlists())

    @app.route('/playlists', methods=['POST'])
    @authorized
    def select_playlist():
        playlist = request.get_json()['playlist']
        return json_response(controller.select_playlist(playlist))

    @app.route('/artist', methods=['POST'])
    @authorized
    def select_artist():
        artist = request.get_json()['artist']
        return json_response(controller.select_artist(artist))

    @app.route('/album', methods=['POST'])
    @authorized
    def select_album():
        album = request.get_json()['album']
        return json_response(controller.select_album(album))

    @app.route('/search', methods=['POST'])
    @authorized
    def select_search():
        query = request.get_json()['query']
        return json_response(controller.select_search(query))

    @app.route('/play', methods=['PUT'])
    @authorized
    def play():
        return json_response(controller.play())

    @app.route('/pause', methods=['PUT'])
    @authorized
    def pause():
        return json_response(controller.pause())

    @app.route('/next', methods=['PUT'])
    @authorized
    def next():
        return json_response(controller.next())

    @app.route('/prev', methods=['PUT'])
    @authorized
    def prev():
        return json_response(controller.prev())

    @app.route('/stop', methods=['PUT'])
    @authorized
    def stop():
        return json_response(controller.stop())

    @app.route('/state', methods=['GET'])
    @authorized
    def state():
        return json_response(controller.state())

    http_server = WSGIServer(('', args['port']), app, log=log, error_log=log)
    http_server.serve_forever()
