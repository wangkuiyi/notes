W = tf.Variable(rng.randn(), name="weight")  # The model parameters.
b = tf.Variable(rng.randn(), name="bias")

X = tf.placeholder("float")  # <== Construct the training graph.
Y = tf.placeholder("float")
pred = tf.add(tf.multiply(X, W), b)
cost = tf.smooth_l1_loss(pred, Y)
optmr = tf.train.GradientDescentOptimizer(0.1).minimize(cost)

init = tf.global_variables_initializer()  # <== Construct the init graph.

with tf.Session() as sess:
    sess.run(init)  # <== Run the init graph.
    for epoch in range(training_epochs):
        for (x, y) in zip(train_X, train_Y):
            sess.run(optmr, {X: x, Y: y})  # <== Run the training graph
