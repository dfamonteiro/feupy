# The sigarra scraping library no one asked for
[![image](https://img.shields.io/pypi/v/feupy)](https://pypi.org/project/feupy/)
[![image](https://img.shields.io/pypi/status/feupy)](https://pypi.org/project/feupy/)
[![Documentation Status](https://readthedocs.org/projects/feupy/badge/?version=master)](https://feupy.readthedocs.io/en/master/?badge=master)
[![image](https://img.shields.io/pypi/pyversions/feupy.svg)](https://pypi.org/project/feupy/)

**Feupy** is a Python library that provides an interface to [FEUP](https://sigarra.up.pt/feup/en/WEB_PAGE.INICIAL "FEUP's Homepage")'s information system, [SIGARRA](https://sigarra.up.pt/up/en/web_page.inicial "SIGARRA's Homepage"). SIGARRA stands for **S**istema de **I**nformação para **G**estão **A**gregada dos **R**ecursos e dos **R**egistos **A**cadémicos (Academic Register and Aggregated Resource Management Information System, give or take).

All web requests that don't need a special permission (that is, you don't need to log in to see the page) are stored in a persistent cache with timeouts, in order to minimize latency and the number of requests made to sigarra. All web requests that need a special permission (i.e. you need to be logged in) are stored in a non-persistent cache.

## Installation
```
pip install feupy
```

## [Documentation](https://feupy.readthedocs.io)
[Click me](https://feupy.readthedocs.io)

## Building the package and uploading to PyPI
1. Change your working directory to the root of this project in your computer
2. Run these two commands
   ```
   python setup.py sdist bdist_wheel
   python -m twine upload dist/*
   ```
3. Enter your PyPI credentials when prompted
4. Celebrate!

## Building the docs and checking them out locally
1. Make sure you have the latest version of [sphinx](https://pypi.org/project/sphinx/) installed
2. Change your working directory to docs/
3. Run this command
   ```
   sphinx-build -b  html source build
   ```
4. Change your working directory to docs/build/
5. Run this command
   ```
   python -m http.server 8080
   ```
6. Open a web browser at [localhost:8080](http://127.0.0.1:8080)

## Running the tests
1. Change your working directory to the root of this project in your computer
2. Run this command
   ```
   python -m unittest
   ```
3. Hope that the tests pass

## Acknowledgements
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
 'base_url': 'https://sigarra.up.pt/feup/en/',
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
 'base_url': 'https://sigarra.up.pt/feup/en/',
 'code': 'EIC0005',
 'curricular_years': (1,),
 'has_moodle': True,
 'is_active': True,
 'name': 'Programming Fundamentals',
 'number_of_students': 182,
 'pv_ocorrencia_id': 419983,
 'regents': (Teacher(230756),),
 'semester': '1',
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

### Course info
```python
>>> from feupy import Course
>>> 
>>> mieic = Course(742)
>>> 
>>> mieic.name
'Master in Informatics and Computing Engineering'
>>> mieic.acronym
'MIEIC'
>>> [director.name for director in mieic.directors] # Let's see the names of the directors
['João Carlos Pascoal Faria', 'Maria Cristina de Carvalho Alves Ribeiro']
>>> 
>>> pprint(vars(mieic))
{'acronym': 'MIEIC',
 'base_url': 'https://sigarra.up.pt/feup/en/'
 'directors': (Teacher(210006), Teacher(209566)),
 'involved_organic_units': ('https://sigarra.up.pt/feup/en/',),
 'name': 'Master in Informatics and Computing Engineering',
 'official_code': '9459',
 'pv_ano_lectivo': 2019,
 'pv_curso_id': 742,
 'text': 'The Integrated Master in Informatics and Computing Engineering has '
         'been awarded the international EUR-ACE quality label. This certifies '
         'MIEIC as a high-quality programme which meets the international '
         'standards for professional engineering education at the masters '
         'level. [+ info]\n'
         '\n'
         'Accreditation by A3ES\r\n'
         'The Agency for Assessment and Accreditation of Higher Education '
         '(A3ES), at 20th of June, 2014, and in accordance with the '
         'recomendation and fundamentation produced by the respective External '
         ... , # etc
 'url': 'https://sigarra.up.pt/feup/en/cur_geral.cur_view?pv_curso_id=742&pv_ano_lectivo=2019'}
>>> 
>>> pprint(mieic.exams()) # Let's see this courses's currently scheduled exams
[{'curricular unit': CurricularUnit(420037),
  'finish': datetime.datetime(2019, 9, 6, 20, 0),
  'observations': 'Tenho um exame de outra disciplina marcado para esse '
                  'horário e assim juntava os dois.\r\n'
                  'José Luís Moura Borges\r\n',
  'rooms': ('B222',),
  'season': 'Especial de Conclusão - SET-E-ESPECIAL',
  'start': datetime.datetime(2019, 9, 6, 17, 0)},
 ..., # etc
 {'curricular unit': CurricularUnit(438941),
  'finish': datetime.datetime(2019, 9, 26, 13, 0),
  'observations': None,
  'rooms': ('B104', 'B208', 'B213'),
  'season': 'Exames ao abrigo de estatutos especiais - Mini-testes (1ºS)',
  'start': datetime.datetime(2019, 9, 26, 9, 0)},
 {'curricular unit': CurricularUnit(438941),
  'finish': datetime.datetime(2019, 9, 26, 17, 30),
  'observations': None,
  'rooms': ('B104', 'B213', 'B208', 'B207'),
  'season': 'Exames ao abrigo de estatutos especiais - Mini-testes (1ºS)',
  'start': datetime.datetime(2019, 9, 26, 13, 30)}]
>>> 
>>> mieic.curricular_units() # All the curricular units (with a link) from that course
[CurricularUnit(446081), CurricularUnit(437142), CurricularUnit(438941), 
CurricularUnit(436401), CurricularUnit(436402), CurricularUnit(436403), 
CurricularUnit(436404), CurricularUnit(436405), CurricularUnit(436406), 
CurricularUnit(436407), CurricularUnit(436408), CurricularUnit(436409), 
CurricularUnit(436410), CurricularUnit(436411), CurricularUnit(436412), 
CurricularUnit(436413), CurricularUnit(436414), CurricularUnit(436415), 
CurricularUnit(436416), CurricularUnit(436417), CurricularUnit(436418), 
CurricularUnit(436419), CurricularUnit(436420), CurricularUnit(436421), 
CurricularUnit(436422), CurricularUnit(436423), CurricularUnit(436424), 
CurricularUnit(436425), CurricularUnit(436426), CurricularUnit(436427), 
CurricularUnit(436428), CurricularUnit(436429), CurricularUnit(436430), 
CurricularUnit(436431), CurricularUnit(436432), CurricularUnit(436433), 
CurricularUnit(436434), CurricularUnit(436435), CurricularUnit(436436), 
CurricularUnit(436437), CurricularUnit(436438), CurricularUnit(436439), 
CurricularUnit(436440), CurricularUnit(436441), CurricularUnit(436442), 
CurricularUnit(436443), CurricularUnit(436444), CurricularUnit(436445), 
CurricularUnit(436446), CurricularUnit(436447), CurricularUnit(436448), 
CurricularUnit(436449), CurricularUnit(436450), CurricularUnit(436451), 
CurricularUnit(436452), CurricularUnit(436453), CurricularUnit(436454), 
CurricularUnit(436455), CurricularUnit(436456), CurricularUnit(436457), 
CurricularUnit(436458), CurricularUnit(436459), CurricularUnit(436460), 
CurricularUnit(436461), CurricularUnit(436462), CurricularUnit(436463), 
CurricularUnit(436464), CurricularUnit(436465), CurricularUnit(436466), 
CurricularUnit(436467), CurricularUnit(436468), CurricularUnit(436469), 
CurricularUnit(436470), CurricularUnit(436471)]
>>> len(mieic.curricular_units()) # Just out of curiosity
74
>>> [uc for uc in mieic.curricular_units() if 2 in uc.curricular_years and uc.semester == 1] # The uc's I will have this semester
[CurricularUnit(436433), CurricularUnit(436434), CurricularUnit(436435), CurricularUnit(436436), CurricularUnit(436437)]
```

### Personal info
```python
>>> from feupy import User
>>> 
>>> me = User.from_credentials(credentials)
>>> me.course.acronym
'MIEIC'
>>> 
>>> pprint(me.courses_units())
# Curricular unit       , grade
[(CurricularUnit(436433), None),
 (CurricularUnit(436434), None),
 (CurricularUnit(436435), None),
 (CurricularUnit(436436), None),
 (CurricularUnit(436437), None),
 (CurricularUnit(436439), None),
 (CurricularUnit(436438), None),
 (CurricularUnit(436441), None),
 (CurricularUnit(436442), None),
 (CurricularUnit(436440), None),
 (CurricularUnit(419981), 10),
 (CurricularUnit(419982), 11),
 (CurricularUnit(419985), 12),
 (CurricularUnit(419983), 13),
 (CurricularUnit(419984), 14),
 (CurricularUnit(420521), 15),
 (CurricularUnit(419986), 16),
 (CurricularUnit(419987), 17),
 (CurricularUnit(419990), 18),
 (CurricularUnit(419989), 19),
 (CurricularUnit(419988), 20)]
```
