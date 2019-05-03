from sys import maxsize

##===========================
##TREE BUILDER

#i - integer
#c - colour
#t - tuple

#Board representation :
#Board_dict will be a dictionary which contains the representation of the board.
#for representation

board_dict = {          #Representation of the board

    'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
    'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
    'b': [(0,3),(1,2),(2,1),(3,0)]
}

next_colour = {         #To decide which player's turn is next
    'r':'g',
    'g':'b',
    'b':'r'
}

#'r' = 0
#'g' = 1
#'b' = 2

blocks = {}             #No blocks atm, for ease.

repCopy = board_dict    #Representational copy of the board to be passed.

class Node(object):
    def __init__(self, i_depth, c_playerColour, d_boardDict, t_evalue = (0, 0, 0)): #t_evalue = (0, 0, 0)?

        self.i_depth = i_depth                  #Depth of the tree
        self.c_playerColour = c_playerColour    #Colour of the player who's turn it is to make the next move.
        self.d_boardDict = d_boardDict          #Representation of the board
        self.t_evalue = t_evalue                #The evaluation tuple to be used for MaxN
        self.children = []                      #Children to each node
        self.CreateChildren()                   #Method to create children to each node

    def CreateChildren(self):
        if self.i_depth >= 0:

            colourPieces = self.d_boardDict[self.c_playerColour]   #List of tuples containing the
                                                                   # coords of the pieces of this specific colour

            length = len(colourPieces) #Length of the list of all the tuples
                                       #of all the positions of the specific colour
            i = 0
            while(i < length):

                #As taken from the definition of possible_action
                #To generate all the possible actions for each piece individually
                for j in possible_action(i, colourPieces, blocks, self.c_playerColour):


                    #When we take the move, how that selected piece is gonna change.
                    changedBoard = self.d_boardDict

                    #Explicitly moving piece to the new position on the representation.
                    changedBoard[self.c_playerColour][i] = j

                    #Recursing, to find the possible moves of all the children, new position of the piece we just took.
                    self.children.append(Node(self.i_depth - 1, next_colour[self.c_playerColour],
                                              changedBoard,
                                              self.RealEvaluation(changedBoard)))


    #Evaluation function that takes in the board
    #representation and returns a tuple of the rewards.
    def RealEvaluation(self, boardState):

        #Put the code for the evaluation here
        return 0





#======================================================================================================================
#ALGORITHM
def MaxN(node, i_depth, c_playerColour):

    #Check if the depth is 0 or we have reached the node that is a win or lose condition.
    if(i_depth == 0): #or ()'''Check if we have reached a win or lose condition ''':
        return node.t_evalue

    t_bestEvalue = (-maxsize,-maxsize,-maxsize)

    ''''#For loop to iterate through every child.
    for i in range(len(node.children)):
        child = node.children[i]'''

    #For loop through every child
    for child in node.children:
        t_evalue = MaxN(child, i_depth - 1, next_colour[c_playerColour])

        #Change by indexing the colour of the player in the tuple bestEvalue
        #Calculate the max between current evaluation and the maximum of the child
        t_bestEvalue = max(t_bestEvalue,  )

    return t_bestEvalue














