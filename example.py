# example 1
from game import play_game
from player_3 import player_3
from player_5 import player_5

red = player_3.Player("red")
black = player_5.Player("black")
# start a new game and watch it comfortably
play_game(red, black, delta_time=0.1)

# # example 2
# from headless_game import play_headless_game
# from player_1 import player_1
# from player_2 import player_2

# if __name__ == "__main__":    # for Windows OS
#     red = player_1.Player("red")
#     black = player_2.Player("black")
#     # you can start a game for testing or collect game data by this function.
#     winner, text, history = play_headless_game(red, black, timeout=False)
#     # print the result in the console
#     print(winner, '\n', text, '\n', history)

# # example 3
# from replay import replay_history_game
# from headless_game import play_headless_game
# from player_1 import player_1
# from player_2 import player_2

# red = player_1.Player("red")
# black = player_2.Player("black")
# winner, text, history = play_headless_game(
#     red, black, timeout=False)    # get history of a game
# replay_history_game(history, delta_time=1)    # replay history

# # example 4
# from replay import replay_final_game
# # replay the fourth game between group 2 and group 3 with delay time 0.1s
# # this will automatically load the record of Game 4 in the "Player 2 VS Player 3" folder
# replay_final_game(player_1=2, player_2=3, game=4, delta_time=0.1)
# # replay_final_game(player_1 = 3, player_2 = 2, game = 4, delta_tiem = 0.1) is equivilent.

# # example 5
# from player_7 import player_7
# from pve_game import play_pve_game
# player = player_7.Player("red")    # AI takes red side
# play_pve_game("black", player)    # you take black side
