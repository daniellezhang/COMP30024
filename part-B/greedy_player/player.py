from beta_come.helper import possible_action,board_update
from beta_come.state import State
from beta_come.player import evaluate, features
import random

class GreedyPlayer:
    def __init__(self, colour):
            self.colour = colour[0]
            self.exited_piece_count = {"r":0, "g":0, "b":0}
            self.board = {
                    'r': [(-3,0),(-3,1),(-3,2),(-3,3)],
                    'g': [(0,-3),(1,-3),(2,-3),(3,-3)],
                    'b': [(0,3),(1,2),(2,1),(3,0)]
            }
            #load the weight
            '''f = open("/Users/zhangdanielle/code/COMP30024/part-B/weight",'r')
            all_weights = f.readlines()
            f.close()
            latest_weight = all_weights[-1].split(',')
            for i in range(len(latest_weight)):
                latest_weight[i] = float(latest_weight[i])'''
            latest_weight = [-0.60735,-6.07406,-6.07713,0.61072]
            #weights for evaluation Function
            #(n_pieces_missing,n_pieces_left,sum_exit_distance,oppoenent_pieces)
            self.weight = latest_weight
            #create a new file to record the evaluation for every output action
            #self.filename = "/Users/zhangdanielle/code/COMP30024/part-B/"+colour


    def action(self):

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
                if action[0] == "EXIT":
                    eval = new_eval
                    output = action
                    feature = features(self.colour, current_state)
                    break
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
        return
