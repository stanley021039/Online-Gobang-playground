from math import floor
import threading
import time

import numpy as np

from .chess_board import ChessBoard
from .utils import generate_room_hash, tuple_2d_to_numpy_2d
from .alpha_zero_gomoku.AI_player import AI

AI_PLAYER = AI()
AI_PLAYER.load_model(folder="chatapp/alpha_zero_gomoku/model")

# 記錄所有Room
class Rooms:
    def __init__(self, socketio):
        self.all_rooms = {}
        self.socketio = socketio
        example_rooms = [("system", "ex_room1", None), ("system", "ex_room2_pwd=123", "123")]
        for (host, roomname, password) in example_rooms:
            self.create(host, roomname, password, is_solid=True)

    def create(self, host, roomname, password, is_solid=False):
        room_hash = generate_room_hash()
        while room_hash in self.all_rooms:
            room_hash = generate_room_hash()
        try:
            new_room = GobangRoom(host=host, name=roomname, hash_=room_hash, password=password, is_solid=is_solid, socketio=self.socketio)
            self.all_rooms[room_hash] = new_room
            print(f'creat room_{room_hash} success')
            return {'accept': True, 'roomhash': room_hash}
        except ValueError as e:
            print("Error creating room:", e)
            return {'accept': False, 'roomhash': None}

    def close_room(self, roomhash):
        print(f"close room_{roomhash}")
        del self.all_rooms[roomhash]

    def get_all_rooms(self):
        rooms_info = []
        for roomhash, room in self.all_rooms.items():
            rooms_info.append({"name": room.name, "hash": roomhash, "black_user": room.black_user, "white_user": room.white_user, "need_pwd": room.need_pwd})
        return rooms_info

    def check_room_exist(self, roomhash):
        return roomhash in self.all_rooms
    
    def user_join(self, roomhash, password, username):
        if self.check_room_exist(roomhash):
            room = self.all_rooms[roomhash]
            if room.password != password:
                return None, "Wrong password"
            room_info = self.all_rooms[roomhash].user_join(username)
            return room_info, f"Join room_{roomhash} success"
        return None, "Room doesn't exist"
    
    def user_leave(self, roomhash, username):
        if self.check_room_exist(roomhash):
            room = self.all_rooms[roomhash]
            is_empty, room_info = room.user_leave_and_check_empty(username)
            if is_empty and not room.is_solid: self.close_room(roomhash)
            return room_info
        return None

    def user_move(self, roomhash, username, userchara_ori, chara_tar):
        if self.check_room_exist(roomhash):
            room = self.all_rooms[roomhash]
            return room.user_move(username, userchara_ori, chara_tar)

    def set_ai(self, roomhash, chara):
        if self.check_room_exist(roomhash):
            room = self.all_rooms[roomhash]
            return room.set_ai_player(chara)


class GobangRoom:
    def __init__(self, host: str, name: str, hash_: str, password: str=None, is_solid: bool=False, socketio=None, board_len: int=15):
        self.host = host
        self.name = name
        self.hash = hash_
        self.password = password
        self.need_pwd = True if password is not None else False
        self.is_solid = is_solid
        self.socketio = socketio
        self.board_len = board_len
        self.board = ChessBoard(board_len=board_len, n_feature_planes=6)
        self.users_count = 0
        self.black_user = None
        self.white_user = None
        self.observer = 0
        self.black_turn = True
        self.lock = threading.Lock()
        self.boart_state_message_mp = {
            0: "遊戲進行中",
            1: "黑棋獲勝!!",
            2: "白棋獲勝!!",
            3: "平局"
        }
        # 若創建時AI先手，調用一次Thread
        if self.black_user == "AI_PLAYER":
            ai_thread = threading.Thread(target=self.run_ai_model_thread)
            ai_thread.start()

    # 用戶加入，優先分配：黑>白>觀眾
    def user_join(self, username: str):
        borad_pattern = self.board.state_planes
        if self.black_user is None:
            self.users_count += 1
            self.black_user = username
            response = self.get_room_state()
            response["chara"] = "black"
            return response
        elif self.white_user is None:
            self.users_count += 1
            self.white_user = username
            response = self.get_room_state()
            response["chara"] = "white"
            return response
        else:
            self.observer += 1
            response = self.get_room_state()
            response["chara"] = "observer"
            return response

    # 用戶離開，人數為0時回傳is_empty
    def user_leave_and_check_empty(self, username: str):
        if username == self.black_user:
            self.black_user = None
            self.users_count -= 1
            return False if self.users_count > 0 else True, {"host": self.host, "black_user": self.black_user, "white_user": self.white_user, "observer": self.observer}
        elif username == self.white_user:
            self.white_user = None
            self.users_count -= 1
            return False if self.users_count > 0 else True, {"host": self.host, "black_user": self.black_user, "white_user": self.white_user, "observer": self.observer}
        else:
            self.observer -= 1
            self.users_count -= 1
            return False if self.users_count > 0 else True, {"host": self.host, "black_user": self.black_user, "white_user": self.white_user, "observer": self.observer}

    # 用戶移動
    def user_move(self, username, chara_ori, chara_tar):
        accept = False
        if chara_tar == 'black' and self.black_user is None:
            self.black_user = username
            if self.white_user == username: self.white_user = None
            if chara_ori == 'observer': self.observer -= 1
            accept = True
        elif chara_tar == 'white' and self.white_user is None:
            self.white_user = username
            if self.black_user == username: self.black_user = None
            if chara_ori == 'observer': self.observer -= 1
            accept = True
        elif chara_tar == 'observer':
            if self.black_user == username: self.black_user = None
            if self.white_user == username: self.white_user = None
            self.observer += 1
            accept = True
        response = self.get_room_state()
        response["accept"] = accept
        return response

    # 用戶/AI落子(若下一turn為AI，則另起thread)
    def get_move(self, username, userchara, move: list[int]) -> dict:
        # black move
        if self.board.black_turn and userchara == 'black' and username == self.black_user:
            if self.board.do_action_(tuple(move)):
                self.black_turn = not self.black_turn
                board_state = self.board.is_game_over()
                if board_state == 1:
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "black win!"}
                elif board_state == 3:
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "draw"}
                else:
                    if self.white_user == "AI_PLAYER":
                        ai_thread = threading.Thread(target=self.run_ai_model_thread)
                        ai_thread.start()
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "on going"}
            else:
                return {"move_accept": False, "move_message": "Location already moved...", "board_state": 0, "board_message": "on going"}
        # white move
        if (not self.board.black_turn) and userchara == 'white' and username == self.white_user:
            if self.board.do_action_(tuple(move)):
                self.black_turn = not self.black_turn
                board_state = self.board.is_game_over()
                if board_state == 2:
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "white win!"}
                elif board_state == 3:
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "draw"}
                else:
                    if self.black_user == "AI_PLAYER":
                        ai_thread = threading.Thread(target=self.run_ai_model_thread)
                        ai_thread.start()
                    return {"move_accept": True, "move_message": "move sucess!", "board_state": board_state, "board_message": "on going"}
            else:
                return {"move_accept": False, "move_message": "Location already moved...", "board_state": 0, "board_message": "on going"}
        # not your turn
        else:
            return {"move_accept": False, "move_message": "Wait for opponent...", "board_state": 0, "board_message": "on going"}

    # 設置/移除AI player
    def set_ai_player(self, chara='black'):
        if chara == 'black':
            if self.black_user is None:
                self.black_user = "AI_PLAYER"
            elif self.black_user == "AI_PLAYER":
                self.black_user = None
        elif chara == 'white':
            if self.white_user is None:
                self.white_user = "AI_PLAYER"
            elif self.white_user == "AI_PLAYER":
                self.white_user = None
        else:
            print("error occur when set AI_PLAYER")
        # 若輪到AI則另起thread
        if (
            (self.black_turn and self.black_user == "AI_PLAYER") or 
            ((not self.black_turn) and self.white_user == "AI_PLAYER")
        ):            
            ai_thread = threading.Thread(target=self.run_ai_model_thread)
            ai_thread.start()
        return self.get_room_state()

    def run_ai_model_thread(self):
        with self.lock:
            response = self.run_ai_model()

    def run_ai_model(self):
        # 優先檢查是否結束
        if self.board.is_game_over() != 0:
            return
        borad = self.board.get_board_state()
        board_np = np.array(borad)
        ai_chara = 'black' if self.board.black_turn else 'white'
        current_color = self.board.BLACK if self.board.black_turn else self.board.WHITE
        last_move = self.board.last_action
        feature = [(tuple_2d_to_numpy_2d(borad), last_move, current_color)]
        log_ps, _ = AI_PLAYER.infer(feature)
        log_ps = log_ps.reshape(board_np.shape)
        log_ps[board_np != 0] = -np.inf
        action = np.argmax(log_ps)
        y, x = floor(action / 15), action % 15
        time.sleep(0.5)
        response = self.get_move("AI_PLAYER", 'black' if current_color == self.board.BLACK else 'white', [x, y])
        if response["move_accept"]:
            self.socketio.emit("someone_move", {"chara": ai_chara, 'move': [int(x), int(y)], "board_state": response["board_state"]}, room=self.hash)
            if response["board_state"] != 0:  # end
                self.socketio.emit("chat", {"username": "system", "message": self.boart_state_message_mp[response["board_state"]]}, room=self.hash)

    def restart(self, username):
        self.board.clear_board()
        if self.black_user == "AI_PLAYER":
            ai_thread = threading.Thread(target=self.run_ai_model_thread)
            ai_thread.start()
    
    def get_room_state(self):
        borad_pattern = self.board.state_planes
        return {"black_user": self.black_user, "white_user": self.white_user, "observer": self.observer, "borad_pattern": borad_pattern}
         