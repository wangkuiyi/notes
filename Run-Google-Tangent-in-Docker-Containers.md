# Run Google Tangent in Docker Containers

I want to contribute to Google Tangent. But I don't want to install the many dependencies, including the TensorFlow package, on my iMac. So, I use Docker containers.

As a developer, I am going to install tangent into the official TensorFlow Docker image; instead, I need to be able to run unit tests with the code I am editing. I do the following steps.

1. Clone the source code and get into the directory.
 
   ```bash
   git clone https://github.com/google/tangent
   cd tangent
   ```

1. Run a Docker container that executes the TensorFlow image, while bind mounts the current directory, which contains the tangent sub-directory of the source of Tangent, into the container as directory work.

   ```bash
   docker run  --rm -it -v $PWD:/work -w /work tensorflow/tensorflow:1.12.0 bash
   ```

1. Inside the container, install all dependencies.

   ```bash
   pip install -r requirements.txt
   ```

1. Inside, the container, set the environment variable `PYTHONPATH` so that we could import tangent resides in `/work/tangent`.

   ```bash
   export PYTHONPATH=/work
   ```

1. Let us try an example program. We could edit it on the host using whatever editor you like and put it in the cloned directory as `a.py`.  My simple example that uses TensorFlow Eager Execution is attached at the end of this page.  Then, inside the container, we can run it using the following command:

   ```bash
   python a.py
   ```

## A Simple Example

The following example comes from 

1. https://github.com/google/tangent/blob/master/README.md, and
1. https://github.com/google/tangent/issues/80#issuecomment-419987803

```python
import tangent
import tensorflow as tf

tf.enable_eager_execution()
tf.executing_eagerly()


def f(W, x):
    h1 = tf.matmul(x, W)
    h2 = tf.tanh(h1)
    out = tf.reduce_sum(h2)
    return out


dfdW = tangent.grad(f)

x = W = [[2.]]
print(dfdW(W, x, bout=tf.constant(1.0)))
```
