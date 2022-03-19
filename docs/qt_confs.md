# Qt interface configs

## Window name

By default the window name is the name of the function, but it can be changed by `name` parameter of `.qt_gui` method:

```Python
from oneface import one, Arg

@one
def bmi(name: Arg(str),
        height: Arg(float, [100, 250]) = 160,
        weight: Arg(float, [0, 300]) = 50.0):
    BMI = weight / (height / 100) ** 2
    print(f"Hi {name}. Your BMI is: {BMI}")
    return BMI

bmi.qt_gui(name="BMI calculator")
```

![rename_example_qt](./imgs/rename_example_qt.png)

## Run multiple times

By default, oneface Qt interface run only once then exit, when click the run button.

![run_once](./imgs/run_once.gif)

You can use the `run_once=False` to make it run multiple times:

```
bmi.qt_gui(run_once=False)
```

![run_once](./imgs/run_not_once.gif)
