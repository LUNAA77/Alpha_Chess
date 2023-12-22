from headless_game import play_headless_game
from player_1 import player_1
from player_2 import player_2
from player_3 import player_3
from player_4 import player_4
from player_5 import player_5
from player_6 import player_6
from player_7 import player_7

# player_1: random player
# player_2: greedy player(min-max depth=1)
# player_3: min-max depth=2
# player_4: min-max depth=3

if __name__ == "__main__":    # for Windows OS
    # play 10 games and calculate the win rate of player_7
    win = 0
    n = 3
    for i in range(n):
        red = player_7.Player("red")
        black = player_4.Player("black")
        # winner, text, history = play_headless_game(red, black, timeout=False)
        winner, text, history = play_headless_game(red, black, timeout=True)
        print('match: ', i, ' winner: ', winner, '\n', text, '\n')
        if winner == 'red':
            win += 1
    for i in range(n):
        red = player_4.Player("red")
        black = player_7.Player("black")
        # winner, text, history = play_headless_game(red, black, timeout=False)
        winner, text, history = play_headless_game(red, black, timeout=True)
        print('match: ', i, ' winner: ', winner, '\n', text, '\n')
        if winner == 'black':
            win += 1
    print('win rate of our player:', win/(2*n))
