from __future__ import annotations
from controllers.controller import Controller

from typing import Any
from streamers.streamer import Streamer
from flask import Flask, request, Response
import logging


class HTTPController(Controller):
    def help(self):
        return Response(
            {"status": int, "message": "Method not allowed"},
            status=405,
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
        return controller.list_streamers().__dict__

    @app.route('/providers', methods=['POST'])
    def select_provider():
        provider = request.get_json()['provider']
        return controller.select_provider(provider).__dict__

    @app.route('/playlists', methods=['GET'])
    def list_playlists():
        return controller.list_playlists().__dict__

    @app.route('/playlists', methods=['POST'])
    def select_playlist():
        playlist = request.get_json()['playlist']
        return controller.select_playlist(playlist).__dict__

    @app.route('/search', methods=['POST'])
    def select_search():
        query = request.get_json()['query']
        return controller.select_search(query).__dict__

    @app.route('/play', methods=['PUT'])
    def play():
        return controller.play().__dict__

    @app.route('/pause', methods=['PUT'])
    def pause():
        return controller.pause().__dict__

    @app.route('/next', methods=['PUT'])
    def next():
        return controller.next().__dict__

    @app.route('/prev', methods=['PUT'])
    def prev():
        return controller.prev().__dict__

    @app.route('/stop', methods=['PUT'])
    def stop():
        return controller.stop().__dict__

    app.run(port=args['port'], debug=False)
