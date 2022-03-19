import functools
import inspect
from qtpy import QtWidgets
from qtpy import QtCore

from oneface.types import (InputPath, OutputPath, Selection, SubSet)


class Worker(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, func, func_kwargs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.func = func
        self.func_kwargs = func_kwargs
        self.result = None

    def run(self):
        self.result = self.func(**self.func_kwargs)
        self.finished.emit()


def gui(func=None, **kwargs):
    if func is None:
        return functools.partial(gui, **kwargs)
    return GUI(func, **kwargs)


class GUI():

    type_to_widget_constructor = {}

    def __init__(self, func, name=None, size=None,
                 run_once=True):
        self.func = func
        self.run_once = run_once
        self.result = None
        self.app = QtWidgets.QApplication([])
        self.main_window = QtWidgets.QMainWindow()
        name = name or func.__name__
        self.main_window.setWindowTitle(name)
        if size:
            self.main_window.setFixedSize(*size)
        self.arg_widgets = {}
        self.window = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.compose_ui()
        self.connect_events()

    def compose_ui(self):
        self.compose_arg_widgets(self.layout)
        self.run_btn = QtWidgets.QPushButton("Run")
        self.layout.addWidget(self.run_btn)
        self.terminal = QtWidgets.QTextEdit()
        self.window.setLayout(self.layout)
        self.main_window.setCentralWidget(self.window)

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
            default = None if p.default is inspect._empty else p.default
            w = constructor(n, ann.range, default, attrs=ann.kwargs)
            self.arg_widgets[n] = w
            layout.addWidget(w)

    def connect_events(self):
        self.run_btn.clicked.connect(self.run_func)

    def get_args(self):
        kwargs = {}
        for n, w in self.arg_widgets.items():
            kwargs[n] = w.get_value()
        return kwargs

    def run_func(self):
        kwargs = self.get_args()
        if self.run_once:
            self.main_window.hide()
            self.result = self.func(**kwargs)
            self.main_window.close()
        else:
            thread = self.thread = QtCore.QThread()
            worker = self.worker = Worker(self.func, kwargs)
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            thread.start()
            self.run_btn.setEnabled(False)

            def finish():
                self.result = worker.result
                self.run_btn.setEnabled(True)
            thread.finished.connect(finish)

    def __call__(self):
        self.main_window.show()
        self.app.exec()
        return self.result

    @classmethod
    def register_widget(cls, type_, widget_constructor):
        cls.type_to_widget_constructor[type_.__name__] = widget_constructor


class InputItem(QtWidgets.QWidget):
    def __init__(self, name, range, default, attrs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.range = range
        self.default = default
        self.attrs = attrs
        self.init_layout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_layout(self):
        self.layout = QtWidgets.QHBoxLayout()

    def init_ui(self, label_stretch=1):
        label = self.attrs.get('text', self.name)
        self.label = QtWidgets.QLabel(f"{label}:")
        if label_stretch:
            self.layout.addWidget(self.label, stretch=label_stretch)
        else:
            self.layout.addWidget(self.label)

    def get_value(self):
        return self.input.value()


class IntInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QSpinBox()
        if self.range:
            self.input.setMinimum(self.range[0])
            self.input.setMaximum(self.range[1])
        if self.default:
            self.input.setValue(self.default)
        self.layout.addWidget(self.input, stretch=1)


class FloatInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QDoubleSpinBox()
        self.input.setSingleStep(0.1)
        if self.range:
            self.input.setMinimum(self.range[0])
            self.input.setMaximum(self.range[1])
        if self.default:
            self.input.setValue(self.default)
        self.layout.addWidget(self.input, stretch=1)


class StrInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QLineEdit()
        if self.default:
            self.input.setText(self.default)
        self.layout.addWidget(self.input, stretch=1)

    def get_value(self):
        return self.input.text()


class BoolInputItem(InputItem):
    def init_ui(self):
        super().init_ui(label_stretch=2)
        self.bt = QtWidgets.QRadioButton("True")
        self.bf = QtWidgets.QRadioButton("False")
        self.layout.addWidget(self.bt, stretch=1)
        self.layout.addWidget(self.bf, stretch=1)
        if (self.default is False):
            self.bf.setChecked(True)
        else:
            self.bt.setChecked(True)

    def get_value(self):
        return self.bt.isChecked()


class SelectionInputItem(InputItem):
    def init_ui(self):
        super().init_ui()
        self.input = QtWidgets.QComboBox()
        if self.range:
            self.input.addItems(self.range)
        if self.default:
            self.input.setCurrentText(self.default)
        self.layout.addWidget(self.input, stretch=1)

    def get_value(self):
        return self.input.currentText()


class SubsetInputItem(InputItem):
    def init_layout(self):
        self.layout = QtWidgets.QVBoxLayout()

    def init_ui(self):
        super().init_ui(label_stretch=None)
        self.cb_layout = QtWidgets.QHBoxLayout()
        self.cbs = []
        for it in self.range:
            cb = QtWidgets.QCheckBox(it)
            self.cb_layout.addWidget(cb)
            self.cbs.append(cb)
        self.layout.addLayout(self.cb_layout)
        if self.default:
            for val in self.default:
                self.cbs[self.range.index(val)].setChecked(True)

    def get_value(self):
        res = []
        for i, val in enumerate(self.range):
            if self.cbs[i].isChecked():
                res.append(val)
        return res


class PathInputItem(InputItem):
    def init_layout(self):
        self.layout = QtWidgets.QVBoxLayout()

    def init_ui(self):
        super().init_ui(label_stretch=None)
        self.box = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.dialog_open = QtWidgets.QPushButton("open")
        self.dialog_open.clicked.connect(self.get_path)
        self.box.addWidget(self.path_edit, stretch=2)
        if self.default:
            self.path_edit.setText(self.default)
        self.box.addWidget(self.dialog_open, stretch=1)
        self.layout.addLayout(self.box)

    def get_path(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open file", "", "All files (*)")
        self.path_edit.setText(fname)

    def get_value(self):
        return self.path_edit.text()


class OutPathInputItem(PathInputItem):
    def get_path(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save file", "", "All files (*)")
        self.path_edit.setText(fname)


GUI.register_widget(int, IntInputItem)
GUI.register_widget(float, FloatInputItem)
GUI.register_widget(str, StrInputItem)
GUI.register_widget(bool, BoolInputItem)
GUI.register_widget(Selection, SelectionInputItem)
GUI.register_widget(SubSet, SubsetInputItem)
GUI.register_widget(InputPath, PathInputItem)
GUI.register_widget(OutputPath, OutPathInputItem)
