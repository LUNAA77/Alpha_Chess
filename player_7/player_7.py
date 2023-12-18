import random

from utils import get_legal_actions
# import xxx    # Here may be other package you want to import
import os
import time
import pickle


class Player():  # please do not change the class name

    def __init__(self, side: str):
        """
        Variables:
            - self.side: specifies which side your agent takes. It must be "red" or "black".
            - self.history: records history actions.
            - self.move and self.move_back: when you do "search" or "rollout", you can utilize these two methods 
                to simulate the change of the board as the effect of actions and update self.history accordingly.
            - self.name : for you to set a name for your player. It is "Player" by default.

        Methods:
            - policy: the core method for you to implement. It must return a legal action according to the input 
                board configuration. Return values must be a four-element tuple or list in the form 
                of (old_x, old_y, new_x, new_y), with the x coordinate representing the column number 
                and the y coordinate representing the row number.
            - move: simulating movement, moving a piece from (old_x, old_y) to (new_x, new_y) 
                and eating a piece when overlap happens.
            - move_back: restoring the last move. You need to use it when backtracing along a path during a search,
                 so that both the board and self.history are reverted correctly.
        """

        self.side = side    # don't change
        self.history = []   # don't change
        self.name = "Player_7"    # please change to your group name
        self.zobrist_table = {}
        self.init_zobrist_hash()
        self.transposition_table = {}
        # 炮的位置价值
        self.pPosition = [
            [6, 4, 0, -10, -12, -10, 0, 4, 6],
            [2, 2, 0, -4, -14, -4, 0, 2, 2],
            [2, 2, 0, -10, -8, -10, 0, 2, 2],
            [0, 0, -2, 4, 10, 4, -2, 0, 0],
            [0, 0, 0, 2, 8, 2, 0, 0, 0],
            [-2, 0, 4, 2, 6, 2, 4, 0, -2],
            [0, 0, 0, 2, 4, 2, 0, 0, 0],
            [4, 0, 8, 6, 10, 6, 8, 0, 4],
            [0, 2, 4, 6, 6, 6, 4, 2, 0],
            [0, 0, 2, 6, 6, 6, 2, 0, 0]
        ]
        # 马的位置价值
        self.mPosition = [
            [4, 8, 16, 12, 4, 12, 16, 8, 4],
            [4, 10, 28, 16, 8, 16, 28, 10, 4],
            [12, 14, 16, 20, 18, 20, 16, 14, 12],
            [8, 24, 18, 24, 20, 24, 18, 24, 8],
            [6, 16, 14, 18, 16, 18, 14, 16, 6],
            [4, 12, 16, 14, 12, 14, 16, 12, 4],
            [2, 6, 8, 6, 10, 6, 8, 6, 2],
            [4, 2, 8, 8, 4, 8, 8, 2, 4],
            [0, 2, 4, 4, -2, 4, 4, 2, 0],
            [0, -4, 0, 0, 0, 0, 0, -4, 0]
        ]
        # 车的位置价值
        self.jPosition = [
            [14, 14, 12, 18, 16, 18, 12, 14, 14],
            [16, 20, 18, 24, 26, 24, 18, 20, 16],
            [12, 12, 12, 18, 18, 18, 12, 12, 12],
            [12, 18, 16, 22, 22, 22, 16, 18, 12],
            [12, 14, 12, 18, 18, 18, 12, 14, 12],
            [12, 16, 14, 20, 20, 20, 14, 16, 12],
            [6, 10, 8, 14, 14, 14, 8, 10, 6],
            [4, 8, 6, 14, 12, 14, 6, 8, 4],
            [8, 4, 8, 16, 8, 16, 8, 4, 8],
            [-2, 10, 6, 14, 12, 14, 6, 10, -2]
        ]
        # 卒的位置价值
        self.zPosition = [
            [0, 3, 6, 9, 12, 9, 6, 3, 0],
            [18, 36, 56, 80, 120, 80, 56, 36, 18],
            [14, 26, 42, 60, 80, 60, 42, 26, 14],
            [10, 20, 30, 34, 40, 34, 30, 20, 10],
            [6, 12, 18, 18, 20, 18, 18, 12, 6],
            [2, 0, 8, 0, 8, 0, 8, 0, 2],
            [0, 0, -2, 0, 4, 0, -2, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def policy(self, board: tuple):  # the core method for you to implement
        """
        You should complement this method.

        Args:
            - board is a 10×9 matrix, showing current game state.
                board[i][j] > 0 means a red piece is on position (i,j)
                board[i][j] < 0 means a black piece is on position (i,j)
                board[i][j] = 0 means position (i,j) is empty.

        Returns:
            - Your return value is a four-element tuple (i,j,x,y), 
              which means your next action is to move your piece from (i,j) to (x,y).
            Note that your return value must be illegal. Otherwise you will lose the game directly.
        """

        # get all actions that are legal to choose from
        optimal_action = self.start_search(board, depth=5)
        return optimal_action

    def move(self, board, old_x, old_y, new_x, new_y):  # don't change
        """utility function provided by us: simulate the effect of a movement"""

        eaten_id = board[new_x][new_y]
        board[new_x][new_y] = board[old_x][old_y]
        board[old_x][old_y] = 0
        self.history.append((old_x, old_y, new_x, new_y, eaten_id))

    def move_back(self, board, old_x, old_y, new_x, new_y):  # don't change
        """utility function provided by us: restore or reverse the effect of a movement"""

        board[old_x][old_y] = board[new_x][new_y]
        board[new_x][new_y] = self.history[-1][4]
        self.history.pop()

    def update_history(self, current_game_history: list):
        """to refresh your self.history after each actual play, which is taken care externally"""

        self.history = current_game_history

    def get_name(self):
        """used by the external logger"""

        return self.name

    # ---------------------------------Our Functions---------------------------------
    def start_search(self, board, depth=4):
        start_time = time.time()
        legal_actions = get_legal_actions(board, self.side, self.history)
        print(f"Player 7's turn, side: {self.side}")

        # 加载转置表
        if os.path.exists('player_7/transposition_table.pkl'):
            with open('player_7/transposition_table.pkl', 'rb') as f:
                self.transposition_table = pickle.load(f)

        optimal_value, optimal_action = self.minimax(
            board=board, depth=depth, alpha=-100000000, beta=100000000, side=self.side, start_time=start_time)
        # print("optimal value: ", optimal_value)

        # check if the optimal action is legal
        if optimal_action not in legal_actions:
            optimal_action = random.choice(legal_actions)
            print("illegal choice!")

        # 存储转置表
        with open('player_7/transposition_table.pkl', 'wb') as f:
            pickle.dump(self.transposition_table, f)

        end_time = time.time()
        print("search time: ", end_time-start_time, '\n')

        return optimal_action

    def minimax(self, board, depth, alpha, beta, side, start_time):
        # check if we reach the end of the search or the time is running out
        if depth == 0:
            return self.get_value(board), None
        # if time.time() - start_time > 9.5:
        #     return self.get_value(board), None

        board_hash = self.zobrist_hash(board)
        if board_hash in self.transposition_table:
            saved_depth, saved_value, saved_action = self.transposition_table[board_hash]
            if saved_depth >= depth:
                # print("transposition table hit!")
                return saved_value, saved_action
        #     else:
        #         print("depth increased!")
        # else:
        #     print("transposition table miss!")

        winner = self.check_winner(board)
        if winner == 'red':
            self.transposition_table[board_hash] = depth, float('inf'), None
            return float('inf'), None
        if winner == 'black':
            self.transposition_table[board_hash] = depth, float(
                '-inf'), None
            return float('-inf'), None

        # get all legal actions and check if the game is over
        legal_actions = get_legal_actions(board, side, self.history)
        # 按legal_actions中的每个action的最后一个元素（被吃掉的棋子）的绝对值从大到小排序
        legal_actions.sort(key=lambda x: abs(board[x[2]][x[3]]), reverse=True)
        if len(legal_actions) == 0:
            if side == 'red':
                self.transposition_table[board_hash] = depth, float(
                    '-inf'), None
                return float('-inf'), None
            else:
                self.transposition_table[board_hash] = depth, float(
                    'inf'), None
                return float('inf'), None

        # random initialization
        optimal_action = random.choice(legal_actions)

        # start search
        if side == 'red':
            max_value = -100000000
            for action in legal_actions:
                self.move(board, action[0], action[1], action[2], action[3])
                value, _ = self.minimax(
                    board, depth-1, alpha, beta, 'black', start_time)
                self.move_back(board, action[0],
                               action[1], action[2], action[3])
                if value > max_value:
                    max_value = value
                    optimal_action = action
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
                self.transposition_table[board_hash] = depth, max_value, optimal_action
            return max_value, optimal_action
        else:  # side == 'black'
            min_value = 100000000
            for action in legal_actions:
                self.move(board, action[0], action[1], action[2], action[3])
                value, _ = self.minimax(
                    board, depth-1, alpha, beta, 'red', start_time)
                self.move_back(board, action[0],
                               action[1], action[2], action[3])
                if value < min_value:
                    min_value = value
                    optimal_action = action
                beta = min(beta, value)
                if beta <= alpha:
                    break
                self.transposition_table[board_hash] = depth, min_value, optimal_action
            return min_value, optimal_action

    def check_winner(self, board):
        """
        Check who is the winner.
        Return 'red' if red wins, 'black' if black wins, otherwise return 'None'.
        """
        red_alive = any([7 in row for row in board])
        black_alive = any([-7 in row for row in board])
        if red_alive and not black_alive:
            return 'red'
        elif not red_alive and black_alive:
            return 'black'
        else:
            return 'None'

    def zobrist_hash(self, board):
        """
        根据棋盘和 Zobrist 哈希表计算哈希值。
        :param board: 棋盘状态。
        :return: 哈希值。
        """
        hash_value = 0
        for i in range(10):
            for j in range(9):
                if board[i][j] != 0:
                    hash_value ^= self.zobrist_table[(i, j, board[i][j])]
        return hash_value

    def init_zobrist_hash(self):
        """
        初始化 Zobrist 哈希表。
        :param board_size: 棋盘尺寸，例如 (10, 9)。
        :return: Zobrist 哈希表。
        """
        pieces = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
        for i in range(10):
            for j in range(9):
                for piece in pieces:
                    self.zobrist_table[(i, j, piece)] = random.getrandbits(64)
        return self.zobrist_table

    def get_value(self, board):
        alpha = 1
        beta = 8
        value = alpha * self.get_piece_value(board) + \
            beta * self.get_position_value(board)
        return value

    def get_piece_value(self, board):
        value = 0
        for i in range(10):
            for j in range(9):
                if board[i][j] == 7:    # 将/帅
                    value += 1000000
                elif board[i][j] == 6:  # 车
                    value += 600
                elif board[i][j] == 5:  # 炮
                    value += 300
                elif board[i][j] == 4:  # 马
                    value += 300
                elif board[i][j] == 3:  # 象
                    value += 110
                elif board[i][j] == 2:  # 士
                    value += 110
                elif board[i][j] == 1:  # 兵/卒
                    value += 70
                elif board[i][j] == -7:  # 将/帅
                    value -= 1000000
                elif board[i][j] == -6:  # 车
                    value -= 600
                elif board[i][j] == -5:  # 炮
                    value -= 300
                elif board[i][j] == -4:  # 马
                    value -= 300
                elif board[i][j] == -3:  # 象
                    value -= 110
                elif board[i][j] == -2:  # 士
                    value -= 110
                elif board[i][j] == -1:  # 兵/卒
                    value -= 70
        return value

    def get_position_value(self, board):
        value = 0
        for i in range(10):
            for j in range(9):
                if board[i][j] == 5:
                    value += self.pPosition[i][j]
                elif board[i][j] == 4:
                    value += self.mPosition[i][j]
                elif board[i][j] == 6:
                    value += self.jPosition[i][j]
                elif board[i][j] == 1:
                    value += self.zPosition[i][j]
                elif board[i][j] == -5:
                    value -= self.pPosition[9-i][j]
                elif board[i][j] == -4:
                    value -= self.mPosition[9-i][j]
                elif board[i][j] == -6:
                    value -= self.jPosition[9-i][j]
                elif board[i][j] == -1:
                    value -= self.zPosition[9-i][j]
        return value
