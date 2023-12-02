from headless_game import play_headless_game
from player_2 import player_2
from player_7 import player_7

if __name__ == "__main__":    # for Windows OS
    # play 10 games and calculate the win rate of player_7
    win = 0
    for i in range(10):
        red = player_2.Player("red")
        black = player_7.Player("black")
        winner, text, history = play_headless_game(red, black, timeout=True)
        print(i, '\n', winner, '\n', text, '\n')
        if winner == 'black':
            win += 1
    for i in range(10):
        red = player_7.Player("red")
        black = player_2.Player("black")
        winner, text, history = play_headless_game(red, black, timeout=True)
        print(i, '\n', winner, '\n', text, '\n')
        if winner == 'red':
            win += 1
    print('win rate of player_7:', win/20)
