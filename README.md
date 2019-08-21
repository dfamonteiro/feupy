# feupy: the sigarra scraping library no one asked for

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