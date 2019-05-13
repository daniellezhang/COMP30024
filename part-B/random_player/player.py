import random
import copy

exit_dict = {"r":[(3,-3),(3,-2),(3,-1),(3,0)],
"g":[(-3,3),(-2,3),(-1,3),(-0,3)],
"b":[(-3,0),(-2,-1),(-1,-2),(0,-3)]}


def ring_generator(position, ring_no = 1):

    coordinates = []
    x_coordinates = []
    y_coordinates = []
    position = (int(position[0]),int(position[1]))

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
def possible_action(piece_index, board, player):
    current_piece = board[player][piece_index]
    all_neighbours = neighbours(current_piece)
    is_occupied = [False]*len(all_neighbours)

    actions = []
    #check if there is any neighbour that is occupied by other pieces
    for colour in "rgb":
        for i in range(len(board[colour])):
            if i != piece_index or colour != player:
                for j in range(len(all_neighbours)):
                    if all_neighbours[j] == board[colour][i]:
                        is_occupied[j] = True

    #check if the current piece is able to exit the board
    exit_list = exit_dict[player]
    for pos in exit_list:
        if pos == current_piece:
            #actions.append(Operation(current_piece,removed,"EXIT"))
            actions.append(("EXIT",current_piece))

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
                for colour in "rgb":
                    for j in range(len(board[colour])):
                        if board[colour][j] == jump_pos:
                            occupied = True
                            break
                #position is not occupied. Jump action is valid
                if not occupied:
                    #actions.append(Operation(current_piece,jump_pos,"JUMP"))
                    actions.append(("JUMP",(current_piece,jump_pos)))
        #neighbour not occupied. A move action is valid
        else:
            #actions.append(Operation(current_piece, neighbour,"MOVE"))
            actions.append(("MOVE",(current_piece,neighbour)))

    return actions
# update the board based on action
def board_update(player, board_dict, action):
    #pass action. no change to the state
    if action[0] == "PASS":
        return board_dict
    #find the piece that took the action
    new_board = copy.deepcopy(board_dict)
    if action[0] == "MOVE" or action[0] == "JUMP":
        moved_piece = action[1][0]
    else:
        moved_piece = action[1]
    for i in range(len(board_dict[player])):
        if board_dict[player][i] == moved_piece:
            current = i
            break

    #move action. update the position of moved piece
    if action[0] == "MOVE":
        new_board[player][current] = action[1][1]
    #jump action
    elif action[0] == "JUMP":
        #update the position of the moved piece
        new_board[player][current] = action[1][1]
        row = (action[1][0][0]+action[1][1][0])/2
        col =  (action[1][0][1]+action[1][1][1])/2
        middle_piece = (row, col)
        #check whether the piece that is jumped over need to be converted
        for colour in "rgb":
            for i in range(len(board_dict[colour])):
                if middle_piece == board_dict[colour][i]:
                    #convert the middle piece if it has a different colour
                    if colour != player:
                        new_board[player].append(middle_piece)
                        new_board[colour].remove(middle_piece)
                    break
    #exit action. remove the piece from the board
    elif action[0] == "EXIT":
        new_board[player].remove(moved_piece)


    return new_board


class RandomPlayer:
    def __init__(self, colour):
            self.colour = colour[0]
            self.exited_piece_count = {"r":0, "g":0, "b":0}
            """self.board = {
                'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
                'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
                'b': [(0,3),(1,2),(2,1),(3,0)]
            }"""
            self.board = {
                    'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
                    'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
                    'b': [(0,3),(1,2),(2,1),(3,0)]
            }


    def action(self):
        actions = []
        for i in range(len(self.board[self.colour])):
            for action in possible_action(i, self.board, self.colour):
                actions.append(action)
        if len(actions) > 1:
            index = random.randint(0,len(actions)-1)
            return actions[index]
        else:
            return ("PASS",None)

    def update(self, colour, action):
        #update the board reprensentation
        self.board = board_update(colour[0], self.board, action)
        #update the exited pieces count
        if action[0] == "EXIT":
            self.exited_piece_count[colour[0]] += 1
        return
