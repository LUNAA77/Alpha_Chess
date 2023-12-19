import csv
import json
import random

def init_zobrist_hash():
    """
    Initialize the Zobrist hash table.
    """
    zobrist_table = {}
    pieces = [0, 1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7]
    for i in range(10):
        for j in range(9):
            for piece in pieces:
                # 将元组键转换为字符串形式
                key_str = f"{i},{j},{piece}"
                zobrist_table[key_str] = random.getrandbits(64)

    # 存储 Zobrist 表
    with open('zobrist_table.json', 'w') as json_file:
        json.dump(zobrist_table, json_file)

    return zobrist_table

def zobrist_hash(board):
    """
    Calculate the hash value based on the Zobrist hash table and the chessboard.
    """
    # 加载 Zobrist 表
    with open('zobrist_table.json', 'r') as json_file:
        zobrist_table = json.load(json_file)

    hash_value = 0
    for i in range(10):
        for j in range(9):
            if board[i][j] != 0:
                # 使用 Zobrist 表中的哈希值，键使用字符串形式
                key_str = f"{i},{j},{board[i][j]}"
                hash_value ^= zobrist_table[key_str]
    return hash_value

def convert_board_to_hash(board_str):
    """
    Convert the string representation of the board to the hash value using Zobrist hashing.
    """
    # Parse the string representation of the board into a 2D list
    board = json.loads(board_str)

    # Calculate the Zobrist hash value
    hash_value = zobrist_hash(board)

    return hash_value

def main():
    # Read the new_file1.csv file, using the first and second columns (board and moves columns)
    with open('new_file1.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Skip the header row
        next(reader)

        # Create a new dictionary to store hash values and moves
        hash_and_moves = {}

        for row in reader:
            # Parse the string representation of the board into a 2D list
            board_str = row[0]

            # Skip the row if it contains "tuple" in the second column
            if "tuple" in row[1]:
                continue

            # Calculate the Zobrist hash value
            hash_value = convert_board_to_hash(board_str)

            # Get the moves information from the second column
            moves_info = json.loads(row[1])

            # Store the hash value and moves information in the dictionary
            hash_and_moves[hash_value] = moves_info

        # Write the dictionary of hash values and moves to the JSON file
        with open('hashing_table.json', 'w') as hashfile:
            json.dump(hash_and_moves, hashfile)

if __name__ == "__main__":
    init_zobrist_hash()
    main()
