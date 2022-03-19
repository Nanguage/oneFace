# Type Extension

You can easily extend the argument types in oneFace.

## Registration of type and range check

For example you have a custom `Person` class:

```Python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

### Register type check

```Python
Arg.register_type_check(Person)
```

This will allow oneface to check the type of the input parameter to make sure it is an instance of `Person`:

```Python
@one
def print_person(person: Arg(Person)):
    print(f"{person.name} is {person.age} years old.")

>>> print_person(["Tom", 10])  # Incorrect input type
Run: print_person
Arguments table:

 Argument  Type                       Range  InputVal     InputType
 person    <class '__main__.Person'>  None   ['Tom', 10]  <class 'list'>

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Nangu\Desktop\oneFace\oneface\core.py", line 117, in __call__
    raise ArgsCheckError(errors)
oneface.core.ArgsCheckError: [TypeError("Input value ['Tom', 10] is not in valid type(<class '__main__.Person'>)")]
```

`Arg.register_type_check` also allow you to define a custom type checker, for example:

```Python
def check_person_type(val, tp):
    return (
        isinstance(val, tp) and
        isinstance(val.name, str) and
        isinstance(val.age, int)
    )

Arg.register_type_check(Person, check_person_type)
```

This will not only check if the input value is an instance of `Preson`, but also ensure that its attributes are of the correct type:

```Python
>>> print_person(Person("Tom", "10"))  # Incorrect age type
Run: print_person
Arguments table:

 Argument  Type                       Range  InputVal                       InputType
 person    <class '__main__.Person'>  None   <__main__.Person object at     <class '__main__.Person'>
                                             0x000001FBEC3BBCC8>

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Nangu\Desktop\oneFace\oneface\core.py", line 117, in __call__
    raise ArgsCheckError(errors)
oneface.core.ArgsCheckError: [TypeError("Input value <__main__.Person object at 0x000001FBEC3BBCC8> is not in valid type(<class '__main__.Person'>)")]
```

### Register range check

You can also register a range check for it, for example, to limit the age to a certain range:

```Python
Arg.register_range_check(Person, lambda val, range: range[0] <= val.age <= range[1])
```

Mark the range in argument annotation:

```Python
@one
def print_person(person: Arg(Person, [0, 100])):
    print(f"{person.name} is {person.age} years old.")
```

This will limit the person's age in the range of 0~100:

```Python
>>> print_person(Person("Tom", -10))
Run: print_person
Arguments table:

 Argument  Type                       Range     InputVal                    InputType
 person    <class '__main__.Person'>  [0, 100]  <__main__.Person object at  <class '__main__.Person'>
                                                0x000001FBEC3FC248>

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Nangu\Desktop\oneFace\oneface\core.py", line 117, in __call__
    raise ArgsCheckError(errors)
oneface.core.ArgsCheckError: [ValueError('Input value <__main__.Person object at 0x000001FBEC3FC248> is not in a valid range.')]
```

