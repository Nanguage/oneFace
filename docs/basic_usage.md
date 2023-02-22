
# Basic Usage

Using `one` decorate the function, and use `Val` mark type and range of the arguments.

```Python
from oneface import one, Val

@one
def print_person(name: str, age: Val[int, [0, 120]]):
    print(f"{name} is {age} years old.")
```

**Note**: `Val(type, range)` is same to `Val[type, range]`.

```Python
# This is same to the previous defination
@one
def print_person(name: str, age: Val(int, [0, 120])):
    print(f"{name} is {age} years old.")
```

You can also mark arguments using decorators in [`funcdesc`](https://github.com/Nanguage/funcdesc):

```Python
from oneface import one
from funcdesc import mark_input

@one
@mark_input("age", range=[0, 120])
def print_person(name: str, age: int):
    print(f"{name} is {age} years old.")

```

This code achieves the same effect as the previous example, and you can refer to the [`funcdesc`](https://github.com/Nanguage/funcdesc) for more information about the `mark_input` decorator.


## Type and range checking

Functions decorated with `one` will automatically check the type and range of input parameters:

```Python
>>> print_person("Tom", 20)
Run: print_person
Arguments table:

 Argument  Type           Range     InputVal  InputType
 name      <class 'str'>  None      Tom       <class 'str'>
 age       <class 'int'>  [0, 120]  20        <class 'int'>

Tom is 20 years old.
```

If we pass parameters with incorrect type or range, it will raise an exception:

```Python
>>> print_person(100, -20)  # incorrect input type and range
Run: print_person
Arguments table:

 Argument  Type           Range     InputVal  InputType
 name      <class 'str'>  None      100       <class 'int'>
 age       <class 'int'>  [0, 120]  -20       <class 'int'>

Traceback (most recent call last):
  File "C:\Users\Nangu\Desktop\oneFace\tmp\test1.py", line 9, in <module>
    print_person(100, -20)
  File "C:\Users\Nangu\miniconda3\envs\oneface\lib\site-packages\funcdesc\guard.py", line 46, in __call__
    self.check_inputs(pass_in, errors)
  File "C:\Users\Nangu\Desktop\oneFace\oneface\check.py", line 86, in check_inputs
    raise CheckError(errors)
funcdesc.guard.CheckError: [TypeError("Value 100 is not in valid type(<class 'str'>)"), ValueError('Value -20 is not in a valid range([0, 120]).')]
```

### Turn-off arguments print

By default, oneface will pretty print the input arguments with a table. It can be turned off with the `print_args` parameter:

```Python
@one(print_args=False)
def print_person(name: str, age: Val[int, [0, 120]]):
    print(f"{name} is {age} years old.")

>>> print_person("Tom", 20)
Tom is 20 years old.
```

## Create interfaces

Create a python module `print_person.py`:

```Python
from oneface import one, Arg

@one
def print_person(name: str, age: Arg[int, [0, 120]]):
    print(f"{name} is {age} years old.")

print_person.cli()
```

This will create a Command Line Interface for `print_person` function. You can call this function in the Shell:

```Bash
$ python print_person.py Tom 20
Run: print_person
Arguments table:

 Argument  Type           Range     InputVal  InputType
 name      <class 'str'>  None      Tom       <class 'str'>
 age       <class 'int'>  [0, 120]  20        <class 'int'>

Tom is 20 years old.
```

If you want change to another interface, just change the `.cli()` to `.qt_gui()` or `.dash_app()`.
Then run this file again:

```
$ python print_person.py
```

You will got the Qt gui:

![print_person_qt](imgs/print_person_qt.png)

Or Dash web app:
![print_person_dash](imgs/print_person_dash.png)
