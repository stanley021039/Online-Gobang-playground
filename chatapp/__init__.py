from flask import Flask, request, render_template, make_response
from flask_restful import Api, Resource
import requests

from .events import socketio, rooms
from .Resource import ImagesResource, RoomsResource
from .routes import main


def create_app():
    app = Flask(__name__)
    api = Api(app)

    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"

    @app.before_request
    def set_application_root():
        script_name = request.headers.get('X-Script-Name', '')
        app.config['APPLICATION_ROOT'] = script_name
    
    app.register_blueprint(main)

    socketio.init_app(app, ping_timeout=5, ping_interval=5, async_mode='threading', cors_allowed_origins="*")
    api.add_resource(ImagesResource, f"{app.config['APPLICATION_ROOT']}/images")
    api.add_resource(RoomsResource, f"{app.config['APPLICATION_ROOT']}/rooms/<roomname>")

    return app