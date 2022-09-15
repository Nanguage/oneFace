<div align="center">

<img src="./docs/imgs/logo.png">

<p> oneFace is a Python library for automatically generating multiple interfaces(CLI, GUI, WebGUI) from a callable Python object or a command line program. </p>

<p>
    <a href="https://github.com/Nanguage/oneFace/actions/workflows/build_and_test.yml">
        <img src="https://github.com/Nanguage/oneFace/actions/workflows/build_and_test.yml/badge.svg" alt="Build Status">
    </a>
    <a href="https://app.codecov.io/gh/Nanguage/oneFace">
        <img src="https://codecov.io/gh/Nanguage/oneFace/branch/master/graph/badge.svg" alt="codecov">
    </a>
    <a href="https://oneface.readthedocs.io/en/latest/">
    	<img src="https://readthedocs.org/projects/oneface/badge/?version=latest" alt="Documentation">
    </a>
  <a href="https://pypi.org/project/oneFace/">
    <img src="https://img.shields.io/pypi/v/oneface.svg" alt="Install with PyPi" />
  </a>
</p>

</div>


oneFace is an easy way to create interfaces.

In Python, just decorate your function and mark the type and range of the arguments:

```Python
from oneface import one, Arg

@one
def bmi(name: str,
        height: Arg[float, [100, 250]] = 160,
        weight: Arg[float, [0, 300]] = 50.0):
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

### Wrap command line program

Or you can wrap a command line using a config file:

```yaml
# add.yaml
# This is a demo app, use for add two numbers.
name: add

# mark the arguments in command with: {}
command: python {verbose} -c 'print({a} + {b})'

arguments:
  # describe the type and range of your arguments
  verbose:
    type: bool
    default: False
    true_insert: "-v"  # insert '-v' to the command when the value is true
    false_insert: ""
  a:
    type: float
    range: [-100.0, 100.0]
    default: 0.0
  b:
    type: float
    range: [-100.0, 100.0]
    default: 10.0
```

Lanuch the app with:

```Bash
$ python -m oneface.wrap_cli run add.yaml dash_app  # run Dash app, or:
$ python -m oneface.wrap_cli run add.yaml qt_gui  # run Qt GUI app
```

## Features

+ Generate CLI, Qt GUI, Dash Web app from a python function or a command line.
+ Automatically check the type and range of input parameters and pretty print them.
+ Easy extension of parameter types and GUI widgets.

Detail usage see the [documentation](https://oneface.readthedocs.io/en/latest/).

## Installation

To install oneFace with complete dependency:

```
$ pip install oneface[all]
```

Or install with just qt or dash dependency:

```
$ pip install oneface[qt]  # qt
$ pip install oneface[dash]  # dash
```
