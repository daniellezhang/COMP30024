'''
written by Danielle Zhang on 15/05/19
script to run tensorflow for performing machine learning on evaluation Function
based on https://github.com/aymericdamien/TensorFlow-Examples/
by Aymeric Damien
'''


from subprocess import call
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

dimension = 4

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

training_rate = 0.001
learning_rate = 0.001
training_epoch = 5
converge_delta = 0.0001
is_converging = False
winning = 0.1
losing = -0.1
gamma = 0.99

command_list = [
#"python3 -m referee random_player beta_come beta_come",
#"python3 -m referee random_player random_player beta_come",
"python3 -m referee random_player greedy_player beta_come",
"python3 -m referee greedy_player beta_come random_player",
"python3 -m referee beta_come random_player greedy_player",
"python3 -m referee greedy_player random_player beta_come"
]
#command = "python3 -m referee beta_come random_player greedy_player"
n_command = 0
threshold = 100
while(is_converging == False and n_command < threshold):
    command = command_list[n_command%len(command_list)]
    log = open("/Users/zhangdanielle/code/COMP30024/part-B/log",'w+')
    log.write("#iteration: %d,command:%s\n"%(n_command+1,command))
    log.close()
    #play a game with the given command
    call(command, shell = True)
    #setting up
    f = open("/Users/zhangdanielle/code/COMP30024/part-B/weight",'r')
    all_weights = f.readlines()
    f.close()
    latest_weight = all_weights[-1].split(',')
    weight = np.array(latest_weight).astype(np.float32)

    f = open("/Users/zhangdanielle/code/COMP30024/part-B/result",'r')
    all_result = f.readlines()
    f.close()
    latest_result = all_result[-1].split(',')
    result = latest_result[0]
    winner = None
    reward = 0

    x = []
    y = []
    n_samples = 0
    exited_count = latest_result[1:]
    for i in range(len(exited_count)):
        exited_count[i] = int(exited_count[i])
        if exited_count[i] < 4:
            reward = losing
        else:
            reward = winning
        filename = "/Users/zhangdanielle/code/COMP30024/part-B/"+index_dict[i]
        f=open(filename, 'r')
        lines = f.readlines()
        n_lines = len(lines)
        n_samples += n_lines
        discount = 1
        for line in lines:
            features = line.split(',')[:-1]
            for i in range(len(features)):
                features[i] = float(features[i])
            eval = float(features[-1])+reward*discount
            discount *= gamma
            x.append(features)
            y.append([eval])


    training_x = np.array([feature for feature in x]).astype(np.float32)
    training_y = np.array([eval for eval in y]).astype(np.float32)

    W = tf.Variable([0]*dimension, name = "weight", dtype = tf.float32)
    #b = tf.Variable(0.0, name = "bias",dtype = tf.float32)

    # tf Graph Input
    X = tf.placeholder(shape = (n_samples,dimension), dtype = tf.float32)
    Y = tf.placeholder(shape = (n_samples,1),dtype = tf.float32)

    pred = tf.multiply(X,W)
    # Mean squared error
    cost = tf.reduce_sum(tf.pow(pred-Y, 2))/(2*n_samples)
    # Gradient descent
    optimizer = tf.train.GradientDescentOptimizer(training_rate).minimize(cost)

    # Initializing the variables
    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(training_epoch):
            sess.run(optimizer, feed_dict={X: training_x, Y: training_y})
            c = sess.run(cost,feed_dict={X: training_x, Y: training_y})
            print("C=",c,"W=", sess.run(W), '\n')

        print("Optimization Finished!")

        #calculate new weight and Bias and the delta between old and new weight
        deltas = [0]*len(weight)
        for j in range(len(weight)):
            delta = learning_rate*(sess.run(W)[j]-weight[j])
            weight[j] += delta
            deltas[j] = delta


        print(weight)

        #write new weight and bias into the weight file
        f = open("/Users/zhangdanielle/code/COMP30024/part-B/weight",'a+')
        new_weight = ""
        for w in weight:
            new_weight+="{:.5f},".format(w)
        new_weight = new_weight[:-1]
        new_weight += '\n'
        f.write(new_weight)
        f.close()
        #clear the supplementary file
        call("bash /Users/zhangdanielle/code/COMP30024/part-B/remove_files.sh",shell = True)

        #update the number of commands have been called
        n_command+=1
        temp_converage  = True
        #check if the weight is converging`
        for i in range(len(deltas)):
            if abs(deltas[i]) >= converge_delta:
                temp_converage = False
                break
            is_converaging = temp_converage
