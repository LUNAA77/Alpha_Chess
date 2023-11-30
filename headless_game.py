import copy
import multiprocessing

from utils import get_legal_actions, init_board, change_round


def play_headless_game(red, black, timeout: bool = False):
    """
    Start a game using "red" and "black" agents with timeout.

    Args:
        - red, black: the two players, both are instances of the Player class. 
        - timeout: specifies whether the red or the black player. When timeout is set to true, a player that used out 
            its thinking time (10 seconds) will lose the game immediately. This is the setup we will use during the 
            final match. When timeout is set to false (default), it means there is no limitation on the thinking time, 
            which is useful for collecting learning data. This mode also has lower overhead due to the removal of 
            the timing thread.

    Returns:
        - winner: "red", "black" and "draw".
        - text: explainations of the result.
        - history: record of actions taken by both sides during the game.
    """

    board = init_board()  # Show current game state
    step = 0    # Record the number of game rounds, which is used for judging "draw"
    history = []    # Record game state ever before
    round = "red"
    winner = None   # Final winner
    text = None  # Explain the reason for the end of the match

    # Start the game
    while True:

        copy_board = copy.deepcopy(board)
        action_list = get_legal_actions(copy_board, round, history)

        # Game Over
        if len(action_list) == 0:
            if round == "red":
                text = "Red loses the game. Black wins!"
                winner = "black"
            elif round == "black":
                text = "Black loses the game. Red wins!"
                winner = "red"
            break

        # Get action
        if round == "red":
            red.update_history(copy.deepcopy(history))
            action = get_player_action_with_timeout(
                copy_board, red) if timeout else red.policy(board)
        elif round == "black":
            black.update_history(copy.deepcopy(history))
            action = get_player_action_with_timeout(
                copy_board, black) if timeout else black.policy(board)

        # Check action
        if action not in action_list:
            if round == "red":
                text = "Red timeout, Black wins!" if action == "Timed out" else "Red moves illegally, Black wins!"
                winner = "black"
                break

            elif round == "black":
                text = "Black timeout, Red wins!" if action == "Timed out" else "Black moves illegally, Red wins!"
                winner = "red"
                break

        # Record game state and change game state
        action_history = (action[0], action[1], action[2],
                          action[3], board[action[2]][action[3]])
        history.append(action_history)

        # Take action
        board[action[2]][action[3]] = board[action[0]][action[1]]
        board[action[0]][action[1]] = 0

        if action_history[4] != 0:  # Refresh the record when some piece is eaten
            step = 0
        else:
            step += 1
            if step == 120:    # Draw
                text = "Both sides have not eaten in sixty rounds, draw!"
                winner = "draw"
                break

        round = change_round(round)

    return winner, text, history


# Wrap functions of player using a message queue
def get_player_action(board, player, result_queue):

    action = player.policy(board)
    result_queue.put(action)  # Put the results in the queue


def get_player_action_with_timeout(board, player):

    # Use a queue for parameter transfer between processes
    result_queue = multiprocessing.Queue()

    # Create a new process to run the function and reckon by time
    p = multiprocessing.Process(
        target=get_player_action, args=(board, player, result_queue))
    p.start()
    # Reserve time (here is 0.5 seconds) to start the process
    p.join(timeout=10 + 0.5)

    if p.is_alive():    # If the process is still running, it indicates a timeout

        p.terminate()   # Terminate the process
        p.join()  # Waiting for the process to end
        result = "Timed out"

    else:
        result = result_queue.get()  # Get the return result of the function from the queue

    return result
