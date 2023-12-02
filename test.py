from headless_game import play_headless_game
from player_1 import player_1
from player_7 import player_7

if __name__ == "__main__":    # for Windows OS
    # play 10 games and calculate the win rate of player_7
    win = 0
    for i in range(25):
        red = player_1.Player("red")
        black = player_7.Player("black")
        winner, text, history = play_headless_game(red, black, timeout=False)
        print(i, '\n', winner, '\n', text, '\n')
        if winner == 'black':
            win += 1
    for i in range(25):
        red = player_7.Player("red")
        black = player_1.Player("black")
        winner, text, history = play_headless_game(red, black, timeout=False)
        print(i, '\n', winner, '\n', text, '\n')
        if winner == 'red':
            win += 1
    print('win rate of player_7:', win/50)
