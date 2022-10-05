import typing as T
import contextlib
from io import StringIO

from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from ansi2html import Ansi2HTMLConverter
import visdcc

from ..types import (Selection, SubSet, InputPath, OutputPath)
from ..arg import Empty, parse_func_args
from .input_item import (
    InputItem, IntInputItem, FloatInputItem, StrInputItem, BoolInputItem,
    DropdownInputItem, MultiDropdownInputItem,
)
from ..utils import AllowWrapInstanceMethod


class App(AllowWrapInstanceMethod):
    type_to_widget_constructor: T.Dict[str, "InputItem"] = {}
    convert_types: T.Dict[str, T.Callable] = {}

    def __init__(
            self, func, name=None,
            show_console=True,
            console_interval=2000,
            interactive=False, init_run=False,
            result_show_type="text",
            **server_args):
        self.func = func
        if name is not None:
            self.name = name
        elif hasattr(func, "name"):
            self.name = func.name
        else:
            self.name = func.__name__
        self.show_console = show_console
        self.console_interval = console_interval
        self.interactive = interactive
        self.init_run = init_run
        self.result_show_type = result_show_type
        self.server_args = server_args
        self.input_names: T.Optional[T.List[str]] = None
        self.input_types: T.Optional[T.List[T.Type]] = None
        self.input_attrs: T.Optional[T.List[dict]] = None
        self.result: T.Optional[T.Any] = None
        self.dash_app: T.Optional[Dash] = None

    def get_layout(self):
        input_widgets = self.parse_args()
        sub_nodes = [
            html.H3("Arguments"),
            *input_widgets,
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

    def base_result_layout(self):
        return [
            html.H3("Result"),
            dcc.Store(id="out")
        ]

    def get_result_layout(self):
        layout = self.base_result_layout()
        show_type = self.result_show_type
        if show_type == "text":
            layout += [
                html.Div(id="show-text")
            ]
        elif show_type == "download":
            layout += [
                html.Button("Download Result", id="res-download-btn"),
                dcc.Download(id="res-download-index")
            ]
        elif show_type == "plotly":
            layout += [
                dcc.Graph(id='plotly-figure')
            ]
        else:
            raise NotImplementedError(
                f"The layout for result_show_type '{show_type}'"
                "is not defined")
        return layout

    def parse_args(self) -> T.List["html.Div"]:
        """Parse target function's arguments,
        return a list of input widgets."""
        widgets, names, types, attrs = [], [], [], []
        arg_objs = parse_func_args(self.func)
        for n, a in arg_objs.items():
            if a.type is Empty:
                continue
            constructor = self.type_to_widget_constructor[a.type.__name__]
            default = None if a.default is Empty else a.default
            attr = a.kwargs
            widget = constructor(
                n, a.range, default, attrs=attr).widget
            widgets.append(widget)
            names.append(n)
            types.append(a.type)
            attrs.append(attr)
        self.input_names = names
        self.input_types = types
        self.input_attrs = attrs
        return widgets

    def get_dash_app(self, *args, **kwargs):
        name = self.name or self.func.__name__
        css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        if 'external_stylesheets' not in kwargs:
            kwargs['external_stylesheets'] = css
        app = Dash(name, *args, **kwargs)
        app.layout = self.get_layout()
        self.add_callbacks(app)
        return app

    def add_callbacks(self, app: "Dash"):
        self.add_run_callbacks(app)
        self.add_result_callbacks(app)

    def add_result_callbacks(self, app: "Dash"):
        show_type = self.result_show_type
        if show_type == "text":
            self.add_text_callback(app)
        elif show_type == "download":
            self.add_download_callbacks(app)
        elif show_type == "plotly":
            self.add_plotly_callbacks(app)
        else:
            raise NotImplementedError(
                f"The callback for result_show_type '{show_type}'"
                "is not defined."
            )

    def get_run_callback_decorator(self, app: "Dash"):
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
        output = Output("out", "data")
        deco = app.callback(output, *inputs)
        return deco

    def add_run_callbacks(self, app):
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

    def add_text_callback(self, app: "Dash"):
        @app.callback(
            Output("show-text", "children"),
            Input("out", "data"))
        def show(text):
            return text

    def add_download_callbacks(self, app: "Dash"):
        @app.callback(
            Output("res-download-index", "data"),
            Input("res-download-btn", "n_clicks"),
            prevent_initial_call=True)
        def send_file(n_clicks):
            return dcc.send_file(self.result)

    def add_plotly_callbacks(self, app: "Dash"):
        @app.callback(
            Output("plotly-figure", "figure"),
            Input("out", "data"),
        )
        def show(data):
            return data

    @classmethod
    def register_widget(cls, type, widget_constructor):
        cls.type_to_widget_constructor[type.__name__] = widget_constructor

    @classmethod
    def register_type_convert(cls, type, converter=None):
        if converter is None:
            converter = type
        cls.convert_types[type.__name__] = converter

    def __call__(self):
        self.dash_app = self.get_dash_app()
        self.dash_app.run_server(**self.server_args)


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
