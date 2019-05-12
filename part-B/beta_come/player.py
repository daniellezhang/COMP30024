import copy
import sys
from sys import maxsize

exit_dict = {"r":[(3,-3),(3,-2),(3,-1),(3,0)],
"g":[(-3,3),(-2,3),(-1,3),(-0,3)],
"b":[(-3,0),(-2,-1),(-1,-2),(0,-3)]}

weights = (1,5,1)

board_dict = {          #Representation of the board

    'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
    'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
    'b': [(0,3),(1,2),(2,1),(3,0)]
}

#May have to define this depending on how the sequence of players is decided by the referee program.
next_colour = {         #To decide which player's turn is next
    'r':'g',
    'g':'b',
    'b':'r'
}

player_index = {

'r' : 0 ,
'g' : 1 ,
'b': 2

}
blocks = {}             #No blocks atm, for ease.

repCopy = board_dict    #Representational copy of the board to be passed.

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

#generate values for feature that are used for evaluation function
#from the perspective of the given player
def features(colour,state):
    board = state.board
    exited_piece_count = state.exited_piece_count
    n_pieces_on_board = len(board[colour])
    n_pieces_left = 4-exited_piece_count[colour]
    if(n_pieces_left <= n_pieces_on_board):
        n_pieces_missing = 0
    else:
        n_pieces_missing = n_pieces_left - n_pieces_on_board
    sum_exit_distance = sum_squared_distance_to_exit(board, colour)
    return (n_pieces_missing,n_pieces_left,sum_exit_distance)


def hex_distance(coordinate1, coordinate2):
    return (abs(coordinate1[0]-coordinate2[0])
    + abs(coordinate1[0]+coordinate1[1]-coordinate2[0]-coordinate2[1])
    +abs(coordinate1[1]-coordinate2[1]))/2

def sum_squared_distance_to_exit(board, colour):
    sum=0
    for piece in board[colour]:
        sum += squared_exit_distance(piece, colour)
    return sum

def squared_exit_distance(piece, colour):
    min_dist = 36
    for exit in exit_dict[colour]:
        distance = hex_distance(piece, exit)
        if(distance < min_dist):
            min_dist=distance
    return min_dist

#evaluate the state from the given player's perspective
def evaluate(colour, current_state,previous_state):
    previous_evaluation_feature = features(colour, previous_state)
    current_evaluation_feature = features(colour, current_state)
    # no previous_evaluation_feature. this is the very first state. return 0
    if previous_evaluation_feature == None:
        return 0
    sum = 0
    for i in range(0,3):
        sum += weights[i]*(previous_evaluation_feature[i] - current_evaluation_feature[i])

    return sum


#a function to generate new board representation based on the action
def generate_state(previous_state, action):
    colour = next_colour[previous_state.colour]
    board = board_update(previous_state.colour,previous_state.board,action)
    #exit action. update the exit pieces count
    if(action[0] == "EXIT"):
        exited_piece_count = copy.deepcopy(previous_state.exited_piece_count)
        exited_piece_count[colour] += 1
    else:
        exited_piece_count = previous_state.exited_piece_count

    return State(colour,board, exited_piece_count, action, previous_state)



# a class for the node in the maxN search tree
class Node(object):
    def __init__(self, i_depth, colour, state, t_evalue = None):

        #Put blocks after clarifying the state of the program.

        self.i_depth = i_depth                  #Depth of the tree
        self.colour = colour    #Colour of the player that is taking the action
        self.t_evalue = t_evalue                #The evaluation tuple to be used for MaxN
        self.state = state                      #the state of the board
        self.children = []                      #Children to each node
        self.CreateChildren()                   #Method to create children to each node

    def CreateChildren(self):
        if self.i_depth >= 0:

            colourPieces = self.state.board[self.colour]   #List of tuples containing the
                                                                   # coords of the pieces of this specific colour
            length = len(colourPieces) #Length of the list of all the tuples
                                       #of all the positions of the specific colour
            i = 0
            while(i < length):

                #As taken from the definition of possible_action
                #To generate all the possible actions for each piece individually
                for action in possible_action(i, self.state.board, self.colour):

                    new_state = generate_state(self.state,action)

                    #Recursing, to find the possible moves of all the children, new position of the piece we just took.
                    self.children.append(Node(self.i_depth - 1, next_colour[self.colour], new_state,
                                              self.Evaluation(self.i_depth - 1,new_state, self.state)))
                i+=1


    #Evaluation function that takes in the board
    #representation and returns a tuple of the rewards.
    def Evaluation(self,i_depth, newState, previousState):

        if i_depth == 0:
            evaluationVector = [0]*3
            for colour in 'rgb':
                index = player_index[colour]
                evaluationVector[index]=evaluate(colour,newState, previousState)

            return evaluationVector
        else:
            return None

#======================================================================================================================
#ALGORITHM_
def MaxN(node, i_depth, c_playerColour):

    #Check if the depth is 0 or we have reached the node that is a win or lose condition.
    if(i_depth == 0): #or ()'''Check if we have reached a win or lose condition ''':

        #Works on the basis that the top constructor calls and gives a value to each node
        #on it's creation
        return node.t_evalue

    #Initializing with -Max value
    #Turn of our maximizingPLayer
    #To stay true to the algorithm
    if c_playerColour:
        t_maxEvalue = (-maxsize,-maxsize,-maxsize)

        #For loop through every child
        for child in node.children:

            #Evaluation of the child
            t_evalue = MaxN(child, i_depth - 1, next_colour[c_playerColour])

            #Calculate the max between current evaluation and the maximum of the child
            #Essentially, do we have to calculate the max of the two, and send back the whole tuple,
            #not just the single record.


            #Check this line of code
            if max(t_maxEvalue[player_index[c_playerColour]], t_evalue[player_index[c_playerColour]]) == t_evalue[player_index[c_playerColour]]:
                t_maxEvalue = t_evalue

    #Draw visualization.
    return t_maxEvalue

#At every move, a new tree has to be generated? Create the maincode or wincondition in such a way.
#The tree generation should keep happening while the Win condition is not met by our or any
#Other player.


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



def print_board(board_dict, message="", debug=False):

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
    print(board)



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

        #load the weight

        #f = open("/Users/zhangdanielle/code/COMP30024/part-B/beta_come/weight",'r')


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

        tree_depth = 3
        c_curr_player = self.colour
        head_state = State(self.colour, self.board, self.exited_piece_count, None, None)
        node = Node(tree_depth, c_curr_player, head_state)
        print("#Hello world")
        #This is the node after the best move has been made.
        bestNode = None

        t_max_value = (-maxsize, -maxsize, -maxsize)
        i_eval_depth = tree_depth - 1

        #Determine the best move
        for child in node.children:

            t_val = MaxN(child, i_eval_depth, next_colour[c_curr_player])
            if child.state.action[0] == "EXIT":
                t_max_value = t_val
                bestNode = child
                return child.state.action
            elif max(t_max_value[player_index[c_curr_player]],
                   t_val[player_index[c_curr_player]]) == t_val[player_index[c_curr_player]]:
                t_max_value = t_val
                bestNode = child

        return bestNode.state.action

    def update(self, colour, action):
        # TODO: Update state representation in response to action.
        self.board = board_update(colour[0], self.board, action)
        if action[0] == "EXIT":
            self.exited_piece_count[colour[0]] += 1
        return


#Add evaluation function, figure out if it would take in the board_dict or state of the game,
#Ensure the code for Node and evaluation function work in Lieu.
#Change MaxN to return in the representation we want.
