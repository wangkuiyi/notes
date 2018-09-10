## `__new__` and `__init__`

`__new__` creates and returns an instance of the class.

`__init__` initializes the new-ed instance.

To enable the overriding of `__new__`, the class, if defined in Python 2.x, must inherits from the base class `object`.  
For more information, please refer [this article](https://spyhce.com/blog/understanding-new-and-init).
