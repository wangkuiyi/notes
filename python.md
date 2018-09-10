## `__new__` and `__init__`

`__new__` creates and returns an instance of the class.

`__init__` initializes the new-ed instance.

To enable the overriding of `__new__`, the class, if defined in Python 2.x, must inherits from the base class `object`.  
For more information, please refer [this article](https://spyhce.com/blog/understanding-new-and-init).

## metaclass and base class

Metaclass is not the base class, because when we call `obj.some_method`, Python doesn't looks for the method named `some_method` in metaclasses, but it does for base classes. For more details, please refer to [this answer](https://stackoverflow.com/a/17802762).

A metaclass is specified with the `__metaclass__` property:

```python
class A(object):
    __metaclass__ = AMetaClass
```

Base classes are specified at the definition:

```python
class A(BaseClass1, BaseClass2, ...):
```
