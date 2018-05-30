# Reading Notes: Google Tangent

## `grad`

The function [`grad`](https://github.com/google/tangent/blob/v0.1.9/tangent/grad_util.py#L333) calls autodiff in reverse mode:

```python
def grad(func,
         wrt=(0,),
         optimized=True,
         preserve_result=False,
         check_dims=True,
         verbose=0):
  return autodiff(
      func,
      wrt=wrt,
      motion='joint',
      mode='reverse',
      optimized=optimized,
      preserve_result=preserve_result,
      check_dims=check_dims,
      input_derivative=INPUT_DERIVATIVE.DefaultOne,
      verbose=verbose)
```

## `autodiff`

The function [`autodiff`](https://github.com/google/tangent/blob/v0.1.9/tangent/grad_util.py#L218) simply does the following given the default parameters:

```python
def autodiff(func,
             wrt=(0,),
             optimized=True,
             motion='joint',
             mode='reverse',
             preserve_result=False,
             check_dims=True,
             input_derivative=INPUT_DERIVATIVE.Required,
             verbose=0):
  node, namespace = autodiff_tree(func, wrt, motion, mode, preserve_result,
                                  check_dims, verbose)

  if mode == 'reverse' and motion == 'joint':
    # Pull the stack definition and initial gradient into the function body
    # TODO: Use first FunctionDef instead of first element
    node.body[0] = _create_joint(node.body[0], func, wrt, input_derivative)
  if optimized:
    node = optimization.optimize(node)
  node = comments.remove_repeated_comments(node)

  # Compile and return
  module = compile_.compile_file(node, namespace)
  if mode == 'forward' or motion == 'joint':
    return getattr(module, node.body[0].name)
```

Invocations:

1. `autodiff_tree`
1. `_create_joint`
1. `optimization.optimize`
1. `compile.compile_file`


### `autodiff_tree`

The function [`autodiff_tree`](https://github.com/google/tangent/blob/v0.1.9/tangent/grad_util.py#L114) traverse the call tree of the given function and generates a module that contains the primals and adjoints of all functions in the call tree.

Invocations:

1. `autodiff_ast`


#### `autodiff_ast`

The function [`autodiff_ast`](https://github.com/google/tangent/blob/v0.1.9/tangent/grad_util.py#L76) is the core of `grad`; it resolves the calls, performes the AD, and returns the AST.  Given the default parameters, the implementation simplifies into the following:

```python
def autodiff_ast(func, wrt, motion, mode, preserve_result, check_dims, verbose):
  node = annotate.resolve_calls(func)
  fence.validate(node, inspect.getsource(func))
  node = anf_.anf(node)
  if mode == 'reverse':
    node, required, stack = reverse_ad.reverse_ad(node.body[0], wrt,
                                                  preserve_result, check_dims)
    if motion != 'split':
      node = reverse_ad.joint(node)
  return node, required
```

Invocations:

1. `annotate.resolve_calls`
1. `anf.anf`
1. `reverse_ad.reverse_ad`
1. `reverse_ad.joint`


##### `annotate.resolve_calls`

The function [`resolve_calls`](https://github.com/google/tangent/blob/v0.1.9/tangent/annotate.py#L83) contains two lines:

```python
def resolve_calls(func):
  node = quoting.parse_function(func)
  ResolveCalls(func).visit(node)
  return node
```

where

- [`quoting.parse_function(fn)`](https://github.com/google/tangent/blob/v0.1.9/tangent/quoting.py#L81) is a shortcut to

  ```python
  return
    gast.ast_to_gast(
      ast.parse(
	    textwrap.dedent(
	      inspect.getsource(fn))))
  ```

  where `ast` is Python's standard library, and [`gast`](https://github.com/serge-sans-paille/gast) provides compatibility of `ast` of Python 2 and Python 2.

- [`ResolveCalls(func).visit(node)`](https://github.com/google/tangent/blob/v0.1.9/tangent/annotate.py#L33) traverses the AST of `func` and annotate each `Call` node a `"func"` attribute whose value is the AST node of the callee.


##### `anf.anf`

According to the comments of `anf.anf`, it is easier to derive the backward pass if we transform the forward pass into the [A-normal form](https://en.wikipedia.org/wiki/A-normal_form) (ANF).

In ANF, all arguments to a function must be *trivial*. That is, evaluation of each argument must halt immediately.  For example, the following expression

```
f(g(x), h(y))
```

has its A-normal form as

```
v0 = g(x)
v1 = h(y)
f(v0, v1)
```

where `v0` and `v1` are said *trivial* because they are direct values.


The class [`ANF`](https://github.com/google/tangent/blob/v0.1.9/tangent/anf.py#L49) changes the AST returned by [`resolve_calls`](https://github.com/google/tangent/blob/v0.1.9/tangent/annotate.py#L83) into ANF.  `ANF` is a subclass of [`transformers.TreeTransformer`](https://github.com/google/tangent/blob/v0.1.9/tangent/transformers.py#L26), which is in turn a subclass of `gast.NodeTransformer`, which is a subclass of `ast.NodeTransformer`.  Please refer to [this short tutorial](https://github.com/wangkuiyi/fluid/wiki/python-abstract-syntax-tree) for more information about NodeTransformer that is necessary before reading the class `ANF`.

The core of class `ANF` is the method [`ANF.trivialize(self, node)`](https://github.com/google/tangent/blob/v0.1.9/tangent/anf.py#L63), which is called by visit methods:

- `ANF.visit_Call` trivializes parameters of a function invocation before calling the function,
- `ANF.visit_BinOp` trivializes the two operands before invoking the operator,
- `ANF.visit_UnaryOp` trivializes the operand before invokding the operator.

The statements that computes the trivialized variables are prepended in the AST.  The name of trivialized variables, e.g., `v0` and `v1` in the above example, are generated by `tangent.naming`.




## Related Readings

- A-Normal Form: http://matt.might.net/articles/a-normalization
