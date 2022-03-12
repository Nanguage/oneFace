import contextlib
import functools
import inspect
from io import StringIO
import os.path as osp
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from ansi2html import Ansi2HTMLConverter


HERE = osp.abspath(osp.dirname(__file__))


def app(func=None, **kwargs):
    if func is None:
        return functools.partial(app, **kwargs)
    return App(func, **kwargs)


class App(object):
    type_to_widget_constructor = {}
    convert_types = {}

    def __init__(self, func, name=None, debug=True):
        self.func = func
        self.name = name
        self.debug = debug
        self.input_names = None
        self.input_types = None
        self.result = None
        self.dash_app = self.get_dash_app()

    def get_layout(self):
        widgets, names, types = self.parse_args()
        self.input_names = names
        self.input_types = types
        layout = html.Div(children=[
            html.H3("Arguments"),
            *widgets,
            html.Br(),
            html.Button("Run", id="run-btn"),
            html.Div("", style={"height": "20px"}),
            html.H3("Console"),
            html.Div("", style={"height": "20px"}),
            dcc.Interval(
                id="console-interval",
                interval=1000, n_intervals=0),
            html.Iframe(id="console-out", style={"width": "100%"}),
            html.H3("Result"),
            html.Div("", id="out")
        ], style={
            'width': "60%",
            'min-width': "400px",
            'max-width': "800px",
            'margin': "auto",
        })
        return layout

    def parse_args(self):
        from oneface.core import Arg
        sig = inspect.signature(self.func)
        widgets, names, types = [], [], []
        for n, p in sig.parameters.items():
            ann = p.annotation
            if not isinstance(ann, Arg):
                continue
            constructor = self.type_to_widget_constructor[ann.type.__name__]
            widgets.append(constructor(n, ann.range))
            names.append(n)
            types.append(ann.type)
        return widgets, names, types

    def get_run_callback_decorator(self, app):
        inputs = [Input("run-btn", 'n_clicks')]
        inputs += [State(f"input-{n}", "value") for n in self.input_names]
        output = Output("out", "children")
        deco = app.callback(output, *inputs)
        return deco

    def get_dash_app(self):
        name = self.name or self.func.__name__
        css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = Dash(name, external_stylesheets=css)
        app.layout = self.get_layout()
        console_buffer = StringIO()

        @self.get_run_callback_decorator(app)
        def run(n_clicks, *args):
            if n_clicks is None:
                raise PreventUpdate
            kwargs = dict(zip(self.input_names, args))
            for i, (k, v) in enumerate(kwargs.items()):
                input_type = self.input_types[i]
                tp_name = input_type.__name__
                if tp_name in self.convert_types:
                    kwargs[k] = self.convert_types[tp_name](v)
            with contextlib.redirect_stdout(console_buffer):
                self.result = self.func(**kwargs)
            return self.result

        @app.callback(
            Output("console-out", "srcDoc"),
            Input("console-interval", "n_intervals"))
        def update_console(n):
            conv = Ansi2HTMLConverter()
            console_buffer.seek(0)
            lines = console_buffer.readlines()
            return conv.convert("".join(lines))

        return app

    @classmethod
    def register_widget(cls, type, widget_constructor):
        cls.type_to_widget_constructor[type.__name__] = widget_constructor

    @classmethod
    def register_type_convert(cls, type, converter=None):
        if converter is None:
            converter = type
        cls.convert_types[type.__name__] = converter

    def __call__(self):
        self.dash_app.run_server(debug=self.debug)


def number_input_widget(name, range, step=None):
    return html.Div([
        f"{name}: ",
        dcc.Slider(
            range[0], range[1], step,
            id=f"input-{name}", value=range[0])
    ])


def dropdown_widget(name, range):
    return html.Div([
        f"{name}: ",
        dcc.Dropdown(range, id=f"input-{name}", value=range[0])
    ])


App.register_widget(
    int,
    functools.partial(number_input_widget, step=1))
App.register_widget(
    float,
    functools.partial(number_input_widget, step=None))
App.register_type_convert(float)
App.register_widget(str, dropdown_widget)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "./")
    from oneface.core import one, Arg

    @app
    @one
    def func(a: Arg(int, [0, 10]),
             b: Arg(float, [0, 10]),
             c: Arg(str, ["a", "b", "c"])):  # noqa
        print(c)
        return a + b

    func()
