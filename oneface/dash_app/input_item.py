from dash import dcc, html


class InputItem(object):
    def __init__(self, name, range, default, attrs=None):
        self.name = name
        self.range = range
        self.default = default
        self.attrs = attrs
        self.input = self.get_input()
        self.input.id = f"input-{name}"
        self.widget = self.get_widget()

    def get_input(self):
        pass

    def get_widget(self):
        label = self.attrs.get("text", self.name)
        return html.Div([
            html.Div(f"{label}: ", style={
                "margin-top": "10px",
                "font-size": "20px",
            }),
            self.input
        ])


class IntInputItem(InputItem):
    def get_input(self):
        _range = self.range or [0, 100]
        _default = _range[0] if (self.default is None) else self.default
        return dcc.Input(
            min=_range[0], max=_range[1], type="number", step=1,
            value=_default, style={
                'width': "100%",
            }
        )


class FloatInputItem(InputItem):
    def get_input(self):
        _range = self.range or [0, 100]
        _default = _range[0] if (self.default is None) else self.default
        return dcc.Slider(
            _range[0], _range[1], step=None,
            value=_default,
        )


class StrInputItem(InputItem):
    def get_input(self):
        return dcc.Input(
            placeholder="Enter a value...",
            type="text",
            value=(self.default or ""),
            style={
                "width": "100%",
                "height": "40px",
                "margin": "5px",
                "font-size": "20px",
            }
        )


class BoolInputItem(InputItem):
    def get_input(self):
        _default = True if self.default is None else self.default
        return dcc.RadioItems(
            ["True", "False"],
            value=str(_default)
        )


class DropdownInputItem(InputItem):
    def get_input(self):
        return dcc.Dropdown(
            self.range,
            value=(self.default or self.range[0])
        )


class MultiDropdownInputItem(InputItem):
    def get_input(self):
        return dcc.Dropdown(
            self.range,
            value=(self.default or self.range[0]), multi=True
        )
