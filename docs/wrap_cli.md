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
