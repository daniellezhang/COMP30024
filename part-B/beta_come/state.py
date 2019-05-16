#a class to represent the state of the game from the perspective of the given player
class State(object):
    def __init__(self, colour, board, exited_piece_count, action, previous_state):
        self.colour = colour
        self.board = board
        self.action = action
        self.exited_piece_count = exited_piece_count

    def print_state(self):
        print(self.colour)
        print(self.action)
        board_dict = {}
        for colour in 'rgb':
            for piece in self.board[colour]:
                board_dict[piece] = colour
        print_board(board_dict)
