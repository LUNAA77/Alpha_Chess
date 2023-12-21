import random

from utils import get_legal_actions
# import xxx    # Here may be other package you want to import
import os
import time
import pickle
import json


def check_winner(board):
    """
    Check who is the winner.
    Returns:
        - 'red': if the red side wins.
        - 'black': if the black side wins.
        - 'None': if there is no winner yet.
    """
    red_alive = any([7 in row for row in board])
    black_alive = any([-7 in row for row in board])
    if red_alive and not black_alive:
        return 'red'
    elif not red_alive and black_alive:
        return 'black'
    else:
        return 'None'


def load_zobrist_table():
    """
    Load the Zobrist hash table from the JSON file.
    Returns:
        - zobrist_table: a dictionary of the Zobrist hash table.
    """
    with open('zobrist_table.json', 'r') as json_file:
        zobrist_table = json.load(json_file)
    return zobrist_table


def load_opening_book():
    """
    Load the opening_book from the JSON file.
    Returns:
        - opening_book: a dictionary of hashing table.
    """
    with open('hashing_table.json', 'r') as json_file:
        opening_book = json.load(json_file)
    return opening_book


def load_transposition_table():
    """
    Load the transposition table from the pickle file.
    Returns:
        - transposition_table: a dictionary of the transposition table.
    """
    with open('transposition_table.pkl', 'rb') as f:
        transposition_table = pickle.load(f)
    return transposition_table


def get_piece_value(board):
    """
    Get the value of the pieces on the board.
    Args:
        board: the current board configuration.

    Returns:
        value: the value of the pieces on the board.
    """
    value = 0
    for i in range(10):
        for j in range(9):
            if board[i][j] == 7:  # 将/帅
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


class Player:  # please do not change the class name

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
            - move_back: restoring the last move. You need to use it when backtracking along a path during a search,
                 so that both the board and self.history are reverted correctly.
        """
        os.chdir(os.path.dirname(__file__))
        self.side = side        # don't change
        self.history = []       # don't change
        self.name = "Player_7"  # please change to your group name
        self.count = 0  # record the number of steps
        self.zobrist_table = load_zobrist_table()
        self.transposition_table = load_transposition_table()
        self.hashing_table = load_opening_book()
        self.killer_moves_table = {}
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

        optimal_action = self.start_search(board, depth=4, count=self.count)
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
    def start_search(self, board, depth=4, count=0):
        start_time = time.time()
        legal_actions = get_legal_actions(board, self.side, self.history)
        optimal_action = None
        print(f"Player 7's turn, side: {self.side}")

        if count < 4:
            optimal_action = self.opening_book_search(board)

        if count >= 4 or optimal_action is None:
            result = self.minimax(
                board=board, depth=depth, alpha=-100000000, beta=100000000, side=self.side, start_time=start_time)

            if result is not None and len(result) == 3:
                optimal_value, _, optimal_action = result
            else:
                # 处理无效返回值
                optimal_value, optimal_action = 0, None

        self.count += 1

        # check if the optimal action is legal
        if optimal_action not in legal_actions:
            optimal_action = random.choice(legal_actions)
            print("illegal choice!")

        # 存储转置表（仅在训练时使用）
        # with open('player_7/transposition_table.pkl', 'wb') as f:
        #     pickle.dump(self.transposition_table, f)

        end_time = time.time()
        print("search time: ", end_time - start_time, '\n')

        return optimal_action

    def update_killer_moves(self, depth, cut_move):
        # 更新杀手着法表
        if depth not in self.killer_moves_table:
            self.killer_moves_table[depth] = [None, None]

        if cut_move != self.killer_moves_table[depth][0]:
            self.killer_moves_table[depth][1] = self.killer_moves_table[depth][0]
            self.killer_moves_table[depth][0] = cut_move

    def get_killer_moves(self, depth):
        # 获取当前深度的杀手着法列表
        return self.killer_moves_table.get(depth, [])



    def minimax(self, board, depth, alpha, beta, side, start_time):
        # check if we reach the end of the search or the time is running out
        if depth == 0:
            return self.get_value(board), None
        # if time.time() - start_time > 9.5:
        #     return self.get_value(board), None

        # search in transposition table
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

        winner = check_winner(board)
        if winner == 'red':
            self.transposition_table[board_hash] = depth, float('inf'), None
            return float('inf'), alpha, None
        if winner == 'black':
            self.transposition_table[board_hash] = depth, float('-inf'), None
            return float('-inf'), beta, None

        legal_actions = get_legal_actions(board, side, self.history)
        if len(legal_actions) == 0:
            if side == 'red':
                self.transposition_table[board_hash] = depth, float('-inf'), None
                return float('-inf'), alpha, None
            else:
                self.transposition_table[board_hash] = depth, float('inf'), None
                return float('inf'), beta , None

        # 杀手启发式搜索，从杀手启发搜索表中优先搜索，之后再从随机合法操作中进行搜索
        killer_moves = self.get_killer_moves(depth)
        # 根据要求，先搜索recent_killer，再搜索old_killer，最后再从所有合法操作中随机选择一个操作
        recent_killer = None
        old_killer = None
        if len(killer_moves) > 0 and killer_moves[0] in legal_actions:
            recent_killer = killer_moves[0]
        if len(killer_moves) > 1 and killer_moves[1] in legal_actions:
            old_killer = killer_moves[1]

            # 排序 legal_actions，按照现有的方式进行排序（按被吃掉的棋子的绝对值从大到小）
            legal_actions.sort(key=lambda x: abs(board[x[2]][x[3]]), reverse=True)

            # 将 recent_killer 和 old_killer 插入到 legal_actions 的头部
            legal_actions = [recent_killer, old_killer] + legal_actions

            optimal_action = None

            if len(legal_actions) == 0:
                return 0, alpha, None

            if side == 'red':
                max_value = -100000000
                for action in legal_actions:
                    self.move(board, action[0], action[1], action[2], action[3])
                    value, _ = self.minimax(
                        board, depth - 1, alpha, beta, 'black', start_time)
                    self.move_back(board, action[0], action[1], action[2], action[3])
                    if value > max_value:
                        max_value = value
                        optimal_action = action
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        cut_move = action  # Operation causing pruning
                        self.update_killer_moves(depth, cut_move)
                        break
                    self.transposition_table[board_hash] = depth, max_value, optimal_action
                return max_value, alpha, optimal_action
            else:  # side == 'black'
                min_value = 100000000
                for action in legal_actions:
                    self.move(board, action[0], action[1], action[2], action[3])
                    value, _ = self.minimax(
                        board, depth - 1, alpha, beta, 'red', start_time)
                    self.move_back(board, action[0], action[1], action[2], action[3])
                    if value < min_value:
                        min_value = value
                        optimal_action = action
                    beta = min(beta, value)
                    if beta <= alpha:
                        cut_move = action  # Operation causing pruning
                        self.update_killer_moves(depth, cut_move)
                        break
                    self.transposition_table[board_hash] = depth, min_value, optimal_action
                return min_value, beta, optimal_action

    def zobrist_hash(self, board):
        """
        compute the Zobrist hash value of the current board configuration
        Args:
            board: the current board configuration

        Returns:
            hash_value: the Zobrist hash value of the current board configuration
        """
        hash_value = 0
        for i in range(10):
            for j in range(9):
                hash_value ^= self.zobrist_table[f"{i},{j},{board[i][j]}"]
        return hash_value

    def opening_book_search(self, board):
        current_hash = f"{self.zobrist_hash(board)}"
        if current_hash in self.hashing_table:
            action_tuple = self.hashing_table[current_hash]
            print("selective actions in opening book: ", len(action_tuple))
            old_x, old_y, new_x, new_y, _ = random.choice(action_tuple)
            optimal_action = (old_x, old_y, new_x, new_y)
            print("selected action: ", optimal_action)
            return optimal_action
        else:
            print("Opening book miss!")
            return None

    def get_value(self, board):
        alpha = 1
        beta = 8
        value = alpha * get_piece_value(board) + beta * self.get_position_value(board)
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
                    value -= self.pPosition[9 - i][j]
                elif board[i][j] == -4:
                    value -= self.mPosition[9 - i][j]
                elif board[i][j] == -6:
                    value -= self.jPosition[9 - i][j]
                elif board[i][j] == -1:
                    value -= self.zPosition[9 - i][j]
        return value