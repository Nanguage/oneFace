# Wrap command line

Another way to use oneFace is to wrap a command line program.
From the perspective of implementation, it's a layer of wrapping
around the oneFace API. You can use a YAML configuration file to
describe the command line to be wrapped and the type, range and default
value of each parameter.

Here is an example YAML file:

```YAML
# example.yaml
# The name of your app
name: add

# The target command to be wraped.
# Use '{}' to mark all arguments.
command: python -c "print({a} + {b})" 

# List all argument's type and range
arguments:

  a:
    type: int
    range: [0, 10]

  b:
    type: int
    range: [-10, 10]
    default: 0

# Interface specific config
# These parameters will pass to the interface
qt_config:
  # qt related config
  run_once: false

dash_config:
  # Dash related config
  console_interval: 2000
```

You can generate this file to your working path, using:

```bash
$ python -m oneface.wrap_cli generate ./example.yaml
```

Then you can lanuch the application with:

```bash
$ python -m oneface.wrap_cli run example.yaml qt_gui  # or
$ python -m oneface.wrap_cli run example.yaml dash_app
```


## Flag insertion

Extra string can insert to the actually executed command when the
parameter is a `bool` type. It's useful when the command contains some
"Flag" parameters. For example:

```YAML
name: add

command: python {verbose} -c "print({a} + {b})" 

arguments:

  verbose:
    type: bool
    default: False
    true_insert: "-v"  # insert "-v" flag when verbose is True
    false_insert: ""

  a:
    type: int
    range: [0, 10]

  b:
    type: int
    range: [-10, 10]
    default: 0
```


## Configurations

You can modify the configuration related to
the specific interface([Qt](./qt_confs.md) and [Dash](./dash_confs.md)).
Using the corresponding fields, for example:

```YAML
qt_config:
  name: "my qt app"
  size: [300, 200]
  run_once: False

dash_config:
  host: 127.0.0.1
  port: 8989
  show_console: True
  console_interval: 2000
  init_run: True
```

And parameter related configrations should set to the corresponding argument fields.
For example:

```YAML
arguments:

  a:
    type: int
    range: [0, 10]
    interactive: True  # will let this argument interactive in dash app

```
