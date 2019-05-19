import copy
import sys
from sys import maxsize
from beta_come.state import State
from beta_come.helper import print_board,possible_action, board_update

exit_dict = {"r":[(3,-3),(3,-2),(3,-1),(3,0)],
"g":[(-3,3),(-2,3),(-1,3),(-0,3)],
"b":[(-3,0),(-2,-1),(-1,-2),(0,-3)]}

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


#threshold to turn off the player's greedy mode
greedy_distance = 2

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
    if n_pieces_on_board != 0:
        n_piece = n_pieces_on_board
        if n_pieces_on_board >=4:
            n_piece = 3
        avg_exit_distance = average_distance(board, colour, n_piece)
    else:
        avg_exit_distance = 0
    missing_oppoenent_pieces = 0
    for opponent in "rgb":
        if opponent != colour:
            if len(board[opponent]) + exited_piece_count[opponent] < 4:
                missing_oppoenent_pieces += (len(board[opponent]) + exited_piece_count[opponent])-4
    return (n_pieces_missing,n_pieces_left,avg_exit_distance,missing_oppoenent_pieces)


def hex_distance(coordinate1, coordinate2):
    return (abs(coordinate1[0]-coordinate2[0])
    + abs(coordinate1[0]+coordinate1[1]-coordinate2[0]-coordinate2[1])
    +abs(coordinate1[1]-coordinate2[1]))/2


def average_distance(board, colour, n_piece):
    distance_list = []
    orderedList = []
    sum = 0

    for piece in board[colour]:
        distance_list.append((exit_distance(piece, colour), piece))
    distance_list = sorted(distance_list)
    for i in range(n_piece):
        sum += distance_list[i][0]
    sum/=n_piece

    return sum
def sum_distance_to_exit(board, colour):
    sum=0
    for piece in board[colour]:
        sum += exit_distance(piece, colour)
    return sum

def exit_distance(piece, colour):
    min_dist = 36
    for exit in exit_dict[colour]:
        distance = hex_distance(piece, exit)
        if(distance < min_dist):
            min_dist=distance
    if min_dist == 0:
        min_dist += 1
    return min_dist*min_dist

#evaluate the state from the given player's perspective
def evaluate(colour, current_state, weight):
    current_evaluation_feature = features(colour, current_state)
    sum = 0
    for i in range(len(weight)):
        sum += weight[i]*(current_evaluation_feature[i])

    return sum

#find the closest opponent's distance to the given player
def closest_opponent(colour, board):
    min_dist = 100
    pieces = board[colour]
    for c in "rgb":
        if c != colour:
            for opponent in board[c]:
                for piece in pieces:
                    dist = hex_distance(piece, opponent)
                    if dist <min_dist:
                        min_dist = dist
    return min_dist

#This function sorts the pieces based on the distance to their exit positions
def sorted_pieces(board, colour):

    computationList = []
    orderedList = []

    for piece in board[colour]:
        computationList.append((exit_distance(piece, colour), piece))

    computationList = sorted(computationList)

    for i, j in computationList:
        orderedList.append(j)

    board[colour] = orderedList

    return

#a function to generate new board representation based on the action
def generate_state(previous_state, action):
    colour = next_colour[previous_state.colour]
    board = board_update(previous_state.colour,previous_state.board,action)
    #exit action. update the exit pieces count
    if(action[0] == "EXIT"):
        exited_piece_count = copy.deepcopy(previous_state.exited_piece_count)
        exited_piece_count[previous_state.colour] += 1
    else:
        exited_piece_count = previous_state.exited_piece_count

    return State(colour,board, exited_piece_count, action, previous_state)



# a class for the node in the maxN search tree
class Node(object):
    def __init__(self, i_depth, colour, state,weight, t_evalue = None):

        #Put blocks after clarifying the state of the program.

        self.i_depth = i_depth                  #Depth of the tree
        self.colour = colour    #Colour of the player that is taking the action
        self.t_evalue = t_evalue                #The evaluation vector to be used for MaxN
        self.state = state                      #the state of the board
        self.children = []                      #Children to each node
        self.weight = weight                             #Weight vector used for evaluation
        self.CreateChildren()                   #Method to create children to each node

    def CreateChildren(self):
        if self.i_depth >= 0:

            colourPieces = self.state.board[self.colour]   #List of tuples containing the
                                                                   # coords of the pieces of this specific colour
            length = len(colourPieces) #Length of the list of all the tuples
                                       #of all the positions of the specific colour
            i = 0
            #the number of pieces on the board for this player is
            # higher than the number of pieces need to exit in order for the players
            #to win. reduce the branching factor and only expand the possible actions
            #of the pieces that are the closest to the exit positions
            '''if length > 4 - self.state.exited_piece_count[self.colour]:'''
            if length >=4:
                sorted_pieces(self.state.board, self.colour)
                length  = 3
            '''length *=2/3'''
            n_action = 0
            while(i < length):

                #As taken from the definition of possible_action
                #To generate all the possible actions for each piece individually
                for action in possible_action(i, self.state.board, self.colour):
                    n_action += 1

                    new_state = generate_state(self.state,action)

                    #Recursing, to find the possible moves of all the children, new position of the piece we just took.
                    self.children.append(Node(self.i_depth - 1, next_colour[self.colour], new_state,self.weight,
                                              self.evaluation(self.i_depth - 1,new_state, self.state, self.weight)))
                i+=1

            #no action at all. this player cannot play any move. add PASS action
            if n_action == 0:
                action  = ("PASS", None)
                new_state = generate_state(self.state,action)
                self.children.append(Node(self.i_depth - 1, next_colour[self.colour], new_state,self.weight,
                                          self.evaluation(self.i_depth - 1,new_state, self.state, self.weight)))


    #Evaluation function that takes in the board
    #representation and returns a list of the rewards.
    def evaluation(self,i_depth, newState, previousState, weight):

        if i_depth == 0:
            evaluationVector = [0]*3
            for colour in 'rgb':
                index = player_index[colour]
                evaluationVector[index]=evaluate(colour,newState, weight)

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


class MaxNPlayer:
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

        self.is_greedy = True

        #load the weight
        '''f = open("/Users/zhangdanielle/code/COMP30024/part-B/weight",'r')
        all_weights = f.readlines()
        f.close()
        latest_weight = all_Weights[-1].split(',')
        for i in range(len(latest_weight)):
            latest_weight[i] = float(latest_weight[i])'''
        latest_weight = [-0.60735,-6.07406,-6.07713,0.61072]
        #weights for evaluation Function
        #(n_pieces_missing,n_pieces_left,sum_exit_distance,oppoenent_pieces)
        self.weight = latest_weight
        #create a new file to record the evaluation for every output action
        #self.filename = "/Users/zhangdanielle/code/COMP30024/part-B/"+colour

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

        if self.is_greedy == False:
            tree_depth = 3
            c_curr_player = self.colour
            head_state = State(self.colour, self.board, self.exited_piece_count, None, None)
            node = Node(tree_depth, c_curr_player, head_state, self.weight)
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
                    break
                elif max(t_max_value[player_index[c_curr_player]],
                       t_val[player_index[c_curr_player]]) == t_val[player_index[c_curr_player]]:
                    t_max_value = t_val
                    bestNode = child


            #write the evaluation feature values and evaluation value into the file

            if bestNode == None:
                bestNode = node
                bestNode.state.action = ("PASS",None)

            '''f = open(self.filename,'a+')
            line =""
            new_evaluation_feature = features(self.colour, bestNode.state)
            for i in range(len(new_evaluation_feature)):
                line += str(new_evaluation_feature[i])
                line +=','
            line += str(evaluate(self.colour, bestNode.state, self.weight))
            line += '\n'
            f.write(line)
            f.close()'''
            return bestNode.state.action
        #player in greedy mode
        else:
            output = None
            eval = None
            feature = None
            for i in range(len(self.board[self.colour])):
                for action in possible_action(i, self.board, self.colour):
                    new_board = board_update(self.colour, self.board, action)
                    current_state = State(self.colour,new_board, self.exited_piece_count, output, None)
                    new_eval = evaluate(self.colour, current_state, self.weight)
                    if eval == None or new_eval > eval:
                        eval = new_eval
                        output = action
                        feature = features(self.colour, current_state)
            if output == None:
                output = ("PASS",None)
                current_state = State(self.colour,self.board, self.exited_piece_count, output, None)
                eval = evaluate(self.colour, current_state, self.weight)
                feature = features(self.colour, current_state)

            '''f = open(self.filename,'a+')
            line =""
            for i in range(len(feature)):
                line += str(feature[i])
                line +=','
            line += str(eval)
            line += '\n'
            f.write(line)
            f.close()'''
            return output


    def update(self, colour, action):
        #update the board reprensentation
        self.board = board_update(colour[0], self.board, action)
        #update the exited pieces count
        if action[0] == "EXIT":
            self.exited_piece_count[colour[0]] += 1
        #update the player mode
        #the player no longer plays greedy strategy when the closest oppoenent are two hexes away
        if self.is_greedy == True and closest_opponent(self.colour, self.board) <= greedy_distance:
            self.is_greedy = False
        elif len(self.board[self.colour]) > 4-self.exited_piece_count[self.colour]:
            # and self.exited_piece_count[self.colour]>0
            self.is_greedy = True


        return
