from setuptools import setup, find_packages
import re


classifiers = [
    "Development Status :: 3 - Alpha",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    'License :: OSI Approved :: MIT License',
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
]


keywords = [
    'GUI',
    'CLI',
]


def get_version():
    with open("oneface/__init__.py") as f:
        for line in f.readlines():
            m = re.match("__version__ = '([^']+)'", line)
            if m:
                return m.group(1)
        raise IOError("Version information can not found.")


def get_long_description():
    return "See https://github.com/Nanguage/oneFace"


def get_requirements_from_file(filename):
    requirements = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements


def get_install_requires():
    return get_requirements_from_file('requirements.txt')


requires_test = ['pytest', 'pytest-cov', 'flake8']
requires_doc = []
with open("docs/requirements.txt") as f:
    for line in f:
        p = line.strip()
        if p:
            requires_doc.append(p)
requires_dash = ['ansi2html', 'dash', 'visdcc']


setup(
    name='oneFace',
    author='Weize Xu',
    author_email='vet.xwz@gmail.com',
    version=get_version(),
    license='MIT',
    description='oneFace is a library for automatically generating multiple '
    'interfaces(CLI, GUI) from a callable Python object',
    long_description=get_long_description(),
    keywords=keywords,
    url='https://github.com/Nanguage/oneFace',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=get_install_requires(),
    extras_require={
        'test': requires_test,
        'doc': requires_doc,
        'dev': requires_test + requires_doc,
        'dash': requires_dash,
        'qt': ['pyqt6'],
        'pyqt5': ['pyqt5'],
        'pyqt6': ['pyqt6'],
        'pyside2': ['PySide2'],
        'pyside6': ['PySide6'],
        'all': ['pyqt6'] + requires_dash,
    },
    python_requires='>=3.8, <4',
)
