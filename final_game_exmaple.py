import random

from headless_game import play_headless_game
from player_1 import player_1
from player_2 import player_2
from player_3 import player_3
# from player_4 import player_4
# from player_5 import player_5
# from player_6 import player_6
from player_7 import player_7
# from player_8 import player_8
# from player_9 import player_9
# from player_10 import player_10

Players = (player_1.Player,
           player_2.Player,
           player_3.Player,
           4,
           5,
           6,
           player_7.Player,
           8,
           9,
           10)


def run_one_game(agent_i, agent_j, player_i, player_j, game):

    win_i = 0
    win_j = 0
    i = player_i
    j = player_j
    k = game
    if agent_i.side == "red":
        red, black = agent_i, agent_j
    elif agent_i.side == "black":
        red, black = agent_j, agent_i

    try:
        winner, text, history = play_headless_game(red, black, True)

        if winner == agent_i.side:
            win_i += 1
            print(f"Game {k}: Player {i} wins by taking {agent_i.side}: ", text)

        elif winner == agent_j.side:
            win_j += 1
            print(f"Game {k}: Player {j} wins by taking {agent_j.side}: ", text)

        elif winner == "draw":

            if k == 7:  # playoff
                if agent_i.side == "black":
                    win_i += 1
                elif agent_j.side == "black":
                    win_j += 1
            else:
                print(f"Game {k}: Draw: ", text)

    except Exception as e:
        print(
            f"Exception occurred during Player {i} VS Player {j} in Game {k} : {e}")

    return win_i, win_j


def fight(player_i: int, player_j: int):
    """
    Play final (six or seven) games between two groups

    Args:
        - player_i, player_j: id (1~10) of two groups.

    Returns: None
    """

    i = player_i
    j = player_j
    win_i = 0
    win_j = 0
    print(f"Playing game: Player {i} VS Player {j}")

    # Six games
    for game in (1, 2, 3, 4, 5, 6):

        # Player i takes the red and Player j takes the black for three times
        if game in (1, 2, 3):
            agent_i = Players[i - 1]("red")
            agent_j = Players[j - 1]("black")
        # Player i takes the black and Player j takes the red for three times
        elif game in (4, 5, 6):
            agent_i = Players[i - 1]("black")
            agent_j = Players[j - 1]("red")

        result_win_i, result_win_j = run_one_game(
            agent_i, agent_j, player_i, player_j, game)
        win_i += result_win_i
        win_j += result_win_j

    # Draw for playoff
    if win_i == win_j:
        p = random.random()
        if 0 <= p <= 0.5:
            agent_i = Players[i - 1]("red")
            agent_j = Players[j - 1]("black")

        elif 0.5 < p <= 1:
            agent_i = Players[i - 1]("black")
            agent_j = Players[j - 1]("red")

        result_win_i, result_win_j = run_one_game(
            agent_i, agent_j, player_i, player_j, 7)
        win_i += result_win_i
        win_j += result_win_j

    print(f"Player {i} : Player {j} is {win_i} : {win_j}")

    if win_i > win_j:
        print(f"Finally Player {i} wins and Player {j} loses!")
    elif win_i < win_j:
        print(f"Finally Player {j} wins and Player {i} loses!")


if __name__ == "__main__":
    fight(1, 7)  # Play games between group 1 and group 2
