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

1. [`autodiff_tree`](#autodiff_tree)
1. `_create_joint`
1. `optimization.optimize`
1. `compile.compile_file`


## `autodiff_tree`

The function [`autodiff_tree`](https://github.com/google/tangent/blob/v0.1.9/tangent/grad_util.py#L114) traverse the call tree of the given function and generates a module that contains the primals and adjoints of all functions in the call tree.

```python
def autodiff_tree(func, wrt, motion, mode, preserve_result, check_dims,
                  verbose):
  # Imported here to avoid circular imports
  import tangent
  namespace = {'tangent': tangent, 'numpy': numpy}

  done = set()
  final = gast.Module(body=[])
  namespace.update(six.get_function_globals(func))

  node, required = autodiff_ast(func, wrt, motion, mode, preserve_result,
                                check_dims, verbose)
  final.body.extend(node.body)

  to_do = set(required)
  while to_do:
    func, wrt = to_do.pop()
    namespace.update(six.get_function_globals(func))

    node, required = autodiff_ast(
        func=func,
        wrt=wrt,
        motion='split',
        mode=mode,
        preserve_result=True,
        check_dims=False,
        verbose=verbose)

    final.body.extend(node.body)
    done.add((func, wrt))
    to_do.update(required)
    to_do -= done

  return final, namespace
```

It differentiate the given function `func` and all functions it calls, plus functions defined in `tangent` and `numpy`.  This [animation](https://raw.githubusercontent.com/google/tangent/master/docs/sct-ad-subroutine.gif) shows how function calls are handled in Tangent -- each callee (`mul`) is transformed into the primal (`pri_mul_`) and the adjoint (`dmul_dab`) in the `split` motion, which is why that the second call to `autodiff_ast` in the above code snippet has the parameter `motion='split'`.

Invocations:

1. [`autodiff_ast`](#autodiff_set)


## `autodiff_ast`

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

1. [`annotate.resolve_calls`](#annotateresolve_calls)
1. [`anf.anf`](#anfanf)
1. [`reverse_ad.reverse_ad`](#reverse_adreverse_ad)
1. `reverse_ad.joint`


## `annotate.resolve_calls`

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


## `anf.anf`

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


The class [`ANF`](https://github.com/google/tangent/blob/v0.1.9/tangent/anf.py#L49) changes the AST returned by [`resolve_calls`](https://github.com/google/tangent/blob/v0.1.9/tangent/annotate.py#L83) into ANF.  `ANF` is a subclass of [`transformers.TreeTransformer`](https://github.com/google/tangent/blob/v0.1.9/tangent/transformers.py#L26), which is in turn a subclass of `gast.NodeTransformer`, which is a subclass of `ast.NodeTransformer`.  Please refer to [this short tutorial](https://github.com/wangkuiyi/notes/blob/master/python-ast.md) for more information about NodeTransformer that is necessary before reading the class `ANF`.

The core of class `ANF` is the method [`ANF.trivialize(self, node)`](https://github.com/google/tangent/blob/v0.1.9/tangent/anf.py#L63), which is called by visit methods:

- `ANF.visit_Call` trivializes parameters of a function invocation before calling the function,
- `ANF.visit_BinOp` trivializes the two operands before invoking the operator,
- `ANF.visit_UnaryOp` trivializes the operand before invokding the operator.

The statements that computes the trivialized variables are prepended in the AST.  The name of trivialized variables, e.g., `v0` and `v1` in the above example, are generated by `tangent.naming`.



## `reverse_ad.reverse_ad`

```python
def reverse_ad(node, wrt, preserve_result, check_dims):
  if not isinstance(node, gast.FunctionDef):
    raise TypeError
  # Activity analysis
  cfg.forward(node, cfg.Active(wrt))

  ad = ReverseAD(wrt, preserve_result, check_dims)
  pri, adj = ad.visit(node)
  mod = gast.Module(body=[pri, adj])
  mod = annotate.find_stacks(mod)
  return mod, ad.required, ad.stack
```

Invocations:

1. [`cfg.Active`](cfgActive)
1. [`cfg.forward`](cfgforward)

where "cfg" stands for control-flow graph.


## `cfg.Active`

`Active` is a subclass of `cfg.Forward`. There are more such kind of subclasses:

1. `cfg.Active` finds all variables whose value possibly depend on a given set of arguments.
1. `cfg.Defined` annotes each statement with a set of variables which are guaranteed to be defined at that point.
1. `cfg.ReachingDefinitions` annotes each statement with a set of (variable, definition) pairs.


## `cfg.forward`

The function `cfg.forward` builds a CFG for each function definition and analyze the CFG.

```python
def forward(node, analysis):
  for succ in gast.walk(node):
    if isinstance(succ, gast.FunctionDef):
      cfg_obj = CFG.build_cfg(succ)
      analysis.visit(cfg_obj.entry)
  return node
```

where `analysis` must be an instance of a `cfg.Forward` subclass.

Invocations:

1. [`CFG.build_cfg`](#cfgbuild_cfg]
1. `Forward.visit`


## `CFG.build_cfg`

The class `CFG` represents the control-flow graph from the AST of a function definition.  Each node in this graph is represented by an instance of [`cfg.Node`](https://github.com/google/tangent/blob/v0.1.9/tangent/cfg.py#L33), which contains

1. `self.value`: an AST node
1. `self.prev`: a set of previous nodes
1. `self.next`: a set of successive nodes

The `CFG.build_cfg` class methods builds the `CFG` in the following steps:

1. Initialization:

   - the *entry* node, whose `self.value` is the `ast.arguments` field in the input `ast.FunctionDef` node.
   - the list of search boundary, *head*, which is initialized to `[entry]`.

1. Follow the statements:

   - If the current statement is NOT a [control-flow](https://github.com/google/tangent/blob/v0.1.9/tangent/grammar.py#L20), calls `CFG.set_head` to
     1. creates a `CFG.Node` of this statement,
	 1. makes it the successive of all head nodes, and
	 1. reset head list to contain this node.
   - Otherwise, it calls `CFG.visit` with this control-flow node. (Please be aware that `CFG` is a subclass of `gast.NodeVisitor`.)
     1. Given a `if` statement in the following form:
	    ```
		if test:
		    statement_1
	    else:
		    statement_2
		statement_3
		```
		the generated local CFG is:
		```
		test --> statement_1 --> statement_3
		     \-> statement_2 /
		```
	 1. Given a `while` statement with a break and a continue in a `if` statement
	    ```
		while test:
		  stmt_1
		  if cond_c:
		    continue
		  stmt_2
		  if cond_b:
		    break
		  stmt_3
		else:
		  stmt_4
	    stmt_5
	    ```
		the generated local CFG is like
		```
		   ___________________________________________________________________________
		  /                                                            _______________\__________
		 ↑                                                            /                \         \
		 ↑                                                           ↑                  ↓         ↓
		test -> stmt_1 -> cond_c -> continue -> stmt_2 -> cond_b -> break -> stmt_3 -> stmt_4 -> stmt_5
		↑  ↑                          ↓                                        ↓
		|  \-------------------------/                                        /
		 \-------------------------------------------------------------------/
		```
		Please be aware that there could be no `continue` or `break` in the `else` clause of `while`.
 	 1. The CFG of `for` is similar to that of `while` except that `for` doesn't have the `else` clause.
     1. The CFG of `try` starts from the body and to each of the handlers and the else clause, then all handlers and the else clause connect to the final body.

1. Add the special node whose value is `None` as the exit node.

   Question: it seems no special handling of the `return` statement, so only the last statement in the function definition connects to the exit node.

1. Call `backlink` which sets `CFG.Node.prev` links according to the `CFG.Node.next` links set up by the `set_head` function.

## Related Readings

- A-Normal Form: http://matt.might.net/articles/a-normalization
