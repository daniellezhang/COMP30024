exit_dict = {"r":[(3,-3),(3,-2),(3,-1),(3,0)],
"g":[(-3,3),(-2,3),(-1,3),(-0,3)],
"b":[(-3,0),(-2,-1),(-1,-2),(0,-3)]}

weights = (1,1,1)

class State:
    def __init__(self, colour, board, exited_piece_count, action, previous_evaluation_feature):
        self.colour = colour
        self.board = board
        self.action = action
        self.n_pieces_on_board = len(board[colour])
        self.n_pieces_left = 4-exited_piece_count[colour]
        if(self.n_pieces_left <= self.n_pieces_on_board):
            self.n_peices_missing = 0
        else:
            self.n_pieces_missing = self.n_pieces_left - self.n_pieces_on_board
        self.sum_exit_distance = sum_squared_distance_to_exit(board, colour, n_pieces_left)
        self.evaluation_feature = (n_peices_missing, n_pieces_left, sum_exit_distance)
        self.previous_evaluation_feature = previous_evaluation_feature
        self.evaluation = evaluate(evaluation_feature, previous_evaluation_feature)


def hex_distance(coordinate1, coordinate2):
    return (abs(coordinate1[0]-coordinate2[0])
    + abs(coordinate1[0]+coordinate1[1]-coordinate2[0]-coordinate2[1])
    +abs(coordinate1[1]-coordinate2[1]))/2

def sum_squared_distance_to_exit(board, colour,n_pieces_left):
    min_dist_list = []
    for piece in board[colour]:
        min_dist_list.append(squared_min_distance_to_exit(piece, colour))
    min_dist_list.sort()
    sum = 0
    for i in range(0,n_pieces_left):
        sum += min_dist_list[i]

    return sum

def squared_exit_distance(piece, colour):
    min_dist = 36
    for exit in exit_dict[colour]:
        distance = hex_distance(piece, exit)
        if(distance < min_dist):
            min_dist=distance

return min_dist

def evaluate(evaluation_feature, previous_evaluation_feature):
    sum = 0
    for i in range(0,3):
        sum += weight[i]*(previous_evaluation_feature[i] - evaluation_feature[i])

    return sum




class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your
        program will play as (Red, Green or Blue). The value will be one of the
        strings "red", "green", or "blue" correspondingly.
        """
        # TODO: Set up state representation.
        self.colour = colour
        self.exited_piece_count = {"r":0, "g":0, "b":0}




    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. If there are no allowed
        actions, your player must return a pass instead. The action (or pass)
        must be represented based on the above instructions for representing
        actions.
        """
        # TODO: Decide what action to take.
        return ("PASS", None)


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s
        turns) to inform your player about the most recent action. You should
        use this opportunity to maintain your internal representation of the
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (Red, Green or Blue). The value will be one of the strings "red",
        "green", or "blue" correspondingly.

        The parameter action is a representation of the most recent action (or
        pass) conforming to the above in- structions for representing actions.

        You may assume that action will always correspond to an allowed action
        (or pass) for the player colour (your method does not need to validate
        the action/pass against the game rules).
        """
        # TODO: Update state representation in response to action.





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
                    #actions.append(Operation(current_piece,jump_pos,"JUMP"))
                    actions.append(("JUMP",(current_piece,jump_pos)))
        #neighbour not occupied. A move action is valid
        else:
            #actions.append(Operation(current_piece, neighbour,"MOVE"))
            actions.append(("MOVE",(current_piece,neighbour)))

    return actions
