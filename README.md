# oneFace

oneFace is a library for automatically generating multiple interfaces(CLI, GUI, WebGUI) from a callable Python object.

<p>
    <a href="https://github.com/Nanguage/oneFace/actions/workflows/build_and_test.yml">
        <img src="https://github.com/Nanguage/oneFace/actions/workflows/build_and_test.yml/badge.svg" alt="Build Status">
    </a>
    <a href="https://app.codecov.io/gh/Nanguage/oneFace">
        <img src="https://codecov.io/gh/Nanguage/oneFace/branch/master/graph/badge.svg" alt="codecov">
    </a>
    <a href="https://nanguage.github.io/oneFace/">
    	<img src="https://readthedocs.org/projects/ansicolortags/badge/?version=latest" alt="Documentation">
    </a>
</p>


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
| ![CLI](./docs/imgs/bmi_cli.png) | ![Qt](./docs/imgs/bmi_qt.png) | ![Dash](./docs/imgs/bmi_dash.png) |