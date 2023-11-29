import sys
import time
import copy

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal

from game_gui import GameGUI, ShowMessageThread
from utils import get_legal_actions, init_board, change_round

class GameLoop(QThread):  # Thread responsible for chess piece movement of AIs

    step_signal = pyqtSignal(int, int, int, int, tuple) # Signal for chess moving
    game_over_signal = pyqtSignal(str)  # Signal for game over

    def __init__(self, red, black, delta_time = 1):
        
        super(GameLoop, self).__init__()
        self.red = red
        self.black = black
        self.delta_time = delta_time    # Intervals for chess moving

    def run(self):

        board = init_board()  # Show current game state
        step = 0    # Record the number of game rounds, which is used for judging "draw"
        history = []    # Record game state ever before
        round = "red"

        # Start a new game
        while True:
        
            time.sleep(self.delta_time) # Delay

            copy_board = copy.deepcopy(board)
            action_list = get_legal_actions(copy_board, round, history)

            # Game Over
            if len(action_list) == 0:
                if round == "red":
                    text = "Red loses the game. Black wins!"
                elif round == "black":
                    text = "Black loses the game. Red wins!"
                self.game_over_signal.emit(text)
                break

            # Get action
            if round == "red":
                self.red.update_history(copy.deepcopy(history))
                action = self.red.policy(copy_board)
            elif round == "black":
                self.black.update_history(copy.deepcopy(history))
                action = self.black.policy(copy_board)

            # Check action
            if action not in action_list:
                if round == "red":
                    text = "Red moves illegally, Black wins!" 
                    self.game_over_signal.emit(text)
                    break
                
                elif round == "black":
                    text = "Black moves illegally, Red wins!"
                    self.game_over_signal.emit(text)
                    break
            
            # Record game state and change game state
            action_history = (action[0], action[1], action[2], action[3], board[action[2]][action[3]])
            history.append(action_history)

            # Take action
            board[action[2]][action[3]] = board[action[0]][action[1]]
            board[action[0]][action[1]] = 0

            if action_history[4] != 0: # Refresh the record when some piece is eaten
                step = 0
            else:
                step += 1
                if step == 120:    # Draw
                    text = "Both sides have not eaten in sixty rounds, draw!"
                    self.game_over_signal.emit(text)
                    break

            self.step_signal.emit(action[0],action[1],action[2],action[3],board)

            round = change_round(round)

class ReplayLoop(QThread):  # Thread responsible for history chess piece movement

    step_signal = pyqtSignal(int, int, int, int, tuple) # Signal for chess moving
    game_over_signal = pyqtSignal(str)  # Signal for game over

    def __init__(self, history, delta_time = 1):
        
        super(ReplayLoop, self).__init__()
        self.delta_time = delta_time    # Intervals for chess moving
        self.history = history

    def run(self):

        board = init_board()  # Show current game state
        step = 0    # Record the number of game rounds, which is used for judging "draw"
        round = "red"

        # Replay the history game
        while True:

            time.sleep(self.delta_time) # Delay

            # Game Over
            if step == len(self.history):
                text = "Replay History Over!"
                self.game_over_signal.emit(text)
                break

            # Take action
            action = self.history[step]
            board[action[2]][action[3]] = board[action[0]][action[1]]
            board[action[0]][action[1]] = 0

            self.step_signal.emit(action[0], action[1], action[2], action[3], board)
            step += 1

            round = change_round(round)

class BaseGame(GameGUI):   # Inherit GameGUI

    def __init__(self, thread, window_name):

        super().__init__(window_name)

        board = init_board()
        self.GameShow(board) # Draw initial interface
        
        self.game_thread = thread  # Establish threads for game
        self.game_thread.step_signal.connect(self.convey) # Thread binding slot function
        self.game_thread.game_over_signal.connect(self.game_over)
        self.game_thread.start() # Start threads

    def convey(self, old_x, old_y, new_x, new_y, board):    # Slot function for game 

        # Modify the chess piece logo and record the movement information of the chess piece message
        self.set_move_mark(-1, -1, old_x, old_y, new_x, new_y)
        self.GameShow(board) # Refresh interface

    def game_over(self, text):   # Slot function for Game Over

        self.show_message_thread = ShowMessageThread("Game Over", text)
        self.show_message_thread.signal.connect(self.show_MessageBox)
        self.show_message_thread.start()
        self.game_thread.terminate()

class Game(BaseGame):   # Inherit BaseGame

    def __init__(self, red, black, delta_time = 1):
        
        red_name = red.get_name()
        black_name = black.get_name()
        window_name = f"{red_name} VS {black_name}"
        thread = GameLoop(red, black, delta_time)
        super().__init__(thread, window_name)

class Replay(BaseGame):

    def __init__(self, history, delta_time = 1):
        
        window_name = "Replay History"
        thread = ReplayLoop(history, delta_time)
        super().__init__(thread, window_name)

def play_game(red, black, delta_time: float = 1):
    """
    Watch a new game played by red and black in a visual environment.

    Args:
        - red, black: red and black players, both of which are instance objects of the Player class. 
        - delta_time: the minimum delay time (in seconds) between rendering two frames. 
            It would be useful when you players thinks very fast but you wish to watch the moves more clearly.

    Returns: None
    """

    app = QApplication(sys.argv)    # Establish a QApplication object
    window = Game(red, black, delta_time)    # Create window object
    window.show()   # Display main window
    sys.exit(app.exec_())   # Main cycle