from __future__ import annotations
from player import PlayerState
from streamers.ymstreamer import YMTrack

from controllers.controller import Controller, Response as ControllerResponse
from copy import deepcopy
from typing import Any
from streamers.streamer import Streamer
from flask import Flask, request, Response
import logging
import jsonpickle


class HTTPController(Controller):
    def help(self):
        return Response(
            {"status": int, "message": "Method not allowed"},
            status=405,
            mimetype='application/json'
        )


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
    controller = HTTPController(streamers)
    app = Flask(__name__)
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True

    @app.route('/help')
    def help(self):
        return controller.help()

    @app.route('/providers', methods=['GET'])
    def list_providers():
        return json_response(controller.list_streamers())

    @app.route('/providers', methods=['POST'])
    def select_provider():
        provider = request.get_json()['provider']
        return json_response(controller.select_provider(provider))

    @app.route('/playlists', methods=['GET'])
    def list_playlists():
        return json_response(controller.list_playlists())

    @app.route('/playlists', methods=['POST'])
    def select_playlist():
        playlist = request.get_json()['playlist']
        return json_response(controller.select_playlist(playlist))

    @app.route('/search', methods=['POST'])
    def select_search():
        query = request.get_json()['query']
        return json_response(controller.select_search(query))

    @app.route('/play', methods=['PUT'])
    def play():
        return json_response(controller.play())

    @app.route('/pause', methods=['PUT'])
    def pause():
        return json_response(controller.pause())

    @app.route('/next', methods=['PUT'])
    def next():
        return json_response(controller.next())

    @app.route('/prev', methods=['PUT'])
    def prev():
        return json_response(controller.prev())

    @app.route('/stop', methods=['PUT'])
    def stop():
        return json_response(controller.stop())

    @app.route('/state', methods=['GET'])
    def state():
        return json_response(controller.state())

    app.run(port=args['port'], debug=False)
