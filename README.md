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

### Student info
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

### Teacher info
```python
>>> from feupy import Teacher
>>> 
>>> jlopes = Teacher(230756)
>>> 
>>> print(f"Thanks for teaching us Python, {jlopes.name}!")
Thanks for teaching us Python, João António Correia Lopes!
>>> 
>>> print(jlopes.presentation)
Personal Presentation
João Correia Lopes is an Assistant Professor in Informatics Engineering at the Universidade do Porto and a senior researcher at INESC TEC. He has graduated in Electrical Engineering in the University of Porto in 1984 and holds a PhD in Computing Science by Glasgow University in 1997. His teaching includes undergraduate and graduate courses in databases and web applications, software engineering and programming, markup languages and semantic web. He has been involved in research projects in the area of data management, service-oriented architectures and e-Science. Currently his main research interests are e-Science and research data management.
ResearcherID  ORCID  Google Scholar Citations  DBLP Author  Scopus Author
>>> 
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

### Curricular unit info
```python
>>> from feupy import CurricularUnit
>>> 
>>> fpro = CurricularUnit(419983)
>>> 
>>> fpro.name
'Programming Fundamentals'
>>> fpro.acronym
'FPRO'
>>> 
>>> pprint(vars(fpro))
{'ECTS_credits': 6.0,
 'academic_year': 2018,
 'acronym': 'FPRO',
 'code': 'EIC0005',
 'curricular_year': 1,
 'has_moodle': True,
 'is_active': True,
 'name': 'Programming Fundamentals',
 'number_of_students': 182,
 'pv_ocorrencia_id': 419983,
 'regents': (Teacher(230756),),
 'semester': 1,
 'teachers': (Teacher(230756),
              Teacher(230756),
              Teacher(520205),
              Teacher(552793),
              Teacher(209847)),
 'text': 'Teaching language\n'
         'Portuguese\n'
         'Objectives\n'
         '1 - BACKGROUND\n'
         'Fluency in the process of software development is a basic '
         'prerequisite to the work of Informatics Engineers. In order to use '
         'computers to solve problems effectively, students must be competent '
         'at reading and writing programs using higher-order programming '
         'languages.\n'
         '2 - SPECIFIC AIMS...', # etc
 'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=419983',
 'webpage_url': 'https://web.fe.up.pt/~jlopes/doku.php/teach/fpro/index'}
>>> 
>>> pprint(fpro.other_occurrences())
(CurricularUnit(436425),
 CurricularUnit(419983),
 CurricularUnit(399878),
 CurricularUnit(384923),
 CurricularUnit(368689),
 CurricularUnit(350482),
 CurricularUnit(332985),
 CurricularUnit(272575),
 CurricularUnit(272574),
 CurricularUnit(272573),
 CurricularUnit(272572),
 CurricularUnit(272571),
 CurricularUnit(272570),
 CurricularUnit(272569))
>>> [uc.academic_year for uc in fpro.other_occurrences()]
[2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006]
>>> 
>>> pprint(fpro.classes(credentials)) # Remember the Credentials object we created earlier?
{
    '1MIEIC01': [Student(201800000),
                 Student(201800001),
                 Student(201800002),
                 Student(201800003)],
    '1MIEIC02': [Student(201800004),
                 Student(201800005),
                 Student(201800006),
                 Student(201800007),
                 Student(201800008),
                 Student(201800009),
                 Student(201800010),
                 Student(201800011),
                 Student(201800012)],
    '...'     : [...] # etc
}
>>>
>>> pprint(fpro.students(credentials))
# (student, status, number of registrations, student type)
[(Student(201800001), 'Ordinário', 1, 'Normal'), 
 (Student(201800002), 'Ordinário', 1, 'Normal'),
 (Student(201800003), 'Ordinário', 1, 'Normal'),
 (Student(201800004), 'Estudante internacional', 1, 'Normal'),
 (Student(201800005), 'Estudante internacional', 1, 'Normal'),
 (Student(201800006), 'Ordinário', 1, 'Normal'),
 (Student(201800007), 'Ordinário', 1, 'Normal'),
 (Student(201800008), 'Ordinário', 2, 'Normal'),
 (Student(201800009), 'Ordinário', 2, 'Normal'),
 (Student(201800010), 'Ordinário', 1, 'Normal'),
 (Student(201800011), 'Estudante internacional', 1, 'Normal'),
 (Student(201800012), 'Trabalhador-Estudante', 1, 'Normal'),
 ... # etc
 ]
>>> 
>>> pprint(fpro.results(credentials)) # Get the results from the exams
{'Época Normal (1ºS)': [(Student(201800001), 10),
                        (Student(201800002), 13),
                        (Student(201800003), 10),
                        (Student(201800004), 'RFE'),
                        (Student(201800005), 'RFF'),
                        (Student(201800006), 'RFF'),
                        ...], # etc
'Época Recurso (1ºS)': [(Student(201800008), 11),
                        (Student(201800009), 7),
                        (Student(201800010), 8),
                        (Student(201800011), 8),
                        (Student(201800012), 'RFE'),
                        (Student(201800013), 13),
                        (Student(201800014), 5),
                        (Student(201800019), 'RFC'),
                        ...]} # etc
>>> 
>>> pprint(fpro.timetable(credentials)) # Returns the classes from the timetable as dicts
[{'class type': 'TP',
  'classes': ('1MIEIC04',),
  'curricular unit': CurricularUnit(419983),
  'finish': datetime.time(10, 0),
  'room': ('B307',),
  'start': datetime.time(8, 0),
  'teachers': (Teacher(209847), Teacher(520205)),
  'weekday': 'Monday'},
 {'class type': 'TP',
  'classes': ('1MIEIC01',),
  'curricular unit': CurricularUnit(419983),
  'finish': datetime.time(10, 30),
  'room': ('B302',),
  'start': datetime.time(8, 30),
  'teachers': (Teacher(230756),),
  'weekday': 'Tuesday'},
 {'class type': 'T',
  'classes': ('1MIEIC01',
              '1MIEIC02',
              '1MIEIC03',
              '1MIEIC04',
              '1MIEIC05',
              '1MIEIC06',
              '1MIEIC07',
              '1MIEIC08'),
  'curricular unit': CurricularUnit(419983),
  'finish': datetime.time(13, 30),
  'room': ('B002',),
  'start': datetime.time(12, 0),
  'teachers': (Teacher(230756),),
  'weekday': 'Tuesday'},
 {'class type': 'TP',
  'classes': ('1MIEIC06',),
  'curricular unit': CurricularUnit(419983),
  'finish': datetime.time(13, 30),
  'room': ('B310',),
  'start': datetime.time(11, 30),
  'teachers': (Teacher(209847), Teacher(552793)),
  'weekday': 'Wednesday'},
  ...] # etc
```