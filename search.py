"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors: Danielle Zhang & Ishan Sodhi
"""

import sys
import json
from queue import PriorityQueue


"""dictionary of every colour's exiting coordinates"""
exit_dict = {"red":[[3,-3],[3,-2],[3,-1],[3,0]],
"green":[[-3,3],[-2,3],[-1,3],[-0,3]],
"blue":[[-3,0],[-2,-1],[-1,-2],[0,-3]]}

"""coordinate marker for pieces that have been removed from the board"""
removed = [-5,-5]

class Operation(object):
    def __init__(self, pos1, pos2, action):
        self.previous_position = pos1
        self.new_position = pos2
        self.action = action


def ring_generator(position, ring_no = 1):

    coordinates = []
    x_coordinates = []
    y_coordinates = []

    #Code to generate the X coordinates
    for i in range(position[0] - ring_no, position[0] + ring_no + 1):
        x_coordinates.append(i)
    for j in range(1, ring_no):
        x_coordinates.append(i)
    for k in range(i, position[0] - ring_no - 1, -1):
        x_coordinates.append(k)
    for j in range(1, ring_no):
        x_coordinates.append(k)

    #Code to generate the Y coordinates
    for i in range(position[1], position[1] - ring_no - 1, -1):
        y_coordinates.append(i)
    for j in range(1, ring_no):
        y_coordinates.append(i)
    for k in range(i, position[1] + ring_no + 1):
        y_coordinates.append(k)
    for j in range(1, ring_no):
        y_coordinates.append(k)
    for l in range(k, position[1], -1):
        y_coordinates.append(l)

    #To combine X and Y
    for i in range(0, len(x_coordinates)):
        coordinates.append([x_coordinates[i], y_coordinates[i]])

    return coordinates

#return a list of positions that are neighbours to the given position
def neighbours(player):

    possible_moves = []
    forbidden_Coords = ring_generator([0, 0], 4)
    moves = ring_generator(player)

    for i in moves:
        if not (i in forbidden_Coords):
            possible_moves.append(i)

    return possible_moves


#Function that return a list of possible operations
def possible_action(piece_index, pieces, blocks, colour):
    current_piece = pieces[piece_index]
    all_neighbours = neighbours(current_piece)
    is_occupied = [False]*len(all_neighbours)
    actions = []
    #check if there is any neighbour that is occupied by other pieces
    for i in range(len(pieces)):
        if i != piece_index:
            for j in range(len(all_neighbours)):
                if all_neighbours[j] == pieces[i]:
                    is_occupied[j] = True
    for block in blocks:
        for j in range(len(all_neighbours)):
            if all_neighbours[j] == block:
                is_occupied[j] = True

    #check if the current piece is able to exit the board
    exit_list = exit_dict[colour]
    for pos in exit_list:
        if pos == current_piece:
            actions.append(Operation(current_piece,removed,"EXIT"))


    #go through the list of neighbours to find possible moves
    for i in range(len(all_neighbours)):
        neighbour = all_neighbours[i]
        #neighbour is occupied. Check if a jump action is valid
        if is_occupied[i]:
            q_difference = neighbour[0]-current_piece[0]
            r_difference = neighbour[1]-current_piece[1]
            jump_pos = [neighbour[0]+q_difference, neighbour[1]+r_difference]
            #check if the new position after a jump action is on the board
            out_of_board = False
            invalid_position = ring_generator([0,0],4)
            for position in invalid_position:
                if position == jump_pos:
                    out_of_board = True
                    break
            # new position is on the board
            if not out_of_board:
                #check if there is other piece or block on this new_position
                occupied = False
                for i in range(len(pieces)):
                    if pieces[i] == jump_pos:
                        occupied = True
                        break
                if not occupied:
                    for block in blocks:
                        if block == jump_pos:
                            occupied = True
                            break
                #position is not occupied. Jump action is valid
                if not occupied:
                    actions.append(Operation(current_piece,jump_pos,"JUMP"))
        #neighbour not occupied. A move action is valid
        else:
            actions.append(Operation(current_piece, neighbour,"MOVE"))

    return actions

def heuristic_distance(current_position, colour):
    """function to calculate the minimum hexagonal distance between given position
    and exit positions"""
    exit_positions = exit_dict[colour]
    dist_list = []
    for position in exit_positions:
        dist = max(abs(current_position[0]-position[0]),
        abs(current_position[0]+current_position[0]-position[0]-position[1]),
        abs(current_position[1]-position[1]))
        dist_list.append(dist)

    return min(dist_list)

"""function to return all the posssible states and the corresponding operation obejcts"""
def next_states(pieces, blocks, colour):
    output = []
    for i in range(len(pieces)):
        if pieces[i] != removed:
            actions = possible_action(i, pieces, blocks, colour)
            for operation in actions:
                new_state = pieces[:]
                new_state[i] = operation.new_position
                output.append((new_state,operation))

    return output


def total_heuristic(pieces, colour):
    """function that sum the heuristic distance of every piece"""
    sum = 0
    for piece in pieces:
        if piece != removed:
            sum += heuristic_distance(piece,colour)
    return sum


def goal_check(pieces):
    for piece in pieces:
        if piece != "REMOVED":
            return False
    return True

#Positions would be the starting positions of all the players.
def A_Star(positions,blocks, colour):

    frontier = PriorityQueue()
    frontier.put(positions, 0)
    came_from = {}

    cost_so_far = {}
    came_from[str(positions)] = None
    cost_so_far[str(positions)] = 0

    while not frontier.empty():
        current = frontier.get()
        print(current)

        #Goal check is going to return if all the pieces have exited the board
        if goal_check(current):
            break

        for state in next_states(current, blocks, colour):
            new_position = state[0]
            key = str(new_position)
            new_cost = cost_so_far[str(current)] + 1

            if key not in cost_so_far or new_cost < cost_so_far[key]:
                cost_so_far[key] = new_cost
                priority = total_heuristic(new_position,colour)
                frontier.put(new_position,priority)
                came_from[key] = (current, state[1])

    return came_from




def main():
    """with open(sys.argv[1]) as file:
        data = json.load(file)"""
    solution = A_Star([[0,0],[3,-3],[-2,1]],[[-1,-2],[-1,1],[1,1],[3,-1]],"red")



    # TODO: Search for and output winning sequence of moves
    # ...


def print_board(board_dict, message="", debug=False, **kwargs):
    """
    Helper function to print a drawing of a hexagonal board's contents.

    Arguments:

    * `board_dict` -- dictionary with tuples for keys and anything printable
    for values. The tuple keys are interpreted as hexagonal coordinates (using
    the axial coordinate system outlined in the project specification) and the
    values are formatted as strings and placed in the drawing at the corres-
    ponding location (only the first 5 characters of each string are used, to
    keep the drawings small). Coordinates with missing values are left blank.

    Keyword arguments:

    * `message` -- an optional message to include on the first line of the
    drawing (above the board) -- default `""` (resulting in a blank message).
    * `debug` -- for a larger board drawing that includes the coordinates
    inside each hex, set this to `True` -- default `False`.
    * Or, any other keyword arguments! They will be forwarded to `print()`.
    """

    # Set up the board template:
    if not debug:
        # Use the normal board template (smaller, not showing coordinates)
        template = """# {0}
#           .-'-._.-'-._.-'-._.-'-.
#          |{16:}|{23:}|{29:}|{34:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-.
#       |{10:}|{17:}|{24:}|{30:}|{35:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{05:}|{11:}|{18:}|{25:}|{31:}|{36:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{01:}|{06:}|{12:}|{19:}|{26:}|{32:}|{37:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{02:}|{07:}|{13:}|{20:}|{27:}|{33:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{03:}|{08:}|{14:}|{21:}|{28:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{04:}|{09:}|{15:}|{22:}|
#          '-._.-'-._.-'-._.-'-._.-'"""
    else:
        # Use the debug board template (larger, showing coordinates)
        template = """# {0}
#              ,-' `-._,-' `-._,-' `-._,-' `-.
#             | {16:} | {23:} | {29:} | {34:} |
#             |  0,-3 |  1,-3 |  2,-3 |  3,-3 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {10:} | {17:} | {24:} | {30:} | {35:} |
#         | -1,-2 |  0,-2 |  1,-2 |  2,-2 |  3,-2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {05:} | {11:} | {18:} | {25:} | {31:} | {36:} |
#     | -2,-1 | -1,-1 |  0,-1 |  1,-1 |  2,-1 |  3,-1 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {01:} | {06:} | {12:} | {19:} | {26:} | {32:} | {37:} |
# | -3, 0 | -2, 0 | -1, 0 |  0, 0 |  1, 0 |  2, 0 |  3, 0 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {02:} | {07:} | {13:} | {20:} | {27:} | {33:} |
#     | -3, 1 | -2, 1 | -1, 1 |  0, 1 |  1, 1 |  2, 1 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {03:} | {08:} | {14:} | {21:} | {28:} |
#         | -3, 2 | -2, 2 | -1, 2 |  0, 2 |  1, 2 | key:
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' ,-' `-.
#             | {04:} | {09:} | {15:} | {22:} |   | input |
#             | -3, 3 | -2, 3 | -1, 3 |  0, 3 |   |  q, r |
#              `-._,-' `-._,-' `-._,-' `-._,-'     `-._,-'"""

    # prepare the provided board contents as strings, formatted to size.
    ran = range(-3, +3+1)
    cells = []
    for qr in [(q,r) for q in ran for r in ran if -q-r in ran]:
        if qr in board_dict:
            cell = str(board_dict[qr]).center(5)
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)

    # fill in the template to create the board drawing, then print!
    board = template.format(message, *cells)
    print(board, **kwargs)


# when this module is executed, run the `main` function:
if __name__ == '__main__':
    main()
