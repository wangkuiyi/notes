# Python's Abstract Syntax Tree

## AST Libraries

Python provides the built-in module for Abstract Syntax Tree parsing, visiting, and transformation.  For Python 2.x, the document is at https://docs.python.org/2/library/ast.html; for Python 3.x, it is at https://docs.python.org/3/library/ast.html.  [`gast`](https://github.com/serge-sans-paille/gast) provides compatibility between these two versions. `gast` doesn't have a complete document, but in practice, it is alright to refer to the native `ast`'s documents.

## An Example

The following example shows how to parse the `sample.py` file into AST and dump the AST:

```python
import ast
tree = ast.parse(open('sample.py').read())
ast.dump(tree)
```

Suppose that `sample.py` is as follows:

```python
def f(x):
    def a(x):
        return x * x
    return a(x)
```

The dump would look like the following

```python
Module(
    body=[
        FunctionDef(name='f',
                    args=arguments(args=[Name(id='x', ctx=Param())],
                                   vararg=None,
                                   kwarg=None,
                                   defaults=[]),
                    body=[
                        FunctionDef(name='a',
                                    args=arguments(args=[Name(id='x', ctx=Param())],
                                                   vararg=None,
                                                   kwarg=None,
                                                   defaults=[]),
                                    body=[Return(value=BinOp(left=Name(id='x', ctx=Load()),
                                                             op=Mult(),
                                                             right=Name(id='x', ctx=Load())))],
                                    decorator_list=[]),
                        Return(
                            value=Call(func=Name(id='a', ctx=Load()),
                                       args=[Name(id='x', ctx=Load())],
                                       keywords=[],
                                       starargs=None,
                                       kwargs=None))],
                    decorator_list=[])])
```

## Concepts

1. Tree and Node

   An AST is a tree, and a tree is composed of nodes.  In the above example, `Module`, `FunctionDef`, `Return` are all nodes in the AST.

1. Node Classes

   In the `ast` module, each AST node is defined as a Python class, for example, `ast.Module`, `ast.FunctionDef`, and `ast.Return`.

1. Node Categorization

   Some node classes are of the same category.  For example, `FunctionDef`, `ClassDef`, and `Return` are all *statements*, so they are all derived from class `ast.stmt`.

1. The Abstract Grammar

   The formal definition of these categorization is the [*abstract grammar*](https://docs.python.org/2/library/ast.html#abstract-grammar) of Python the language, where it states:

   ```
   stmt = FunctionDef(identifier name, arguments args,
                      stmt* body, expr* decorator_list)
         | ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
         | Return(expr? value)
         ...
   ```

1. Concrete Node Classes

   In each grammar rule, the left-hand side class is *abstract*, the right-hand side class is *concrete*.

1. Fields

   Each concrete class has an attribute `_fields`, which gives the names of all child nodes.  From the above example, we can see that `ast.BinOp._fields` contains three fields: `left`, `op`, and `right`.


## Traversal

### Walking

The function `ast.walk(node)` returns a generator that allows us to walk nodes in no specified order.  For example:

```python
for node in ast.walk(root):
    if isinstance(node, ast.Name):
        print(node)
```


### `NodeVisitor`

An upgrading of `ast.walk` is the class `ast.NodeVisitor`, which has two methods

1. `NodeVisitor.visit(node)`, and
1. `NodeVisitor.generic_visit(node)`.

As `ast.NodeVisitor` is supposed to work as the base class; we could add more methods, for example, `visit_Class` and `visit_FunctionDef`.  The function `visit` would traverse the tree and calls a method, whose name matches the node class, on each node.  If for some node classes, there are no corresponding methods, `visit` would call `generic_visit`.

### `NodeTransformer`

`NodeVisitor` doesn't change the AST.  If we are going to change the AST, we should use `NodeTransformer`, which is a subclass of `NodeVisitor`.  `NodeTransformer.visit` will replace each node by the return value from the visit method.
