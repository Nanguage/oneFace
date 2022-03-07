import functools
import inspect
from PyQt6 import QtWidgets


def gui(func=None, **kwargs):
    if func is None:
        return functools.partial(gui, **kwargs)
    return GUI(func, **kwargs)


class GUI():

    type_to_widget_constructor = {}

    def __init__(self, func, name=None, size=None):
        self.func = func
        self.result = None
        self.app = QtWidgets.QApplication([])
        self.main_window = QtWidgets.QMainWindow()
        name = name or func.__name__
        self.main_window.setWindowTitle(name)
        if size:
            self.main_window.setFixedSize(*size)
        self.arg_widgets = {}
        self.compose_ui()
        self.connect_events()

    def compose_ui(self):
        self.window = window = QtWidgets.QWidget()
        self.layout = layout = QtWidgets.QVBoxLayout()
        self.compose_arg_widgets(layout)
        self.run_btn = QtWidgets.QPushButton("Run")
        layout.addWidget(self.run_btn)
        self.terminal = QtWidgets.QTextEdit()
        window.setLayout(layout)
        self.main_window.setCentralWidget(window)

    def compose_arg_widgets(self, layout):
        from oneface.core import Arg
        sig = inspect.signature(self.func)
        for n, p in sig.parameters.items():
            ann = p.annotation
            if not isinstance(ann, Arg):
                continue
            if ann.type.__name__ not in self.type_to_widget_constructor:
                raise NotImplementedError(
                  f"Input widget constructor is not registered for {ann.type}")
            constructor = self.type_to_widget_constructor[ann.type.__name__]
            w = constructor(n, ann.range)
            layout.addWidget(w)

    def connect_events(self):
        self.run_btn.clicked.connect(self.run_func)

    def get_args(self):
        NotImplemented

    def run_func(self):
        kwargs = self.get_args()
        self.result = self.func(**kwargs)

    def __call__(self):
        self.main_window.show()
        self.app.exec()
        return self.result

    @classmethod
    def register_widget(cls, type_, widget_constructor):
        cls.type_to_widget_constructor[type_.__name__] = widget_constructor


class InputItem(QtWidgets.QWidget):
    def __init__(self, name, range, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.range = range
        self.layout = QtWidgets.QHBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        self.layout.addWidget(QtWidgets.QLabel(f"{self.name}:"))


class IntInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QSpinBox()
        if self.range:
            self.input.setMinimum(self.range[0])
            self.input.setMaximum(self.range[1])
        self.layout.addWidget(self.input)


class FloatInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QDoubleSpinBox()
        if self.range:
            self.input.setMinimum(self.range[0])
            self.input.setMaximum(self.range[1])
        self.layout.addWidget(self.input)


GUI.register_widget(int, IntInputItem)
GUI.register_widget(float, FloatInputItem)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "./")
    from oneface.core import one, Arg

    @gui(name="Test")
    @one
    def func(a: Arg(int, [0, 10]),
             b: Arg(float, [0, 1])):
        print(a+b)
        return a+b

    print(func())
