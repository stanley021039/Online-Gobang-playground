import requests

from flask import request, current_app
from flask_socketio import emit, join_room

from .extensions import socketio
from .room import Rooms
from .utils import user_verify

# {username: {sid: , roomhash: , chara: }}
users = {"AI_PLAYER": {"sid": -1, "roomhash": None, "chara": None},
         "system": {"sid": 0, "roomhash": None, "chara": None},
        }
rooms = Rooms(socketio)

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on('disconnect')
def handle_disconnect():
    for username in users:
        if users[username]['sid'] == request.sid:
            roomhash = users[username]['roomhash']
            chara = users[username]['chara']
            if roomhash is not None:
                room_info = rooms.user_leave(roomhash, username)
                if room_info is not None:
                    emit("online_user_update", room_info, room=roomhash)
            del users[username]
            print(f"room_{roomhash}: {username} ({chara}) leave!")
            emit("chat", {"username": "system", "message": f"{username} 離開"}, room=roomhash)
            break

@socketio.on("user_join_lobby")
def handle_user_join_lobby(username):
    if username in users:  # username existed
        print(f"User {username} already exist...")
        emit("user_join_lobby_response", {"accept": False, "message": f"User {username} already exist..."})
        return
    print(f"User {username} join lobby")
    users[username] = {'sid': request.sid, "roomhash": "lobby", "chara": None}
    join_room("lobby")
    emit("user_join_lobby_response", {"accept": True, "message": f"Join lobby success"})
    emit("chat", {"username": "system", "message": f"{username} 加入大廳"}, room="lobby")

# 檢查房間資訊是否正確
@socketio.on("knock_room")
def handle_knock_room(roomhash, password):
    password = password if password else None
    if roomhash in rooms.all_rooms:
        room = rooms.all_rooms[roomhash]
        if room.password == password:
            emit("knock_room_response", {"accept": True, "message": "success"})
            return
        emit("knock_room_response", {"accept": False, "message": "Wrong password"})
        return
    emit("knock_room_response", {"accept": False, "message": "Room doesn't exist"})

@socketio.on("user_join_room")
def handle_user_join_room(roomhash, password, username):
    password = password if password else None
    # 該房間已有相同用戶
    if username in users:
        print(f"User {username} already exist...")
        emit("user_join_room_response", {"accept": False, "message": f"User {username} already exist..."})
        return
    room_info, message = rooms.user_join(roomhash, password, username)
    # 房間不存在 or 密碼錯誤
    if room_info is None:
        emit("user_join_room_response", {"accept": False, "message": message})
    else:
        chara, black_user, white_user, observer, borad_pattern = room_info["chara"], room_info["black_user"], room_info["white_user"], room_info["observer"], room_info["borad_pattern"]
        users[username] = {'sid': request.sid, "roomhash": roomhash, "chara": chara}
        join_room(roomhash)
        print(f"User {username} join room_{roomhash}")
        emit("user_join_room_response", {"accept": True, "roomhash":roomhash, "chara": chara, "borad_pattern": borad_pattern, "message": message})
        emit("online_user_update", {"black_user": black_user, "white_user": white_user, "observer": observer}, room=roomhash)
        emit("chat", {"username": "system", "message": f"{username} ({chara}) 加入房間"}, room=roomhash)

# 用戶添加/移除AI
@socketio.on("set_AI")
def handle_set_AI(roomhash, username, userchara, chara):
    if user_verify(users, request.sid, roomhash, userchara, username):
        response = rooms.set_ai(roomhash, chara)
        emit("online_user_update", response, room=roomhash)

# 用戶更換角色
@socketio.on("user_move")
def handle_user_move(roomhash, username, userchara_ori, chara_tar):
    if not user_verify(users, request.sid, roomhash, userchara_ori, username):
        return
    if userchara_ori == chara_tar:
        return
    response = rooms.user_move(roomhash, username, userchara_ori, chara_tar)
    if response["accept"]:
        users[username]['chara'] = chara_tar
        emit("user_move_response", {"accept": True, "chara": chara_tar})
        emit("online_user_update", response, room=roomhash)

# 用戶新建房間
@socketio.on("create_room")
def handle_create_room(roomname, password, username):
    response = rooms.create(username, roomname, password if password != "" else None)
    emit("create_room_response", response)

# 用戶傳送訊息
@socketio.on("new_message")
def handle_new_message(roomhash, message):
    print(f"New message in room_{roomhash}: {message}")
    username = None 
    for user in users:
        if users[user]['sid'] == request.sid:
            username = user
    emit("chat", {"username": username, "message": message}, room=roomhash)

# 用戶落子
@socketio.on("get_move")
def handle_get_move(roomhash, username, userchara, move: list[int]):
    boart_state_message_mp = {
        0: "遊戲進行中...",
        1: "黑棋獲勝!!",
        2: "白棋獲勝!!",
        3: "平局"
    }
    if not user_verify(users, request.sid, roomhash, userchara, username):
        print(f"{username} verification failed...")
        emit("get_move_response", {"state": -1, "message": "verification failed..."})
        return
    state = rooms.all_rooms[roomhash].get_move(username, userchara, move)
    if state["move_accept"]:
        emit("someone_move", {"chara": userchara, 'move': move, "board_state": state["board_state"]}, room=roomhash)
        if state["board_state"] != 0:  # end
            emit("chat", {"username": "system", "message": boart_state_message_mp[state["board_state"]]}, room=roomhash)
    emit("get_move_response", {"message": state["move_message"]})

# 用戶重新開始
@socketio.on("restart")
def handle_restart(roomhash, username, userchara):
    if user_verify(users, request.sid, roomhash, userchara, username):
        rooms.all_rooms[roomhash].restart(username)
        emit("restart", room=roomhash)
        emit("chat", {"username": "system", "message": f"{username} restart!"}, room=roomhash)
