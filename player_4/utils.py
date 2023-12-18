import copy


def init_board():   # Initialize chessboard
    board = ([-6, -4, -3, -2, -7, -2, -3, -4, -6],
             [0,  0,  0,  0,  0,  0,  0,  0,  0],
             [0, -5,  0,  0,  0,  0,  0, -5,  0],
             [-1,  0, -1,  0, -1,  0, -1,  0, -1],
             [0,  0,  0,  0,  0,  0,  0,  0,  0],
             [0,  0,  0,  0,  0,  0,  0,  0,  0],
             [1,  0,  1,  0,  1,  0,  1,  0,  1],
             [0,  5,  0,  0,  0,  0,  0,  5,  0],
             [0,  0,  0,  0,  0,  0,  0,  0,  0],
             [6,  4,  3,  2,  7,  2,  3,  4,  6],)
    return board


# Generate all feasible actions for side based on the current board and history
def get_legal_actions(board: tuple, side: str, history: list):
    """
    return the list of all legal actions according to the input board.

    Args:
        - board: a 10×9 chessboard matrix (a tuple of ten lists). You can use board[x][y] to retrieve 
            the content at column x and row y of the chessboard.
        - side: is a string ("red" or "black"), indicating which side you are querying.
        - history: records previous action sequences as a list. It is necessary because some illegal 
            actions are caused by history.

    Returns:
        - action_list : a list of actions, with each action being a four-element tuple. An action is 
            encoded as (old_x, old_y, new_x, new_y), which means moving board[old_x][old_y] to (new_x, new_y) 
            if legal and (possibly) eating the original piece at (new_x, new_y).
    """

    action_list = []
    candidate_action_list = []
    red_piece = []
    black_piece = []

    Red_King = None
    Black_King = None

    # Record the current chess piece position for acceleration
    for i in range(10):
        for j in range(9):
            piece_id = board[i][j]

            if piece_id > 0:
                if piece_id == 7:
                    Red_King = (7, i, j)
                else:
                    red_piece.append((piece_id, i, j))

            elif piece_id < 0:
                if piece_id == -7:
                    Black_King = (-7, i, j)
                else:
                    black_piece.append((piece_id, i, j))

    # Positions of King are put in the end
    red_piece.append(Red_King)
    black_piece.append(Black_King)

    if side == "red":
        pieces = red_piece
    elif side == "black":
        pieces = black_piece

    # Generate candidate actions
    for piece in pieces:
        id = piece[0]
        x = piece[1]
        y = piece[2]
        candidate_action_list += get_one_piece_action(board, id, x, y)

    # Check if King is attacked and if there is some piece attacking King for three times
    for action in candidate_action_list:
        if check_King_attacked(board, action, red_piece, black_piece) == False:
            if check_history(board, action, history) == False:
                action_list.append(action)

    return action_list


# Generate action of a certain chess piece
def get_one_piece_action(board, piece_id, old_x, old_y):
    action_list = []

    # Red Pawn and Black Pawn
    if piece_id in (1, -1):
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        for i in range(4):
            new_x = old_x + dx[i]
            new_y = old_y + dy[i]
            if 0 <= new_x <= 9 and 0 <= new_y <= 8 and rule(board, piece_id, old_x, old_y, new_x, new_y):
                action_list.append((old_x, old_y, new_x, new_y))

    # Red Advisor and Black Advisor
    elif piece_id in (2, -2):
        if piece_id == 2:
            x = [9, 9, 8, 7, 7]
            y = [3, 5, 4, 5, 3]
        elif piece_id == -2:
            x = [0, 0, 1, 2, 2]
            y = [3, 5, 4, 3, 5]

        for i in range(5):
            if rule(board, piece_id, old_x, old_y, x[i], y[i]):
                action_list.append((old_x, old_y, x[i], y[i]))

    # Red Elephant and Black Elephant
    elif piece_id in (3, -3):
        if piece_id == 3:
            x = [9, 7, 7, 5, 5, 9, 7]
            y = [2, 4, 0, 2, 6, 6, 8]
        elif piece_id == -3:
            x = [0, 2, 4, 2, 0, 4, 2]
            y = [2, 0, 2, 4, 6, 6, 8]
        for i in range(7):
            if rule(board, piece_id, old_x, old_y, x[i], y[i]):
                action_list.append((old_x, old_y, x[i], y[i]))

    # Red Horse and black Horse
    elif piece_id in (4, -4):
        dx = [-2, -2, 2, 2, -1, 1, -1, 1]
        dy = [-1, 1, -1, 1, 2, 2, -2, -2]
        for i in range(8):
            new_x = old_x + dx[i]
            new_y = old_y + dy[i]
            if 0 <= new_x <= 9 and 0 <= new_y <= 8 and rule(board, piece_id, old_x, old_y, new_x, new_y):
                action_list.append((old_x, old_y, new_x, new_y))

    # Red Cannon, Black Cannon, Red Chariot and Black Chariot
    elif piece_id in (5, -5, 6, -6):
        for new_x in range(10):
            if rule(board, piece_id, old_x, old_y, new_x, old_y):
                action_list.append((old_x, old_y, new_x, old_y))
        for new_y in range(9):
            if rule(board, piece_id, old_x, old_y, old_x, new_y):
                action_list.append((old_x, old_y, old_x, new_y))

    # Red King and Black King
    elif piece_id in (7, -7):
        if piece_id == 7:
            x = [9, 9, 9, 8, 8, 8, 7, 7, 7]
            y = [3, 4, 5, 3, 4, 5, 3, 4, 5]
        elif piece_id == -7:
            x = [0, 0, 0, 1, 1, 1, 2, 2, 2]
            y = [3, 4, 5, 3, 4, 5, 3, 4, 5]
        for i in range(9):
            if (rule(board, piece_id, old_x, old_y, x[i], y[i])):
                action_list.append((old_x, old_y, x[i], y[i]))

    return action_list


def rule(board, piece_id, old_x, old_y, new_x, new_y):  # Check whether the action is legal
    if board[new_x][new_y] * piece_id > 0:
        return False   # Illegal if there is one's own chess in the target position

    # Red Pawn
    if piece_id == 1:
        if old_x == new_x + 1 and old_y == new_y:
            return True    # Legal if Red Pwan moves up
        elif old_x <= 4 and old_x == new_x and abs(old_y - new_y) <= 1:
            return True    # Legal if Red Pwan crossing the river moves left or right
        else:
            return False

    # Black Pawn
    elif piece_id == -1:
        if old_x == new_x - 1 and old_y == new_y:
            return True    # Legal if Black Pwan moves down
        elif old_x >= 5 and old_x == new_x and abs(old_y - new_y) <= 1:
            return True    # Legal if Black Pwan crossing the river moves left or right
        else:
            return False

    # Red Advisor
    elif piece_id == 2:
        if 7 <= new_x <= 9 and 3 <= new_y <= 5:    # Not crossing the boundary
            dx = new_x - old_x
            dy = new_y - old_y
            if (dx, dy) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                return True  # Legal if Advisor moves oblique
        else:
            return False

    # Black Advisor
    elif piece_id == -2:
        if 0 <= new_x <= 2 and 3 <= new_y <= 5:    # Not crossing the boundary
            dx = new_x - old_x
            dy = new_y - old_y
            if ((dx, dy) in ((-1, -1), (-1, 1), (1, -1), (1, 1))):
                return True  # Legal if Advisor moves obliquely
        else:
            return False

    # Red Elephant
    elif piece_id == 3:
        if 5 <= new_x <= 9:    # Not crossing the boundary
            dx = new_x - old_x
            dy = new_y - old_y
            if (dx, dy) == (-2, -2) and board[new_x + 1][new_y + 1] == 0:
                return True    # Moves obliquely to the left and upward without blocking the elephant eye
            elif (dx, dy) == (2, -2) and board[new_x - 1][new_y + 1] == 0:
                return True    # Moves obliquely to the left and downward without blocking the elephant eye
            elif (dx, dy) == (-2, 2) and board[new_x + 1][new_y - 1] == 0:
                return True    # Moves obliquely to the right and upward without blocking the elephant eye
            elif (dx, dy) == (2, 2) and board[new_x - 1][new_y - 1] == 0:
                return True    # Moves obliquely to the right and downwards without blocking the elephant eye
        else:
            return False

    # Black Elephant
    elif piece_id == -3:
        if 0 <= new_x <= 4:    # Not crossing the boundary
            dx = new_x - old_x
            dy = new_y - old_y
            if (dx, dy) == (-2, -2) and board[new_x + 1][new_y + 1] == 0:
                return True    # Moves obliquely to the left and upward without blocking the elephant eye
            elif (dx, dy) == (2, -2) and board[new_x - 1][new_y + 1] == 0:
                return True    # Moves obliquely to the left and downward without blocking the elephant eye
            elif (dx, dy) == (-2, 2) and board[new_x + 1][new_y - 1] == 0:
                return True    # Moves obliquely to the right and upward without blocking the elephant eye
            elif (dx, dy) == (2, 2) and board[new_x - 1][new_y - 1] == 0:
                return True    # Moves obliquely to the right and downwards without blocking the elephant eye
        else:
            return False

    # Red Horse and Black Horse
    elif piece_id in (4, -4):
        dx = new_x - old_x
        dy = new_y - old_y
        #   Judge eight directions and blocking the horse legs
        if (dx, dy) in ((-2, -1), (-2, 1)) and board[old_x - 1][old_y] == 0:
            return True
        elif (dx, dy) in ((2, -1), (2, 1)) and board[old_x + 1][old_y] == 0:
            return True
        elif (dx, dy) in ((-1, 2), (1, 2)) and board[old_x][old_y + 1] == 0:
            return True
        elif (dx, dy) in ((-1, -2), (1, -2)) and board[old_x][old_y - 1] == 0:
            return True
        else:
            return False

    # Red Cannon and Black Cannon
    elif piece_id in (5, -5):
        count = 0   # Calculate the number of blank positions between the target position and the current position

        # The target position is empty and on the same line
        if board[new_x][new_y] == 0 and new_x == old_x:
            for i in range(min(new_y, old_y) + 1, max(new_y, old_y)):
                if board[new_x][i] != 0:
                    count += 1
            if count == 0:
                return True  # Legal if there are no chess pieces in the middle

        # The target position is empty and in the same column
        elif board[new_x][new_y] == 0 and new_y == old_y:
            for i in range(min(new_x, old_x) + 1, max(new_x, old_x)):
                if board[i][new_y] != 0:
                    count += 1
            if count == 0:
                return True

        # The target position is the opponent's piece and is on the same line
        elif board[new_x][new_y] * piece_id < 0 and new_x == old_x:
            for i in range(min(new_y, old_y) + 1, max(new_y, old_y)):
                if board[new_x][i] != 0:
                    count += 1    # Legal if there is only one chess piece in the middle
            if count == 1:
                return True

        # The target position is empty and in the same column
        elif board[new_x][new_y] * piece_id < 0 and new_y == old_y:
            for i in range(min(new_x, old_x) + 1, max(new_x, old_x)):
                if board[i][new_y] != 0:
                    count += 1
            if count == 1:
                return True
        else:
            return False

    # Red Chariot and Black Chariot
    elif piece_id in (6, -6):
        count = 0   # Calculate the number of blank positions between the target position and the current position

        # The target position is empty or exists opposing pieces on the same line
        if board[new_x][new_y] * piece_id <= 0 and new_x == old_x:
            for i in range(min(new_y, old_y) + 1, max(new_y, old_y)):
                if board[new_x][i] != 0:
                    count += 1
            if count == 0:
                return True

        # The target position is empty or exists opposing pieces in the same column
        elif board[new_x][new_y] * piece_id <= 0 and new_y == old_y:
            for i in range(min(new_x, old_x) + 1, max(new_x, old_x)):
                if board[i][new_y] != 0:
                    count += 1
            if count == 0:
                return True
        else:
            return False

    # Red King
    elif piece_id == 7:
        if 7 <= new_x <= 9 and 3 <= new_y <= 5:    # Red King is in the Nine Palaces
            dx = new_x - old_x
            dy = new_y - old_y
            if (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                return True  # Red King moves up, down, left, right
        # in the same column with Black King(judge King facing each other)
        elif board[new_x][new_y] == -7 and new_y == old_y:
            count = 0
            for i in range(min(new_x, old_x) + 1, max(new_x, old_x)):
                if board[i][new_y] != 0:
                    count += 1
            if count == 0:
                return True
        else:
            return False

    # Black King
    elif piece_id == -7:
        if 0 <= new_x <= 2 and 3 <= new_y <= 5:    # Black King is in the Nine Palaces
            dx = new_x - old_x
            dy = new_y - old_y
            if (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                return True  # Black King moves up, down, left, right
        # in the same column with Black King(judge King facing each other)
        elif board[new_x][new_y] == 7 and new_y == old_y:
            count = 0
            for i in range(min(new_x, old_x) + 1, max(new_x, old_x)):
                if board[i][new_y] != 0:
                    count += 1
            if count == 0:
                return True
        else:
            return False

    return False


# Check if King is attacked
def check_King_attacked(board, action, red_piece, black_piece):

    old_x = action[0]
    old_y = action[1]
    new_x = action[2]
    new_y = action[3]
    piece_id = board[old_x][old_y]

    # Simulate moving chess piece
    IsAttacked = False
    eaten_id = board[new_x][new_y]
    board[new_x][new_y] = piece_id
    board[old_x][old_y] = 0

    if piece_id > 0:   # Judge whether Red King will be attacked

        if piece_id == 7:
            Red_King_x = new_x
            Red_King_y = new_y
        else:
            # Red_King is at the end of red_piece
            Red_King_x = red_piece[-1][1]
            Red_King_y = red_piece[-1][2]

        for piece in black_piece:
            if piece == (eaten_id, new_x, new_y):
                continue
            black_piece_id = piece[0]
            black_piece_x = piece[1]
            black_piece_y = piece[2]

            if rule(board, black_piece_id, black_piece_x, black_piece_y, Red_King_x, Red_King_y):
                IsAttacked = True
                break

    elif piece_id < 0:   # Judge whether Black King will be attacked

        if piece_id == -7:
            Black_King_x = new_x
            Black_King_y = new_y
        else:
            # Black_King is at the end of red_piece
            Black_King_x = black_piece[-1][1]
            Black_King_y = black_piece[-1][2]

        for piece in red_piece:
            if piece == (eaten_id, new_x, new_y):
                continue
            red_piece_id = piece[0]
            red_piece_x = piece[1]
            red_piece_y = piece[2]
            if rule(board, red_piece_id, red_piece_x, red_piece_y, Black_King_x, Black_King_y):
                IsAttacked = True
                break

    # Restore the position of moved chess piece
    board[old_x][old_y] = piece_id
    board[new_x][new_y] = eaten_id

    return IsAttacked


# Check if there is some piece attacking King for three times
def check_history(board, action, history):

    if len(history) <= 6:
        return False

    copy_board = copy.deepcopy(board)

    piece_x = action[0]
    piece_y = action[1]
    new_x = action[2]
    new_y = action[3]
    piece_id = copy_board[piece_x][piece_y]

    if piece_id > 0:
        side = "black"
    elif piece_id < 0:
        side = "red"

    # Simulate current action to check if King is attacked in action
    eaten_id = copy_board[new_x][new_y]
    copy_board[new_x][new_y] = piece_id
    copy_board[piece_x][piece_y] = 0

    King_x, King_y = get_King_location(copy_board, side)
    if rule(copy_board, piece_id, new_x, new_y, King_x, King_y):    # King is attacked next step

        # Restore the position of simulate moved chess piece
        copy_board[piece_x][piece_y] = piece_id
        copy_board[new_x][new_y] = eaten_id

        # Back to board state one step ago
        copy_board[history[-1][0]][history[-1][1]
                                   ] = copy_board[history[-1][2]][history[-1][3]]
        copy_board[history[-1][2]][history[-1][3]] = history[-1][4]

        King_x, King_y = get_King_location(copy_board, side)

        # The same piece attacks King for one time
        if copy_board[piece_x][piece_y] == piece_id and rule(copy_board, piece_id, piece_x, piece_y, King_x, King_y):

            # Back to board state three steps ago
            copy_board[history[-2][0]][history[-2][1]
                                       ] = copy_board[history[-2][2]][history[-2][3]]
            copy_board[history[-2][2]][history[-2][3]] = history[-2][4]

            copy_board[history[-3][0]][history[-3][1]
                                       ] = copy_board[history[-3][2]][history[-3][3]]
            copy_board[history[-3][2]][history[-3][3]] = history[-3][4]

            King_x, King_y = get_King_location(copy_board, side)

            # The same piece attacks King for two times
            if (history[-2][2], history[-2][3]) == (piece_x, piece_y) and rule(copy_board, piece_id, history[-2][0], history[-2][1], King_x, King_y):

                # Back to board state five steps ago
                copy_board[history[-4][0]][history[-4][1]
                                           ] = copy_board[history[-4][2]][history[-4][3]]
                copy_board[history[-4][2]][history[-4][3]] = history[-4][4]

                copy_board[history[-5][0]][history[-5][1]
                                           ] = copy_board[history[-5][2]][history[-5][3]]
                copy_board[history[-5][2]][history[-5][3]] = history[-5][4]

                King_x, King_y = get_King_location(copy_board, side)

                # The same piece attacks King for three times
                if (history[-4][2], history[-4][3]) == (history[-2][0], history[-2][1]) and rule(copy_board, piece_id, history[-4][0], history[-4][1], King_x, King_y):
                    return True
    return False


def get_King_location(board, side):  # Get position of King. Used for check_histroy
    if side == "red":
        for i in (7, 8, 9):
            for j in (3, 4, 5):
                if (board[i][j] == 7):
                    return i, j

    elif side == "black":
        for i in (0, 1, 2):
            for j in (3, 4, 5):
                if (board[i][j] == -7):
                    return i, j


def change_round(side):
    if side == "red":
        return "black"
    elif side == "black":
        return "red"
