"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors: Danielle Zhang & Ishan Sodhi
"""

import sys
import json
from queue import PriorityQueue
from queue import Queue


#dictionary of every colour's exiting positions
exit_dict = {"red":[(3,-3),(3,-2),(3,-1),(3,0)],
"green":[(-3,3),(-2,3),(-1,3),(-0,3)],
"blue":[(-3,0),(-2,-1),(-1,-2),(0,-3)]}

#position marker for pieces that have been removed from the board
removed = (-5,-5)

path_dict = {}

#a class to hold information about the change in state after an action
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
        coordinates.append((x_coordinates[i], y_coordinates[i]))

    return coordinates

#return a list of positions that are neighbours to the given position
def neighbours(player):

    neighbours = []
    forbidden_Coords = ring_generator((0, 0), 4)
    moves = ring_generator(player)

    for i in moves:
        if not (i in forbidden_Coords):
            neighbours.append(i)
    return neighbours


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
            jump_pos = (neighbour[0]+q_difference, neighbour[1]+r_difference)
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


"""function to return all the posssible states and the corresponding operation obejcts"""
def next_states(pieces, blocks, colour):
    output = []
    for i in range(len(pieces)):
        if pieces[i] != removed:
            actions = possible_action(i, pieces, blocks, colour)
            for operation in actions:

                new_state = pieces[:]

                new_state = list(new_state)

                new_state[i] = operation.new_position
                new_state = tuple(new_state)

                output.append((new_state,operation))

    return output

#FUnction that calculate the heuristic for the state
def total_heuristic(pieces, blocks, colour):
    sum = 0
    #sum the shortest path length for every piece on the board
    for piece in pieces:
        if piece != removed:
            sum += path_dict[piece]

    return sum*3/4

#Function to check if a piece has been removed
def goal_check(pieces):
    for piece in pieces:
        if piece != removed:
            return False
    return True

#function to find the shortest path to the exits for every position on the board
def shortest_path(blocks, pieces, colour):
    #every node in the queue is consisted of the current position and the
    #previous position
    frontier = Queue()

    #start the algorithm from the exit positions' neighbours
    for coordinate in exit_dict[colour]:
        #only consider the exit positions that aren't blocked
        if(coordinate not in blocks):
            path_dict[coordinate] = 1
            next_coordinates = neighbours(coordinate)
            for next in next_coordinates:
                frontier.put((next,coordinate))

    while not frontier.empty():
        current = frontier.get()
        new_path = path_dict[current[1]] + 1
        #the current position doesn't have a block on it
        if current[0] not in blocks :
            #current position hasn't been visited yet. Assign path length
            if path_dict.get(current[0],-1) == -1:
                path_dict[current[0]] = new_path

            #current position has been visited. New path length is shorter.
            #Assign path length
            elif new_path < path_dict[current[0]]:
                path_dict[current[0]] = new_path
            next_coordinates = neighbours(current[0])

            for next in next_coordinates:
                #add current position's neighbour that has not yet been
                #visited to the queue
                if path_dict.get(next, -1) == -1:
                    frontier.put((next,current[0]))
                #Assign path length to the current position's neighbour
                #if the new path length is shorter
                elif path_dict[next] > new_path + 1:

                    path_dict[next] = new_path + 1

        #the current position has a block on it
        else:
            next_coordinates = neighbours(current[0])
            q_difference = current[0][0] - current[1][0]
            r_difference = current[0][1] - current[1][1]
            #perform a jump action from previous position, using the block
            #on the current position
            for next in next_coordinates:
                #new position reached by jump action has not been visited.
                #Assign path length
                if next[0] == current[0][0]+q_difference and\
                next[1] == current[0][1]+r_difference:
                    if path_dict.get(next,-1) == -1:
                        frontier.put((next, current[1]))
                    #Assign path length to the new position reached by jump
                    #action if the new path length is shorter
                    elif path_dict[next] > new_path:
                        path_dict[next] = new_path

    return

#Function which implements the A* Algorithm for pathfinding.
#Positions would be the starting positions of all the players.
#return a dictionary that store the Operation object that get to each state
def A_Star(positions,blocks, colour):
    count = 0

    #Priority queue to choose state with lowest cost
    frontier = PriorityQueue()
    item = (0,positions)
    frontier.put(item)
    came_from = {}

    #To store cost upto the position and path the player came from
    cost_so_far = {}
    came_from[positions] = None
    cost_so_far[positions] = 0

    while not frontier.empty():
        count += 1
        current = frontier.get()

        #Goal check is going to return if all the pieces have exited the board
        is_goal = True
        for piece in current[1]:
            if piece != removed:
                is_goal = False
                break
        if is_goal:
            break

        for state in next_states(current[1], blocks, colour):
            new_position = state[0]

            new_cost = cost_so_far[current[1]] + 1

            #To calculate the path cost
            if cost_so_far.get(new_position,-1)==-1 or new_cost < cost_so_far[new_position]:
                cost_so_far[new_position] = new_cost
                priority = new_cost+ total_heuristic(new_position,blocks,colour)
                item = (priority,new_position)
                frontier.put(item)
                came_from[new_position] = (current[1], state[1])
    return came_from

#Converts a list of lists into a tuple of tuples
def List_to_Tuple(list):
    return tuple(tuple(i) for i in list)

def main():

    #Storing data from JSON file and initializing board
    with open(sys.argv[1]) as file:
        data = json.load(file)
    count = 0
    pieces = List_to_Tuple(data.get('pieces'))
    blocks = List_to_Tuple(data.get('blocks'))
    colour = data.get('colour')
    output = []
    board_dict = {}

    #adding pieces and blocks into board_dict for visualisation of the board
    for piece in pieces:
        board_dict[tuple(piece)] = 'p'
    for piece in blocks:
        board_dict[tuple(piece)] = 'b'

    #remove exit position from exit_dict if the position is occupied
    #by a block
    for block in blocks:
        if block in exit_dict[colour]:
            exit_dict[colour].remove(block)

    #Compute shortest path and print board
    shortest_path(blocks,pieces, colour)
    print_board(board_dict)
    print_board(path_dict)
    #search for solution
    solution_dict = A_Star(pieces,blocks,colour)
    #initialise goal state
    goal = [removed]*len(pieces)
    goal = tuple(goal)

    #backtracking from goal to find the shortest solution
    while goal or previous_state:
        previous_state = solution_dict[goal]
        if previous_state != None:
            output.append((goal, previous_state[1].previous_position,
            previous_state[1].new_position, previous_state[1].action))
            goal = previous_state[0]
        else:
            break

    #print out solution
    for operation in reversed(output):
        del board_dict[tuple(operation[1])]
        count+=1
        if operation[3] != "EXIT":
            board_dict[tuple(operation[2])] = 'r'
        if operation[3] == "EXIT":
            print("%s from %s."%(operation[3], str(operation[1])))
        else:
            print("%s from %s to %s."%(operation[3], str(operation[1]), str(operation[2])))

    print("#",count)




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
