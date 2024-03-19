from flask import Blueprint, request, make_response, render_template

from .events import rooms

main = Blueprint("main", __name__)

@main.route("/")
def index():
    username = request.args.get('username')
    script_name = request.headers.get('X-Script-Name', '')
    rooms_info = rooms.get_all_rooms()
    return make_response(render_template('lobby.html', APPLICATION_ROOT=script_name, username=username, rooms_info=rooms_info))