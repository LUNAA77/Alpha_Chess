import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtCore

from game_gui import GameGUI, ShowMessageThread
from utils import get_legal_actions, init_board

board = init_board()
history = []

class PVELoop(QThread):  # Thread responsible for chess piece movement of AI

    step_signal = pyqtSignal(int, int, int, int)   # Signal for chess moving
    game_over_signal = pyqtSignal(str)  # Signal for game over

    def __init__(self, player):
        
        super(PVELoop,self).__init__()
        self.player = player

    def run(self):
        
        # Get action of AI
        action_list = get_legal_actions(board, self.player.side, history)

        # You win, AI loses
        if len(action_list) == 0:
            text = "You won the game! Congratulations!"
            self.game_over_signal.emit(text)
        else:
            # Get action
            action = self.player.policy(board)

            # Check action
            if action not in action_list:
                text = "AI moves illegally, you win!"
                self.game_over_signal.emit(text)

            # Take action
            eaten_id = board[action[2]][action[3]]
            board[action[2]][action[3]] = board[action[0]][action[1]]
            board[action[0]][action[1]] = 0

            history.append((action[0], action[1], action[2], action[3], eaten_id))

            self.step_signal.emit(action[0], action[1], action[2], action[3])

class PVE(GameGUI): # Inherit GameGUI

    def __init__(self, side = "red", player = None):  # side is yours, if side is "black", then you take the black side

        name = player.get_name()
        super().__init__(f"Human VS {name}")

        self.chosen = False # Mark the chess piece selected or moved
        self.old_x = None
        self.old_y = None
        self.round = "red"
        self.side = side

        assert player is not None
        assert player.side != side

        if side == "black":
            self.board_reverse = True

        self.GameShow(board) # Draw initial interface

        self.game_thread = PVELoop(player)  # Establish threads for game
        self.game_thread.step_signal.connect(self.convey) # Thread binding slot function
        self.game_thread.game_over_signal.connect(self.game_over)

        # If you take the black side, then AI takes action first
        if side == "black":
            self.game_thread.start()

    def mousePressEvent(self, event):

        if event.buttons () == QtCore.Qt.LeftButton and self.victory == None:    # Press the left button
            x = event.x()   # Get the horizontal axis coordinates of the form
            y = event.y()   # Get the vertical axis coordinates of the form

            # Convert form coordinates to chess board array coordinates
            x, y = (y - self.start_y) // self.chess_y, (x - self.start_x) // self.chess_x
            if self.side == "black":   # Flip view
                x = 9 - x
                y = 8 - y
            draw_flag, move_flag = self.step(x,y) # Pass array coordinates to game
            if draw_flag or move_flag:
                self.GameShow(board) # If any piece move, redraw the chessboard
            if move_flag:
                self.game_thread.start() # Start thread

    def convey(self, old_x, old_y, new_x, new_y):    # Slot function for game
        
        self.round = self.side
        self.set_move_mark(-1, -1, old_x, old_y, new_x, new_y)
        self.GameShow(board)
        
        action_list = get_legal_actions(board, self.side, history)
        if len(action_list) == 0:
            text = "You lost the game! Please make persistent efforts!"
            self.game_over(text)

    def step(self, x, y): # One step for your action

        self.draw_flag = False
        self.move_flag = False

        if self.round == self.side:   # When you are playing chess
            if self.chosen == False:   # When no chess piece have been selected yet
                if 0 <= x <= 9 and 0 <= y <= 8:    # Check if the chessboard array is out of bounds
                    self.piece_id = board[x][y]
                    if (self.piece_id > 0 and self.side == "red") or (self.piece_id < 0 and self.side == "black"):
                        self.old_x = x
                        self.old_y = y
                        self.set_move_mark(x,y)
                        self.chosen = True  # Change the mark for selected piece

            elif self.chosen == True:   # When there is already selected piece
                self.chosen = False # Change the selected state of the chess piece to unselected state if click elsewhere
                self.set_move_mark(-1,-1)
                if 0 <= x <= 9 and 0 <= y <= 8:    # Check if the chessboard array is out of bounds
                    action_list = get_legal_actions(board, self.side, history)
                    if (self.old_x, self.old_y, x, y) in action_list: # When complying with the chess piece movement rules
                        self.set_move_mark(-1, -1, self.old_x, self.old_y, x, y)
                        history.append((self.old_x, self.old_y, x, y, board[x][y]))
                        board[x][y] = board[self.old_x][self.old_y]
                        board[self.old_x][self.old_y] = 0
                        self.round = "black" if self.side == "red" else "red"
                        self.move_flag = True

        return self.draw_flag, self.move_flag
    
    def game_over(self, text):   # Slot function for Game Over

        self.victory = True
        self.show_message_thread = ShowMessageThread("Game Over", text)
        self.show_message_thread.signal.connect(self.show_MessageBox)
        self.show_message_thread.start()
        self.game_thread.terminate()
  
def play_pve_game(side: str = "red", player = None):
    """
    Used for playing a game against AI.

    Args:
        - side: the side ("red" or "black") you want to take.
        - player: an instance of your Player class.

    Returns: None
    """

    app = QApplication(sys.argv)    # Establish a QApplication object
    window = PVE(side, player)    # Create window object
    window.show()   # Display main window
    sys.exit(app.exec_())   # Main cycle