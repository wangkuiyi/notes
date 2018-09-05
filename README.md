# Learning Eager Execution

## The [Google Blog Post](https://developers.googleblog.com/2017/10/eager-execution-imperative-define-by.html)

### Automatic Differentiation

```python
def square(x):
  return tf.multiply(x, x) 
grad = tfe.gradients_function(square)
print(square(3.))    # [9.]
print(grad(3.))      # [6.]
```

Curious how does Eager Execution's C++ API expose higher-order functions and function-typed return values. Does it use [C++11's Lambda](https://en.cppreference.com/w/cpp/language/lambda)?

