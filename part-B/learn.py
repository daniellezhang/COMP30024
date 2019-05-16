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
training_epoch = 10

#call("python -m referee beta_come beta_come beta_come", shell = True)

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
winning = 1
losing = -1
reward = 0

x = []
y = []
n_samples = 0
exited_count = latest_result[1:]
for i in range(len(exited_count)):
    exited_count[i] = int(exited_count[i])
    if exited_count[i] == 0:
        reward = losing
    else:
        reward = winning *exited_count[i]/4
    filename = "/Users/zhangdanielle/code/COMP30024/part-B/"+index_dict[i]
    f=open(filename, 'r')
    lines = f.readlines()
    n_samples += len(lines)
    for line in lines:
        features = line.split(',')[:-1]
        for i in range(len(features)):
            features[i] = float(features[i])
        eval = float(features[-1])+reward
        x.append(features)
        y.append([eval])


training_x = np.array([feature for feature in x]).astype(np.float32)
training_y = np.array([eval for eval in y]).astype(np.float32)

W = tf.Variable([0]*dimension, name = "weight", dtype = tf.float32)
#b = tf.Variable(0.0, name = "bias",dtype = tf.float32)

# tf Graph Input
X = tf.placeholder(shape = (n_samples,dimension), dtype = tf.float32)
Y = tf.placeholder(shape = (n_samples,1),dtype = tf.float32)
print(X.shape)
print(Y.shape)

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

    #calculate new weight and Bias
    for j in range(len(weight)):
        weight[j] += learning_rate*(sess.run(W)[j]-weight[j])

    print(weight)

    #write new weight and bias into the weight file
    f = open("/Users/zhangdanielle/code/COMP30024/part-B/weight",'a+')
    new_weight = ""
    for w in weight:
        new_weight+="{:.3f},".format(w)
    new_weight = new_weight[:-1]
    new_weight += '\n'
    f.write(new_weight)
    f.close()
    #clear the supplementary file
    call("bash /Users/zhangdanielle/code/COMP30024/part-B/remove_files.sh",shell = True)
