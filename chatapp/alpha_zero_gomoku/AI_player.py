import os
from math import floor

import numpy as np
import torch

from .neural_network import NeuralNetWork

def tuple_2d_to_numpy_2d(tuple_2d):
    res = [None] * len(tuple_2d)
    for i, tuple_1d in enumerate(tuple_2d):
        res[i] = list(tuple_1d)
    return np.array(res)

class AI():
    """train and predict
    """

    def __init__(self, num_layers=4, num_channels=256, n=15, action_size=225):
        """ init
        """
        self.num_channels = num_channels
        self.n = n

        self.neural_network = NeuralNetWork(num_layers, num_channels, n, action_size)

    def infer(self, feature_batch):
        """predict p and v by raw input
           return numpy
        """
        board_batch, last_action_batch, cur_player_batch = list(zip(*feature_batch))
        states = self._data_convert(board_batch, last_action_batch, cur_player_batch)

        self.neural_network.eval()
        log_ps, vs = self.neural_network(states)

        return np.exp(log_ps.cpu().detach().numpy()), vs.cpu().detach().numpy()

    def _infer(self, state_batch):
        """predict p and v by state
           return numpy object
        """

        self.neural_network.eval()
        log_ps, vs = self.neural_network(state_batch)

        return np.exp(log_ps.cpu().detach().numpy()), vs.cpu().detach().numpy()

    def _data_convert(self, board_batch, last_action_batch, cur_player_batch):
        """convert data format
           return tensor
        """
        n = self.n

        board_batch = torch.Tensor(board_batch).unsqueeze(1)
        state0 = (board_batch > 0).float()
        state1 = (board_batch < 0).float()

        state2 = torch.zeros((len(last_action_batch), 1, n, n)).float()

        for i in range(len(board_batch)):
            if cur_player_batch[i] == -1:
                temp = state0[i].clone()
                state0[i].copy_(state1[i])
                state1[i].copy_(temp)

            last_action = last_action_batch[i]
            if last_action != -1:
                x, y = last_action // self.n, last_action % self.n
                state2[i][0][x][y] = 1

        res =  torch.cat((state0, state1, state2), dim=1)
        # res = torch.cat((state0, state1), dim=1)
        return res  # .cuda() if self.train_use_gpu else res

    def load_model(self, folder="model", filename="best_checkpoint"):
        """load model from file
        """

        filepath = os.path.join(folder, filename)
        state = torch.load(filepath, map_location=torch.device('cpu'))
        self.neural_network.load_state_dict(state['network'])