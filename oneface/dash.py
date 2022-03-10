import functools
import inspect
import os.path as osp
from dash import Dash, dcc, html


HERE = osp.abspath(osp.dirname(__file__))


def app(func=None, **kwargs):
    if func is None:
        return functools.partial(app, **kwargs)
    return App(func, **kwargs)


class App(object):
    type_to_widget_constructor = {}

    def __init__(self, func, name=None, debug=True):
        self.func = func
        self.name = name
        self.debug = debug
        self.dash_app = self.get_dash_app()

    def get_layout(self):
        from oneface.core import Arg
        sig = inspect.signature(self.func)
        input_widgets = []
        for n, p in sig.parameters.items():
            ann = p.annotation
            if not isinstance(ann, Arg):
                continue
            constructor = self.type_to_widget_constructor[ann.type.__name__]
            input_widgets.append(constructor(n, ann.range))
        layout = html.Div(children=[
            *input_widgets,
            html.Br(),
            html.Button("Run", id="run-btn")
        ], style={
            'width': "60%",
            'min-width': "400px",
            'margin': "auto",
        })
        print(layout)
        return layout

    def get_dash_app(self):
        name = self.name or self.func.__name__
        css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = Dash(name, external_stylesheets=css)
        app.layout = self.get_layout()
        return app

    @classmethod
    def register_widget(cls, type, widget_constructor):
        cls.type_to_widget_constructor[type.__name__] = widget_constructor

    def __call__(self):
        self.dash_app.run_server(debug=self.debug)


def number_input_widget(name, range, step=None):
    return html.Div([
        f"{name}: ",
        dcc.Slider(range[0], range[1], step, id=f"input-{name}")
    ])


def dropdown_widget(name, range):
    return html.Div([
        f"{name}: ",
        dcc.Dropdown(range)
    ])


App.register_widget(int, functools.partial(number_input_widget, step=1))
App.register_widget(float, functools.partial(number_input_widget, step=None))
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
