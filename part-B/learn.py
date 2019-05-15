from subprocess import call
import tensorflow as tf
import numpy as np

index_dict = {
    0: "red",
    1: "green",
    2:"blue"
}
colour_dict = {
    'b':"blue",
    'r':"red",
    'g':"green"
}

#setting up
f = open("/Users/zhangdanielle/code/COMP30024/part-B/beta_come/weight",'r')
all_weights = f.readlines()
f.close()
latest_weight = all_weights[-1].split(',')
weight = np.array(latest_weight).astype(np.float32)

training_rate = 0.01

f = open("/Users/zhangdanielle/code/COMP30024/part-B/beta_come/result",'r')
all_result = f.readlines()
f.close()
latest_result = all_result[-1].split(',')
result = latest_result[0]
winner = None

#game is a draw. set winner to be the player with the highest number of exited pieces
if result == "draw":
    exited_count = latest_result[1:]
    max_exit = 0

    for i in range(3):
        if int(exited_count[i]>max_exit):
            winner = index_dict[i]

    '''weight += 0.1*np.random.randn(len(weight))
    line = ','.join(['%.5f' % w for w in weight])
    line += '\n'
    print(line)
    f = open("/Users/zhangdanielle/code/COMP30024/part-B/beta_come/weight",'a+')
    f.write(line)
    f.close()'''

#game has a winner.load the evaluation history of the winner
else:
    winner = colour_dict[result]

filename = "/Users/zhangdanielle/code/COMP30024/part-B/beta_come/"+winner
f=open(filename, 'r')
lines = f.readlines()
eval_matrix = np.array([line.split(',') for line in lines]).astype(np.float32)
print(eval_matrix)
#with tf.Session() as sess:


'''call("bash /Users/zhangdanielle/code/COMP30024/part-B/beta_come/remove_files.sh",
shell = True)'''
