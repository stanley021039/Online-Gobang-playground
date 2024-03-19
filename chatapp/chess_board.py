# coding: utf-8
from typing import Tuple
from copy import deepcopy
from collections import OrderedDict

import torch
import numpy as np


class ChessBoard:
    """ 棋盘类 """

    EMPTY = 0
    BLACK = 1
    WHITE = -1

    def __init__(self, board_len=15, n_feature_planes=6):
        """
        Parameters
        ----------
        board_len: int
            棋盘边长

        n_feature_planes: int
            特征平面的个数，必须为偶数
        """
        self.board_len = board_len
        self.black_turn = True
        # self.current_player = self.BLACK
        self.n_feature_planes = n_feature_planes
        self.available_actions = list(range(self.board_len**2))
        # 棋盘状态字典，key 为 action，value 为 current_player
        self.state = OrderedDict()
        self.last_action = -1
        self.state_planes = [[0 for _ in range(self.board_len)] for _ in range(self.board_len)]  # 棋盤落子情況
        # 上一个落点
        self.previous_action = None

    def copy(self):
        """ 复制棋盘 """
        return deepcopy(self)

    def clear_board(self):
        """ 清空棋盘 """
        self.state.clear()
        self.previous_action = None
        # self.current_player = self.BLACK
        self.black_turn = True
        self.available_actions = list(range(self.board_len**2))
        self.last_action = -1
        self.state_planes = [[0 for _ in range(self.board_len)] for _ in range(self.board_len)]

    def do_action(self, pos: tuple):
        """ 落子并更新棋盘

        Parameters
        ----------
        pos: tuple
            落子位置
        """
        x, y = pos
        action = y*self.board_len + x

        self.last_action = action
        self.state_planes[y][x] = self.BLACK if self.black_turn else self.WHITE
        self.previous_action = action
        self.available_actions.remove(action)
        # self.state[action] = self.current_player
        # self.current_player = self.WHITE + self.BLACK - self.current_player
        self.state[action] = self.BLACK if self.black_turn else self.WHITE
        self.black_turn = not self.black_turn

    def do_action_(self, pos: tuple) -> bool:
        """ 落子并更新棋盘

        Parameters
        ----------
        pos: Tuple[int, int]
            落子在棋盘上的位置，范围为 `(0, 0) ~ (board_len-1, board_len-1)`

        Returns
        -------
        update_ok: bool
            是否成功落子
        """
        x, y = pos
        action = y*self.board_len + x

        if action in self.available_actions:
            self.do_action(pos)
            return True
        return False

    def is_game_over(self) -> int:
        """ 判断游戏是否结束

        Returns
        -------
        黑白其定義與遊戲桌外不同!!!!!!黑白其定義與遊戲桌外不同!!!!!!!!
        end type: int
            0: 遊戲進行中
            1: 黑棋獲勝
            2: 白棋獲勝
            3: 平手
        -------
        """
        # 如果下的棋子不到 9 个，就直接判断游戏还没结束
        if len(self.state) < 9:
            return 0

        n = self.board_len
        act = self.previous_action
        player = self.state[act]
        row, col = act//n, act % n

        # 搜索方向
        directions = [[(0, -1),  (0, 1)],   # 水平搜索
                      [(-1, 0),  (1, 0)],   # 竖直搜索
                      [(-1, -1), (1, 1)],   # 主对角线搜索
                      [(1, -1),  (-1, 1)]]  # 副对角线搜索

        for i in range(4):
            count = 1
            for j in range(2):
                flag = True
                row_t, col_t = row, col
                while flag:
                    row_t = row_t + directions[i][j][0]
                    col_t = col_t + directions[i][j][1]
                    if 0 <= row_t < n and 0 <= col_t < n and self.state.get(row_t*n+col_t, 0) == player:
                        # 遇到相同颜色时 count+1
                        count += 1
                    else:
                        flag = False
            # 分出胜负
            if count >= 5:
                return 1 if player == self.BLACK else 2

        # 平局
        if not self.available_actions:
            return 3

        return 0

    def get_board_state(self) -> list:
        return self.state_planes

    # def get_feature_planes(self) -> torch.Tensor:
    #     """ 棋盘状态特征张量，维度为 `(n_feature_planes, board_len, board_len)`

    #     Returns
    #     -------
    #     feature_planes: Tensor of shape `(n_feature_planes, board_len, board_len)`
    #         特征平面图像
    #     """
    #     n = self.board_len
    #     feature_planes = torch.zeros((self.n_feature_planes, n**2))
    #     # 最后一张图像代表当前玩家颜色
    #     # feature_planes[-1] = self.current_player
    #     # 添加历史信息
    #     if self.state:
    #         actions = np.array(list(self.state.keys()))[::-1]
    #         players = np.array(list(self.state.values()))[::-1]
    #         Xt = actions[players == (self.BLACK if self.black_turn else self.WHITE)]
    #         Yt = actions[players != (self.BLACK if self.black_turn else self.WHITE)]
    #         for i in range((self.n_feature_planes-1)//2):
    #             if i < len(Xt):
    #                 feature_planes[2*i, Xt[i:]] = 1
    #             if i < len(Yt):
    #                 feature_planes[2*i+1, Yt[i:]] = 1

    #     return feature_planes.view(self.n_feature_planes, n, n)

class ColorError(ValueError):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
