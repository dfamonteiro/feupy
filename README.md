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

## Thanks
I would like to thank the following people:
+ The maintainers of the [requests](https://pypi.org/project/requests/) package
+ The maintainers of the [requests_futures](https://pypi.org/project/requests-futures/) package
+ The maintainers of the [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) package
+ The maintainers of the [lxml](https://pypi.org/project/lxml/) package
+ The maintainers of the [Pillow](https://pypi.org/project/Pillow/) package
+ [Miguel Ramalho](https://github.com/msramalho) for creating [sigpy](https://github.com/msramalho/sigpy)

## Examples

### Logging in
```python
>>> # For a function to be able to access pages where you need to be logged in,
>>> # you need to pass a Credentials object as an argument to that function.
>>> 
>>> # You can tell whether or not a function needs a Credentials object by
>>> # checking if the function needs a parameter called "credentials"
>>> 
>>> from feupy import Credentials
>>> 
>>> credentials = Credentials()
Username?
:> up201806185
Password for 201806185?
:>
>>> credentials
Credentials(201806185)
```

### Student information
```python
>>> from feupy import Student
>>> from pprint import pprint
>>> 
>>> daniel = Student(201806185) # That's me!
>>> print(f"Hello, {daniel.name}!")
Hello, Daniel Filipe Amaro Monteiro!
>>> pprint(daniel.courses)
({'course': Course(742, 2019), # MIEIC
  'first academic year': 2018, # (2018/2019)
  'institution': 'Faculty of Engineering'},) # Best faculty
```

### Teacher
```python
>>> from feupy import Teacher
>>> jlopes = Teacher(230756)
>>> print(f"Thanks for teaching us Python, {jlopes.name}!")
Thanks for teaching us Python, João António Correia Lopes!
>>> print(jlopes.presentation)
Personal Presentation
João Correia Lopes is an Assistant Professor in Informatics Engineering at the Universidade do Porto and a senior researcher at INESC TEC. He has graduated in Electrical Engineering in the University of Porto in 1984 and holds a PhD in Computing Science by Glasgow University in 1997. His teaching includes undergraduate and graduate courses in databases and web applications, software engineering and programming, markup languages and semantic web. He has been involved in research projects in the area of data management, service-oriented architectures and e-Science. Currently his main research interests are e-Science and research data management.
ResearcherID  ORCID  Google Scholar Citations  DBLP Author  Scopus Author
>>> pprint(vars(jlopes))
{'acronym': 'JCL',
 'career': 'Pessoal Docente de Universidades',
 'category': 'Professor Auxiliar',
 'department': 'Department of Informatics Engineering',
 'email': None,
 'links': ('http://www.fe.up.pt/~jlopes/',
           'https://www.authenticus.pt/R-000-6RX',
           'http://orcid.org/0000-0002-9040-0889'),
 'name': 'João António Correia Lopes',
 'p_codigo': 230756,
 'personal_webpage': 'http://www.fe.up.pt/~jlopes/',
 'presentation': 'Personal Presentation\n'
                 'João Correia Lopes is an Assistant Professor in Informatics '
                 'Engineering at the Universidade do Porto and...', #etc
 'profession': 'Docente',
 'rooms': 'I129',
 'status': 'Active',
 'url': 'https://sigarra.up.pt/feup/en/func_geral.formview?p_codigo=230756',
 'voip': 3375}
```