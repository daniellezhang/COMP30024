import copy
import player
import sys

board_dict = {          #Representation of the board

    'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
    'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
    'b': [(0,3),(1,2),(2,1),(3,0)]
}

exited_piece_count = {
    'r':0,'g':0,'b':0
}


#test possible_action()
for action in player.possible_action(2,board_dict,'r'):
    print(action)

#test the board_update function
"""print(board_dict)
action = ("JUMP",((-3,1),(-3,3)))
new_board = player.board_update(board_dict,action)
print(new_board)"""

#print(player.hex_distance((-3,5),(-3,1)))
"""
current = player.State('r', board_dict, exited_piece_count, None, None)
current.print_state()
next = player.generate_state(current, ("MOVE",((-3,0),(-2,0))))
next.print_state()
next = player.generate_state(next,("PASS",None))
next.print_state()
next = player.generate_state(next,("PASS",None))
next.print_state()
"""
