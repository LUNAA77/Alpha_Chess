import os
import ast
import sys

from PyQt5.QtWidgets import QApplication

from game import Replay


def read_history(player_1, player_2, game):  # Read histroy from txt files

    # Check parameters
    assert player_1 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert player_2 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert player_1 != player_2
    player_1, player_2 = min(player_1, player_2), max(player_1, player_2)

    # Get path
    current_path = os.path.dirname(os.path.abspath(__file__))
    folder_name = f"Player {player_1} VS Player {player_2}"
    file_name = f"Game {game}.txt"

    directory = os.path.join(current_path, folder_name)
    file_path = os.path.join(directory, file_name)

    with open(file_path, "r") as f:
        history = f.readline()

    # Parse a list in string form into an available list
    history = ast.literal_eval(history)

    return history


def replay_final_game(player_1: int, player_2: int, game: int, delta_time: float = 1):
    """
    Used for replaying the games among 10 groups.

    Args:
        - player_1, player_2: player_id (1~10) of the two groups.
        - game: specifies which game you want to watch (1~6/1~7).
        - delta_time: the time gap between rendering two frames.

    Returns: None
    """

    history = read_history(player_1, player_2, game)
    replay_history_game(history, delta_time)


def replay_history_game(history: list, delta_time: float = 1):
    """
    Replay the history game in a visual environment.

    Args:
        - history: history recorded in a past game, a list of actions.
        - delta_time: the minimum delay time (seconds) between redering two frames.

    Returns: None
    """

    app = QApplication(sys.argv)    # Establish a QApplication object
    window = Replay(history, delta_time)    # Create window object
    window.show()   # Display main window
    sys.exit(app.exec_())   # Main cycle
