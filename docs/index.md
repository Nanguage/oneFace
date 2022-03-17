# oneFace

oneFace is a Python library for automatically generating multiple interfaces(CLI, GUI, WebGUI) from a callable Python object.

```Python
from oneface import one, Arg

@one
def bmi(name: Arg(str),
        height: Arg(float, [100, 250]) = 160,
        weight: Arg(float, [0, 300]) = 50.0):
    BMI = weight / (height / 100) ** 2
    print(f"Hi {name}. Your BMI is: {BMI}")
    return BMI


# run cli
bmi.cli()
# or run qt_gui
bmi.qt_gui()
# or run dash web app
bmi.dash_app()
```

These code will generate the following interfaces:

|  CLI | Qt | Dash |
| ---- | -- | ---- |
| ![CLI](imgs/bmi_cli.png) | ![Qt](imgs/bmi_qt.png) | ![Dash](imgs/bmi_dash.png) |