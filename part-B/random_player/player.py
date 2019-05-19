from beta_come.helper import possible_action,board_update
from beta_come.state import State
from beta_come.player import evaluate, features
import random

class RandomPlayer:
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
            self.filename = "/Users/zhangdanielle/code/COMP30024/part-B/"+colour


    def action(self):
        actions = []
        output = None
        for i in range(len(self.board[self.colour])):
            for action in possible_action(i, self.board, self.colour):
                actions.append(action)
        if len(actions) > 1:
            index = random.randint(0,len(actions)-1)
            output = actions[index]
        else:
            output = ("PASS",None)
        new_board = board_update(self.colour, self.board, output)
        current_state = State(self.colour,new_board, self.exited_piece_count, output, None)
        '''f = open(self.filename,'a+')
        line =""
        new_evaluation_feature = features(self.colour, current_state)
        for i in range(len(new_evaluation_feature)):
            line += str(new_evaluation_feature[i])
            line +=','
        line += str(evaluate(self.colour, current_state, self.weight))
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
