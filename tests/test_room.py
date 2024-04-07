import unittest
from unittest.mock import MagicMock

# 导入要测试的类
from chatapp.room import Rooms

# 创建测试类
class TestRooms(unittest.TestCase):

    # 在测试开始之前设置
    def setUp(self):
        # 创建一个Rooms实例并传入一个Mock对象
        self.socketio_mock = MagicMock()
        self.rooms = Rooms(self.socketio_mock)

    # 测试创建房间
    def test_create_room(self):
        result = self.rooms.create("user", "test_room", "password")
        self.assertTrue(result['accept'])
        self.assertTrue(result['roomhash'] in self.rooms.all_rooms)

    # 测试加入房间
    def test_user_join_room(self):
        roomhash = self.rooms.create("user", "test_room", "password")['roomhash']
        result, message = self.rooms.user_join(roomhash, "password", "new_user")

        self.assertIsNotNone(result)
        self.assertEqual(message, f"Join room_{roomhash} success")

    # 测试离开房间
    def test_user_leave_room(self):
        roomhash = self.rooms.create("user", "test_room", "password")['roomhash']
        self.rooms.user_join(roomhash, "password", "new_user_1")
        self.rooms.user_join(roomhash, "password", "new_user_2")

        # 用戶離開
        room_info = self.rooms.user_leave(roomhash, "new_user_2")
        self.assertIsNone(self.rooms.all_rooms[roomhash].white_user)

        # 關閉房間
        room_info = self.rooms.user_leave(roomhash, "new_user_1")
        self.assertIsNone(self.rooms.all_rooms.get(roomhash))
        
    # 测试设置AI
    def test_set_ai(self):
        roomhash = self.rooms.create("user", "test_room", "password")['roomhash']
        result = self.rooms.set_ai(roomhash, "black")
        self.assertTrue(result)

    def test_game_over(self):
        roomhash = self.rooms.create("user_black", "test_room", "password")['roomhash']
        room_info, message = self.rooms.user_join(roomhash, "password", "user_black")
        room_info, message = self.rooms.user_join(roomhash, "password", "user_white")
        _ = self.rooms.all_rooms[roomhash].get_move("user_black", "black", [0, 0])
        _ = self.rooms.all_rooms[roomhash].get_move("user_white", "white", [0, 2])
        _ = self.rooms.all_rooms[roomhash].get_move("user_black", "black", [1, 1])
        _ = self.rooms.all_rooms[roomhash].get_move("user_white", "white", [1, 3])
        _ = self.rooms.all_rooms[roomhash].get_move("user_black", "black", [2, 2])
        _ = self.rooms.all_rooms[roomhash].get_move("user_white", "white", [2, 4])
        _ = self.rooms.all_rooms[roomhash].get_move("user_black", "black", [3, 3])
        _ = self.rooms.all_rooms[roomhash].get_move("user_white", "white", [3, 5])
        move_info = self.rooms.all_rooms[roomhash].get_move("user_black", "black", [4, 4])
        self.assertEqual(move_info["board_state"], 1)

    def tearDown(self):
        pass

# 运行测试
if __name__ == '__main__':
    unittest.main()