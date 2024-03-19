import random
import string

import numpy as np

def generate_room_hash(length=8):
    # 產生包含字母和數字的隨機字串
    characters = string.ascii_letters + string.digits
    room_name = ''.join(random.choice(characters) for _ in range(length))
    return room_name

def user_verify(users, req_sid, roomhash, userchara, username):
    return not (username not in users or 
            users[username]['sid'] != req_sid or 
            users[username]['roomhash'] != roomhash or 
            users[username]['chara'] != userchara)

def tuple_2d_to_numpy_2d(tuple_2d):
    res = [None] * len(tuple_2d)
    for i, tuple_1d in enumerate(tuple_2d):
        res[i] = list(tuple_1d)
    return np.array(res)