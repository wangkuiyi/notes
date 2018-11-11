def f(W, x):
    h1 = tf.matmul(x, W)
    h2 = tf.tanh(h1)
    out = tf.reduce_sum(h2)
    return out

dfdW = tangent.grad(f)
