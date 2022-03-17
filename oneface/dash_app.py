import contextlib
import functools
import inspect
from io import StringIO
import os.path as osp

from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from ansi2html import Ansi2HTMLConverter
import visdcc

from oneface.types import (Selection, SubSet, InputPath, OutputPath)


HERE = osp.abspath(osp.dirname(__file__))


def app(func=None, **kwargs):
    if func is None:
        return functools.partial(app, **kwargs)
    return App(func, **kwargs)


class App(object):
    type_to_widget_constructor = {}
    convert_types = {}

    def __init__(
            self, func, name=None,
            show_console=True,
            conosole_interval=2000,
            interactive=False, init_run=False,
            result_show_type="text",
            **server_args):
        self.func = func
        self.name = name
        self.show_console = show_console
        self.console_interval = conosole_interval
        self.interactive = interactive
        self.init_run = init_run
        self.result_show_type = result_show_type
        self.server_args = server_args
        self.input_names = None
        self.input_types = None
        self.input_attrs = None
        self.result = None
        self.dash_app = self.get_dash_app()

    def get_layout(self):
        widgets, names, types, attrs = self.parse_args()
        self.input_names = names
        self.input_types = types
        self.input_attrs = attrs
        sub_nodes = [
            html.H3("Arguments"),
            *widgets,
            html.Br(),
            html.Button("Run", id="run-btn"),
            html.Div("", style={"height": "20px"}),
        ]
        if self.show_console:
            sub_nodes += self.get_console_layout()
        sub_nodes += self.get_result_layout()
        layout = html.Div(children=sub_nodes, style={
            'width': "60%",
            'min-width': "400px",
            'max-width': "800px",
            'margin': "auto",
        })
        return layout

    def get_console_layout(self):
        return [
            html.H3("Console"),
            html.Div("", style={"height": "20px"}),
            dcc.Interval(
                id="console-interval",
                interval=self.console_interval, n_intervals=0),
            html.Iframe(id="console-out", style={
                "width": "100%",
                "max-width": "100%",
                "height": "400px",
                "resize": "both"
            }),
            visdcc.Run_js(id="jsscroll", run="")
        ]

    def get_result_layout(self):
        layout = [
            html.H3("Result"),
        ]
        if self.result_show_type == "text":
            layout += [
                html.Div("", id="out"),
            ]
        elif self.result_show_type == "download":
            layout += [
                html.Div("", id="out", style={'display': 'none'}),
                html.Button("Download Result", id="res-download-btn"),
                dcc.Download(id="res-download-index")
            ]
        return layout

    def parse_args(self):
        from oneface.core import Arg
        sig = inspect.signature(self.func)
        widgets, names, types, attrs = [], [], [], []
        for n, p in sig.parameters.items():
            ann = p.annotation
            if not isinstance(ann, Arg):
                continue
            constructor = self.type_to_widget_constructor[ann.type.__name__]
            default = None if p.default is inspect._empty else p.default
            attr = ann.kwargs
            widget = constructor(
                n, ann.range, default, attrs=attr).widget
            widgets.append(widget)
            names.append(n)
            types.append(ann.type)
            attrs.append(attr)
        return widgets, names, types, attrs

    def get_run_callback_decorator(self, app):
        inputs = [Input("run-btn", 'n_clicks')]
        for i, n in enumerate(self.input_names):
            is_interactive = (
                self.interactive or
                (self.input_attrs[i].get('interactive') is True)
            )
            id_ = f"input-{n}"
            if is_interactive:
                input = Input(id_, "value")
            else:
                input = State(id_, "value")
            inputs.append(input)
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
            if (not self.init_run) and (n_clicks is None):
                raise PreventUpdate
            kwargs = dict(zip(self.input_names, args))
            for i, (k, v) in enumerate(kwargs.items()):
                input_type = self.input_types[i]
                tp_name = input_type.__name__
                if tp_name in self.convert_types:
                    kwargs[k] = self.convert_types[tp_name](v)
            with contextlib.redirect_stdout(console_buffer), \
                 contextlib.redirect_stderr(console_buffer):
                self.result = self.func(**kwargs)
            return self.result

        if self.show_console:
            self.add_console_callbacks(app, console_buffer)

        if self.result_show_type == "download":
            self.add_download_callbacks(app)

        return app

    def add_console_callbacks(self, app, console_buffer):
        @app.callback(
            Output("console-out", "srcDoc"),
            Input("console-interval", "n_intervals"))
        def update_console(n):
            conv = Ansi2HTMLConverter()
            console_buffer.seek(0)
            lines = console_buffer.readlines()
            html_ = conv.convert("".join(lines))
            return html_

        doc_cache = None

        @app.callback(
            Output('jsscroll', 'run'),
            Input('console-out', 'srcDoc'))
        def scroll(doc):
            scroll_cmd = """
            var out = document.getElementById('console-out');
            out.contentWindow.scrollTo(0, 999999999);
            """
            nonlocal doc_cache
            if doc == doc_cache:
                cmd = ""
            else:
                cmd = scroll_cmd
            doc_cache = doc
            return cmd

    def add_download_callbacks(self, app):
        @app.callback(
            Output("res-download-index", "data"),
            Input("res-download-btn", "n_clicks"),
            prevent_initial_call=True)
        def send_file(n_clicks):
            return dcc.send_file(self.result)

    @classmethod
    def register_widget(cls, type, widget_constructor):
        cls.type_to_widget_constructor[type.__name__] = widget_constructor

    @classmethod
    def register_type_convert(cls, type, converter=None):
        if converter is None:
            converter = type
        cls.convert_types[type.__name__] = converter

    def __call__(self):
        self.dash_app.run_server(**self.server_args)


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
        return dcc.Input(
            min=self.range[0], max=self.range[1], type="number", step=1,
            value=(self.default or self.range[0]), style={
                'width': "100%",
            }
        )


class FloatInputItem(InputItem):
    def get_input(self):
        return dcc.Slider(
            self.range[0], self.range[1], step=None,
            value=(self.default or self.range[0])
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
        return dcc.RadioItems(
            ["True", "False"],
            value=(str(self.default) or "True")
        )


class DropdownInputItem(InputItem):
    def get_input(self):
        return dcc.Dropdown(
            self.range,
            value=(self.default or range[0])
        )


class MultiDropdownInputItem(InputItem):
    def get_input(self):
        return dcc.Dropdown(
            self.range,
            value=(self.default or range[0]), multi=True
        )


App.register_widget(int, IntInputItem)
App.register_widget(float, FloatInputItem)
App.register_type_convert(float)
App.register_widget(str, StrInputItem)
App.register_widget(bool, BoolInputItem)
App.register_type_convert(bool, lambda s: s == "True")
App.register_widget(Selection, DropdownInputItem)
App.register_widget(SubSet, MultiDropdownInputItem)
App.register_widget(InputPath, StrInputItem)
App.register_widget(OutputPath, StrInputItem)
