# The sigarra scraping library no one asked for
[![image](https://img.shields.io/pypi/v/feupy)](https://pypi.org/project/feupy/)
[![image](https://img.shields.io/pypi/status/feupy)](https://pypi.org/project/feupy/)
[![image](https://img.shields.io/pypi/pyversions/feupy.svg)](https://pypi.org/project/feupy/)

**Feupy** is a Python library that provides an interface to [FEUP](https://sigarra.up.pt/feup/en/WEB_PAGE.INICIAL "FEUP's Homepage")'s information system, [SIGARRA](https://sigarra.up.pt/up/en/web_page.inicial "SIGARRA's Homepage"). SIGARRA stands for **S**istema de **I**nformação para **G**estão **A**gregada dos **R**ecursos e dos **R**egistos **A**cadémicos (Academic Register and Aggregated Resource Management Information System, give or take).

All web requests that don't need a special permission (that is, you don't need to log in to see the page) are stored in a persistent cache with timeouts, in order to minimize latency and the number of requests made to sigarra. All web requests that need a special permission (i.e. you need to be logged in) are stored in a non-persistent cache.

## Installation
```
pip install feupy
```

## Building the package and uploading to PyPI
1. Change your working directory to the root of this project in your computer
2. Run these two commands
   ```
   python setup.py sdist bdist_wheel
   python -m twine upload dist/*
   ```
3. Enter your PyPI credentials when prompted
4. Celebrate!
