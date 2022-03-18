# Built-in argument types

oneFace support the following types:

| Type | Example | Type check | Range check | Description |
| ---- | ------- | ---------- | ----------- | ----------- |
| str  | `Arg(str)` | `True` | `False` | String input. |
| int | `Arg(int, [0, 10])` | `True` | `True` | Int input. |
| float | `Arg(float, [0, 1])` | `True` | `True` | Float input. |
| bool | `Arg(bool)` | `True` | `False` | Bool input. | 
| Selection | `Arg(Selection, ["a", "b", "c"])` | `False` | `True` | Input should be a element of the range. |
| SubSet | `Arg(SubSet, ["a", "b", "c"])` | `False` | `True` | Input should be a subset of the range. |
| InputPath | `Arg(InputPath)` | `True` | `True` | Input should be an exist file path(`str` or `pathlib.Path`). |
| OutPath | `Arg(OutputPath)` | `True` | `False` | Input should be a file path(`str` or `pathlib.Path`) |

This example show all built-in types, name as `builtin_example.py`:
