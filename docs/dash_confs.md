# Dash interface configs

## Hidden console

oneface dash provides a terminal for displaying operational status.
The `show_console` parameter is used to control whether it is displayed.

```Python
from oneface import one, Arg

@one
def bmi(name: str = "Tom",
        height: Arg[float, [100, 250]] = 160,
        weight: Arg[float, [0, 300]] = 50.0):
    BMI = weight / (height / 100) ** 2
    print(f"Hi {name}. Your BMI is: {BMI}")
    return BMI

bmi.dash_app(show_console=False)
```

Will not show the console.

## Console refresh interval

By default, the console is refreshed in 2 seconds (2000 microseconds).
`console_interval` can be used to set the refresh interval

```Python
bmi.dash_app(console_interval=1000)
```

Will set refresh interval to 1 second.

## Argument label

By default, argument label is the variable name. But it can be explicitly set by `text` parameter:

```Python
@one
def bmi(name: Arg(str, text="NAME"),  # explicitly label setting
        height: Arg(float, [100, 250]) = 160,
        weight: Arg(float, [0, 300]) = 50.0):
    BMI = weight / (height / 100) ** 2
    print(f"Hi {name}. Your BMI is: {BMI}")
    return BMI
```

## Init run

By default, it is not called until the user clicks the run button.
However, the initial call can be turned on by setting `init_run=True`:

```Python
bmi.dash_app(init_run=True)
```

This will cause the `bmi` function to be called once automatically at the end of app initialization.
In this case, all parameters need to have default values.

## Interactive parameter

Interactive parameters rerun the function each time the input is changed.
We can use `Arg`'s interactive to mark the interactive parameter, for example we mark `height` as interactive:

```Python
@one
def bmi(name: Arg(str) = "Tom",
        height: Arg(float, [100, 250], interactive=True) = 160,
        weight: Arg(float, [0, 300]) = 50.0):
    BMI = weight / (height / 100) ** 2
    print(f"Hi {name}. Your BMI is: {BMI}")
    return BMI
```

![interactive_arg_dash](./imgs/interactive_arg_dash.gif)

And, if you pass `interactive = True` to the `.dash_app` method, it will mark all parameters as interactive:

```Python
bmi.dash_app(interactive=True)
```

## Result show type

By default, the `result_show_type` is `'text'`, which means that the result will be displayed in text.
In addition, the results can also be presented in other forms:

### Download type

In many cases, the results of running a web application need to be downloaded as a file for the user.
You can set the `result_show_type='download'` for this purpose.
In this case, the target function should return the path to the result file:

```Python
from oneface import one, Arg

@one
def bmi(name: Arg(str) = "Tom",
        height: Arg(float, [100, 250], interactive=True) = 160,
        weight: Arg(float, [0, 300]) = 50.0):
    BMI = weight / (height / 100) ** 2
    out_path = f"./{name}_bmi.txt"
    with open(out_path, 'w') as fo:
        fo.write(f"Hi {name}. Your BMI is: {BMI}")
    return out_path

bmi.dash_app(result_show_type="download")
```

![download_res_dash](./imgs/download_res_dash.gif)

## Host and Port

Specify the app's host and port:

```Python
bmi.dash_app(host="0.0.0.0", port=9000)
```

## debug mode

The debug mode is useful for debugging errors, use `debug=True` to open it:

```Python
bmi.dash_app(debug=True)
```
