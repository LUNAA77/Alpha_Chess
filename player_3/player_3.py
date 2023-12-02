import random

from utils import get_legal_actions
# import xxx    # Here may be other package you want to import


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
        action_list = get_legal_actions(board, self.side, self.history)
        optimal_action = random.choice(action_list)
        if self.side == 'red':
            max_value = -100000000
            for action in action_list:
                self.move(board, action[0], action[1], action[2], action[3])
                enemy_actions = get_legal_actions(board, 'black', self.history)
                min_enemy_value = 100000000
                for enemy_action in enemy_actions:
                    self.move(
                        board, enemy_action[0], enemy_action[1], enemy_action[2], enemy_action[3])
                    value = self.get_value(board)
                    if value < min_enemy_value:
                        min_enemy_value = value
                    self.move_back(
                        board, enemy_action[0], enemy_action[1], enemy_action[2], enemy_action[3])
                if min_enemy_value > max_value:
                    max_value = min_enemy_value
                    optimal_action = action
                self.move_back(board, action[0],
                               action[1], action[2], action[3])
        else:
            min_value = 100000000
            for action in action_list:
                self.move(board, action[0], action[1], action[2], action[3])
                enemy_actions = get_legal_actions(board, 'red', self.history)
                max_enemy_value = -100000000
                for enemy_action in enemy_actions:
                    self.move(
                        board, enemy_action[0], enemy_action[1], enemy_action[2], enemy_action[3])
                    value = self.get_value(board)
                    if value > max_enemy_value:
                        max_enemy_value = value
                    self.move_back(
                        board, enemy_action[0], enemy_action[1], enemy_action[2], enemy_action[3])
                if max_enemy_value < min_value:
                    min_value = max_enemy_value
                    optimal_action = action
                self.move_back(board, action[0],
                               action[1], action[2], action[3])
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
        # 炮的位置价值
        pPosition = [
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
        mPosition = [
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
        jPosition = [
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
        zPosition = [
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
        for i in range(10):
            for j in range(9):
                if board[i][j] == 5:
                    value += pPosition[i][j]
                elif board[i][j] == 4:
                    value += mPosition[i][j]
                elif board[i][j] == 6:
                    value += jPosition[i][j]
                elif board[i][j] == 1:
                    value += zPosition[i][j]
                elif board[i][j] == -5:
                    value -= pPosition[9-i][j]
                elif board[i][j] == -4:
                    value -= mPosition[9-i][j]
                elif board[i][j] == -6:
                    value -= jPosition[9-i][j]
                elif board[i][j] == -1:
                    value -= zPosition[9-i][j]
        return value
