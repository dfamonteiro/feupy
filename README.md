# The sigarra scraping library no one asked for
[![image](https://img.shields.io/pypi/v/feupy)](https://pypi.org/project/feupy/)
[![image](https://img.shields.io/pypi/status/feupy)](https://pypi.org/project/feupy/)
[![image](https://img.shields.io/pypi/pyversions/feupy.svg)](https://pypi.org/project/feupy/)
## Installation
```
pip install feupy
```

## Building the package and uploading to PyPI
1. Change your working directory to the root of this project in your computer
2. Run these two commands
```powershell
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```
3. Enter your PyPI credentials when prompted

