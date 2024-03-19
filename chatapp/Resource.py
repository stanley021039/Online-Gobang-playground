import os

from flask import Flask, request, send_file, render_template, make_response, redirect, url_for
from flask_restful import Resource

from .events import rooms

class ImagesResource(Resource):
    def get(self):
        image_name = request.args.get('imgname', '')
        image_url = os.path.join(f"img/{image_name}")
        return send_file(image_url, mimetype='image/jpeg')

class RoomsResource(Resource):
    def get(self, roomname):
        username = request.args.get('username')
        script_name = request.headers.get('X-Script-Name', '')
        return make_response(render_template('room.html', APPLICATION_ROOT=script_name, roomname=roomname, username=username))
