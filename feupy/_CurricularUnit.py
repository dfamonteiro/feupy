import datetime as _datetime
import re as _re
import urllib as _urllib

import bs4 as _bs4

from . import _Credentials
from . import cache as _cache
from . import exams as _exams
from . import _Student
from . import _Teacher
from . import timetable as _timetable
from . import _internal_utils as _utils

__all__ = ["CurricularUnit"]

class CurricularUnit:
    """This class represents a FEUP curricular unit.

    Properties:
        pv_ocorrencia_id   (int)
        url                (str) # The url of this curricular unit page
        name               (str) # e.g. 'Microprocessors and Personal Computers'
        code               (str) # e.g. 'EIC0016'
        acronym            (str) # e.g. 'MPCP'
        academic_year      (int) # e.g. 2018 (meaning this curricular unit was taught in 2018/2019)
        semester           (int) # either 1 or 2
        has_moodle         (bool)
        is_active          (bool)
        webpage_url        (str or None) # For example, CurricularUnit(419983).webpage_url == 'https://web.fe.up.pt/~jlopes/doku.php/teach/fpro/index' (FPRO)
        number_of_students (int)
        curricular_year    (int) # usually 1-5
        ECTS_credits       (float)
        regents            (tuple of Teacher objects)
        teachers           (tuple of Teacher objects)
        text               (string) # Basically a text dump starting from "Teaching language"
    
    Methods:
        from_url   (class method)
        from_a_tag (class method)
        contents
        students
        timetable
        all_timetables
        other_occurrences
        stats
        grades_distribution
        statistics_history
        classes
        exams
        results
    
    Operators:
        __repr__, __str__
        __eq__, __le__, __lt__, __ge__, __gt__ (Comparisons between curricular units and hashing are made with the pv_ocorrencia_id)
        __hash__
    """
    __slots__ = ["pv_ocorrencia_id", "url", "name", "code", "acronym", "academic_year", "semester", "has_moodle", "is_active", "webpage_url", 
                 "number_of_students", "curricular_year", "ECTS_credits", "regents", "teachers", "text"]
    
    def __init__(self, pv_ocorrencia_id : int, use_cache : bool = True):
        """Parses the webpage of the curricular unit with the given pv_ocorrencia_id.
        The cache can be bypassed by setting use_cache to False.
        If a given attribute can't be parsed (or is nonexistent),
        it will be set to None.
        """

        self.pv_ocorrencia_id = pv_ocorrencia_id
        self.url = _utils.SIG_URLS["curricular unit"] + "?" + _urllib.parse.urlencode({"pv_ocorrencia_id" : str(pv_ocorrencia_id)})
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "The School responsible for the occurrence was not found." in html:
            raise ValueError(f"Curricular unit with pv_ocorrencia_id {pv_ocorrencia_id} doesn't exist")
       
        contents = soup.find("div", {"id" : "conteudoinner"})

        self.name = contents.find_all("h1")[1].string

        first_table = contents.find("table")
        self.code, self.acronym = _utils.scrape_html_table(first_table)[0][1], _utils.scrape_html_table(first_table)[0][4]

        self.academic_year = _utils.parse_academic_year(contents)

        match = _re.findall(r"Instance: \d\d\d\d/\d\d\d\d - (\d)S", str(contents))[0]
        self.semester = int(match)

        self.has_moodle = "UC tem página no Moodle" in str(contents)

        second_table = first_table.find_next("table", {"class" : "formulario"})
        self.webpage_url = None
        for label, info in _utils.scrape_html_table(second_table):
            if   label == "Active? ":           # Usually the first row on the table
                self.is_active = "Yes" in info
            elif label == "Web Page: ":         # Usually the second row on the table (optional)
                self.webpage_url = info
        
        third_table = second_table.find_next("table", {"class" : "dados"})
        third_table = _utils.scrape_html_table(third_table)
        third_table.pop(0) # We don't care about the header row

        n_students = (int(row[1]) for row in third_table)
        self.number_of_students = sum(n_students)

        self.curricular_year = int(third_table[0][3])
        self.ECTS_credits    = float(third_table[0][5].replace(',', '.'))
        
        teachers_div   = contents.find("div", {"class" : "horas"})
        if teachers_div == None:
            teachers_links = filter(lambda tag: "func_geral.formview" in str(tag), contents.find_all("a"))
        else:
            teachers_links = filter(lambda tag: "func_geral.formview" in tag["href"], teachers_div.find_all("a"))
        teachers_urls = [_utils.BASE_URL + tag["href"] for tag in teachers_links]
        _cache.get_html_async(teachers_urls)
        self.teachers  = tuple(_Teacher.Teacher.from_url(url) for url in teachers_urls)

        regents_div    = contents.find("div", {"class" : "responsabilidades"})
        if regents_div == None:
            self.regents = ()
        else:
            regents_links  = filter(lambda tag: "p_codigo" in tag["href"], regents_div.find_all("a")) # If "p_codigo" is in the url, then it's a teacher
            self.regents   = tuple((_Teacher.Teacher.from_a_tag(link) for link in regents_links))

        text = contents.text
        beggining_index = text.find("Teaching language")
        self.text = text[beggining_index:]

    def contents(self, credentials : _Credentials.Credentials) -> dict:
        """Returns a nested dictionary structure, where each dictionary represents a folder.
        Every dictionary maps a string (the folder or file name) to either a dictionary
        (a nested folder) or a tuple (a file or a link).

        A tuple representing a file is made of 4 attributes:
        (
            file type       :string (either "file" or "link"),
            url             :string (note: if you want to download a file from sigarra, check Credentials.download()),
            info            :string or None,
            upload date     :Datetime.Date (Note: links will have this attribute always set to today)
        )

        Example of the output:
        {'A folder': {'folderception': {'A file': ('file',
                                                'https://sigarra.up.pt/feup/pt/conteudos_service.conteudos_cont?pct_id=012345&pv_cod=06ahastCa',
                                                None,
                                                datetime.date(2018, 10, 2)),
                                        'Python': ('file',
                                                'https://sigarra.up.pt/feup/pt/conteudos_service.conteudos_cont?pct_id=012346&pv_cod=06TtaSaPH7',
                                                'aaaaaa',
                                                datetime.date(2018, 11, 13)),
                                        'Simulator': ('link',
                                                    'https://github.com/hneemann/Digital',
                                                    'It\'s a simulator.',
                                                    datetime.date(2019, 5, 25))},
                    'jhbh': {'aa': ('link',
                                    'https://salmanarif.bitbucket.io/visual/index.html',
                                    'aaaaaa',
                                    datetime.date(2019, 8, 2)),
                            'bb': ('file',
                                    'https://sigarra.up.pt/feup/pt/conteudos_service.conteudos_cont?pct_id=012347&pv_cod=06WjyvGato',
                                    'banana',
                                    datetime.date(2018, 10, 12))}}}
        """
        html = credentials.get_html(self.url) # curricular unit page
        soup = _bs4.BeautifulSoup(html, "lxml")

        tag = soup.find("a", {"title" : "Contacts"})

        if tag == None:
            return {}
            # The curricular unit either doesn't have a contents page
            # or you don't have access to it
            # I can't distinguish between these two situations, therefore I'm
            # returning an empty dict. I prefer this approach to raising an (perhaps erroneous) exception
        
        url = _utils.BASE_URL_PT + tag["href"]

        html = credentials.get_html(url) # contents page
        soup = _bs4.BeautifulSoup(html, "lxml")
        content = soup.find("div", {"id" : "conteudoinner"})

        if "Não existem conteúdos para ver" in html:
            return {}
        
        def has_pct_grupo(a):
            try:
                int(a["name"])
                return True
            except:
                return False

        pct_grupos = (a["name"] for a in content.find_all("a") if has_pct_grupo(a))
        query = "&".join(f"pct_grupo={grupo}" for grupo in pct_grupos)
        url = url + "&" + query 

        html = credentials.get_html(url) # contents page with all the folders open
        soup = _bs4.BeautifulSoup(html, "lxml")
        content = soup.find("div", {"id" : "conteudoinner"})
        
        files_and_dirs = [p for p in content.find_all("p") if p.has_attr("class")]
        
        def convert_list_to_dict(files_and_dirs_list : list, result : dict, conteudosnivel : int = 1):
            """Please use protective glasses when looking at this function"""
            for i, p in enumerate(files_and_dirs_list):
                if p["class"] == [f"conteudosnivel{conteudosnivel}"]:
                    if "/feup/pt/imagens/Pasta" in str(p): # It's a directory
                        name = p.find_all("a")[-1].string
                        result[name] = {}

                        for i1, p1 in enumerate(files_and_dirs_list):
                            if i1 <= i:
                                continue

                            if p1["class"] == [f"conteudosnivel{conteudosnivel}"]:
                                convert_list_to_dict(files_and_dirs_list[i + 1: i1], result[name], conteudosnivel + 1)
                                break
                        else:
                            convert_list_to_dict(files_and_dirs_list[i + 1:], result[name], conteudosnivel + 1)
                    
                    else: # It's a file (or a link)
                        if p.a == None: # If there's no link, just ignore it
                            continue

                        file_type = "link" if p.find("span", {"class" : "t"}) == None else "file"
                        name = p.a.string
                        try:
                            info = p.find("span", {"class" : "textopequenoconteudos"}).string
                        except:
                            info = None

                        if file_type == "file":
                            
                            upload_time = _datetime.date(*map(int, p.find("span", {"class" : "t"}).string.split("-")[1].split("/")))
                            url = _utils.BASE_URL_PT + p.a["href"]
                        else:
                            upload_time = _datetime.date.today() # A placeholder value
                            url = p.a["href"]

                        result[name] = (file_type, url, info, upload_time)

        result = {}
        convert_list_to_dict(files_and_dirs, result, 1)

        return result

    def students(self, credentials : _Credentials.Credentials, use_cache : bool = True) -> list:
        """Parses the student page and returns a list of tuples.
        A credencials object is required because one needs 
        privileged access to access the page.
        The cache can be bypassed by setting use_cache to False.
        The each tuple is made of a Student object, their status (string), 
        number of registrations (int), and the type of student.
        Example of a tuple:
        [
            ...,
            (Student(201812345), 'Ordinário', 1, 'Normal'),
            ...
        ]
        """

        data   = []
        tables = []

        def format_table(tags_list, index): # Note: what this function returns doesn't matter,
            if index == 0:                  # we're appending the information in the tables to data
                return None                               
            
            student_username = int(tags_list[0].string)
            student = _Student.Student(student_username)

            status = tags_list[2].string.strip()

            number_of_registrations = int(tags_list[3].string)

            student_type = tags_list[4].string

            data.append((student, status, number_of_registrations, student_type))
                    
        n_pages    = (self.number_of_students // 50) + 1
        pages_urls = []
        for n in range(1, n_pages + 1):
            url = _utils.SIG_URLS["curricular unit students"] + "?" + _urllib.parse.urlencode({"pv_ocorrencia_id" : str(self.pv_ocorrencia_id), "pv_num_pag" : str(n)})
            pages_urls.append(url)
        
        for html in credentials.get_html_async(pages_urls):
            soup = _bs4.BeautifulSoup(html, "lxml")
            table = soup.find("table", {"class" : "dadossz"})
            tables.append(table)


        student_urls = []
        for table in tables: # get all the student urls
            student_usernames = _re.findall(r"(\d\d\d\d\d\d\d\d\d)", str(table))
            student_urls.extend(_utils.SIG_URLS["student page"] + "?" + _urllib.parse.urlencode({"pv_num_unico" : username}) for username in student_usernames)
        _cache.get_html_async(student_urls, use_cache = use_cache) # Refreshing the cache

        for table in tables:
            _utils.scrape_html_table(table, format_table) # get the data in the tables
        
        return data
    
    def timetable(self, credentials : _Credentials.Credentials) -> list:
        """Returns the current curricular unit timetable 
        as a list of dictionaries if possible, otherwise returns None.
        (see timetable.parse_current_timetable for more info)
        Example:
        [
            {'class type': 'T',
            'classes': ('1MIEIC01',
                        '1MIEIC02',
                        '1MIEIC09'),
            'curricular unit': CurricularUnit(419989),
            'finish': datetime.time(11, 0),
            'room': ('B003',),
            'start': datetime.time(10, 0),
            'teachers': (Teacher(23545),),
            'weekday': 'Friday'},
            ...
        ]
        """
        html = credentials.get_html(_utils.SIG_URLS["curricular unit timetable"], {"pv_ocorrencia_id" : self.pv_ocorrencia_id})
        soup = _bs4.BeautifulSoup(html, "lxml")

        return _timetable.parse_current_timetable(credentials, soup.a["href"])
    
    def all_timetables(self, credentials : _Credentials.Credentials) -> dict:
        """Parses all the timetables related to this curricular unit.
        Returns a dictionary which maps a tuple with two datetime.date objects,
        start and finish (the time span in which this timetable is valid), to a
        list of dictionaries (see timetable.parse_timetable for further info).
        (see timetable.parse_timetables for further info)
        An example:
        {
            (datetime.date(2019, 2, 10), datetime.date(2019, 6, 1)): [
                {...},
                {...},
                {...},
                ...
            ],
            ...
        }
        """
        html = credentials.get_html(_utils.SIG_URLS["curricular unit timetable"], {"pv_ocorrencia_id" : self.pv_ocorrencia_id})
        soup = _bs4.BeautifulSoup(html, "lxml")

        return _timetable.parse_timetables(credentials, soup.a["href"])

    def other_occurrences(self, use_cache : bool = True) -> tuple:
        """Returns a tuple of CurricularUnit objects,
        which are occurrences of this object from other years.
        The cache can be bypassed by setting use_cache to False.
        """
        html = _cache.get_html(self.url)
        soup = _bs4.BeautifulSoup(html, "lxml")

        tag = soup.find("a", {"title" : "Other occurrences"})
        url = _utils.BASE_URL + tag["href"]

        html = _cache.get_html(url)         # Now we have the html of the "other occurrences" page 
        soup = _bs4.BeautifulSoup(html, "lxml")

        table = soup.find_all("table", {"class" : "dados"})[1]
        course_tags = table.find_all("a")

        _cache.get_html_async((_utils.BASE_URL + a_tag["href"] for a_tag in course_tags), use_cache = use_cache) # Refresh the cache

        return tuple(CurricularUnit.from_a_tag(a_tag) for a_tag in course_tags)
        
    def stats(self, credentials : _Credentials.Credentials) -> tuple:
        """Returns a tuple of 3 ints: number of registered students,
        number of evaluated students, and number of approved students.
        A Credentials object is required.
        """
        
        html = credentials.get_html(_utils.SIG_URLS["curricular unit statistics"], params = {"pv_ocorrencia_id" : str(self.pv_ocorrencia_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Não foram encontrados estudantes inscritos na ocorrência indicada." in html:
            raise LookupError(f"The statistics for {self.__repr__()} have not been released yet")

        table = soup.find_all("table")[-1] # get the last table of the page
        table_data = table.find_all("td", {"class" : "k n"})[0:3] # get the first three tds

        registered, evaluated, approved = map(lambda tag: int(tag.string), table_data)

        return (registered, evaluated, approved)
    
    def grades_distribution(self, credentials : _Credentials.Credentials) -> dict:
        """Returns a dictionary representing the distribution of the grades.
        The dictionary maps the grade to the number of students who got
        that grade. Here is an example of the output of this function:
        {'RFC': 9,
         'RFE': 17,
         'RFF': 18,
             5: 4,
             6: 5,
             7: 7,
             8: 6,
             9: 4,
            10: 12,
            11: 11,
            12: 13,
            13: 21,
            14: 4,
            15: 12,
            16: 7,
            17: 13,
            18: 8,
            19: 7,
            20: 1}
        """

        html = credentials.get_html(_utils.SIG_URLS["curricular unit grades distribution"], params = {"pv_ocorrencia_id" : str(self.pv_ocorrencia_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Não foram encontrados estudantes avaliados na ocorrência indicada." in html:
            raise LookupError(f"The statistics for {self.__repr__()} have not been released yet")
        
        table = soup.find_all("table")[-2] # get the second last table of the page
        tbody = table.find("tbody")
        result = {}

        def format_table(tags_list, index): # Note: what this function returns doesn't matter,
            try:                            # We're updating the result dictionary
                grade = int(tags_list[0].string)
            except:
                grade = tags_list[0].string
            
            n_students = int(tags_list[2].string)

            result[grade] = n_students
        
        _utils.scrape_html_table(tbody, format_table)

        return result

    def statistics_history(self, credentials : _Credentials.Credentials) -> list:
        """Returns a list of tuples each representing an academic year.
        Contents of a tuple:
        (
            academic year        (int)
            registered students, (int)
            evaluated students,  (int)
            approved students,   (int)
            evaluated students average grade,      (float)
            evaluated students standard deviation, (float)
            approved students  average grade,      (float)
            approved students  standard deviation, (float)
        )

        Example of the output of this function:
       [(2016, 208, 152, 120, 12.43, 3.75, 13.4,  2.5),
        (2017, 203, 149, 113, 12.08, 3.08, 12.27, 3.0),
        (2018, 203, 170, 133, 12.51, 3.76, 13.53, 2.76)]
        """
        
        html = credentials.get_html(_utils.SIG_URLS["curricular unit stats history"], params = {"pv_ocorrencia_id" : str(self.pv_ocorrencia_id), "pv_n_prev_alet" : "20"})
        soup = _bs4.BeautifulSoup(html, "lxml")

        table = soup.find_all("table")[-1] # get the last table of the page
        tbody = table.find("tbody")
        rows = [row for row in tbody.find_all("tr") if row["class"] == ['p']]

        result = []
        
        for row in rows:
            academic_year_td = row.find("td", {"class" : "k"})
            academic_year = int(academic_year_td.text[0:4])

            row_data = row.find_all("td", {"class" : "n"})

            registered, evaluated, approved = map(lambda tag: int(tag.string), row_data[0:3])

            evaluated_avg, evaluated_std_dev, approved_avg, approved_std_dev = map(lambda tag: float(tag.string), row_data[3:7])

            result.append((academic_year, registered, evaluated, approved, evaluated_avg, evaluated_std_dev, approved_avg, approved_std_dev))

        return result
    
    def classes(self, credentials : _Credentials.Credentials, use_cache : bool = True) -> dict:
        """Returns a dictionary which maps a class name to a tuple of students
        (the students of that class). Example:
        {
            '1MIEIC01': (Student(201800000),
                         Student(201800001),
                         Student(201800002),
                         Student(201800003)),
            '1MIEIC02': (Student(201800004),
                         Student(201800005),
                         Student(201800006),
                         Student(201800007),
                         Student(201800008),
                         Student(201800009),
                         Student(201800010),
                         Student(201800011),
                         Student(201800012)),
            '...'     : (...)
        }
        """
        html = credentials.get_html(_utils.SIG_URLS["curricular unit classes"], params = {"pv_ocorrencia_id" : str(self.pv_ocorrencia_id)}) # this html redirects us to the url we want
        soup = _bs4.BeautifulSoup(html, "lxml")

        tags = soup.find_all("a")

        if len(tags) == 1:
            urls = [tags[0]["href"]]
        else:
            urls = [_utils.BASE_URL + tag["href"] for tag in tags if "it_listagem.lista_turma_disciplina" in str(tag)]

        result = {}

        for url in urls:
            html = credentials.get_html(url)
            soup = _bs4.BeautifulSoup(html, "lxml")
            contents = soup.find("div", {"id" : "conteudo"})

            all_students_urls = (_utils.BASE_URL + tag["href"] for tag in contents.find_all("a") if tag.parent.name == "td")
            _cache.get_html_async(all_students_urls, use_cache = use_cache) # refresh the cache
            
            title = contents.find("h3") # starting point

            while title.find_next("h3") != None:
                title = title.find_next("h3") # Skip to the next class

                class_name = _re.findall(r"Turma: ([^\s]+)", title.text)[0]

                table = title.find_next("table")

                if table == None:
                    students = ()
                else:
                    students = tuple(_Student.Student.from_a_tag(tag) for tag in table.find_all("a"))

                result[class_name] = students

        return result

    def exams(self, use_cache : bool = False):
        """Returns a tuple of dictionaries (See exams.exams() for further information)"""
        url = _utils.SIG_URLS["curricular unit exams"] + "?" + _urllib.parse.urlencode({"p_ocorr_id" : str(self.pv_ocorrencia_id)})

        return _exams.exams(url, use_cache)

    def results(self, credentials : _Credentials.Credentials, use_cache : bool = True) -> dict:
        """Returns a dictionary which maps a string representing the exams season ('Época Normal (2ºS)'/'Época Recurso (2ºS)')
        to a list of tuples with two values each. The first value is a Student object and the second value is the grade the student got.
        Example:
        {'Época Normal (2ºS)': [(Student(201800001), 10),
                                (Student(201800002), 13),
                                (Student(201800003), 10),
                                (Student(201800004), 'RFE'),
                                (Student(201800005), 'RFF'),
                                (Student(201800006), 'RFF'),
                                ...],
        'Época Recurso (2ºS)': [(Student(201800008), 11),
                                (Student(201800009), 7),
                                (Student(201800010), 8),
                                (Student(201800011), 8),
                                (Student(201800012), 'RFE'),
                                (Student(201800013), 13),
                                (Student(201800014), 5),
                                (Student(201800019), 'RFC'),
                                ...]}
        """
        html = credentials.get_html(_utils.SIG_URLS["curricular unit results"], params = {"pv_ocorr_id" : str(self.pv_ocorrencia_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Não tem permissões para aceder a este conteúdo" in html:
            raise PermissionError("Your Credentials object does not have access to this curricular unit's results")
        
        tags = (tag for tag in soup.find_all("a") if "lres_geral.show_pauta_resul" in str(tag))

        result = {}

        for tag in tags:
            result[tag.string] = []

            url = _utils.BASE_URL + tag["href"]

            html = credentials.get_html(url)
            soup = _bs4.BeautifulSoup(html, "lxml")

            table = soup.find("table", {"class" : "dadossz"})

            rows = table.find_all("tr", {"class" : "i"})

            student_urls = []
            for row in rows: # get all the student urls
                student_usernames = _re.findall(r"(\d\d\d\d\d\d\d\d\d)", str(row))
                student_urls.extend(_utils.SIG_URLS["student page"] + "?" + _urllib.parse.urlencode({"pv_num_unico" : username}) for username in student_usernames)
            _cache.get_html_async(student_urls, use_cache = use_cache) # Refreshing the cache

            for row in rows:
                username = int(row.find("td", {"class" : "l"}).string)

                grade_str = row.find("td", {"class" : "n"}).string
                try:
                    grade = int(grade_str)
                except:
                    grade = grade_str
                
                result[tag.string].append((_Student.Student(username), grade))
        
        return result

    @classmethod
    def from_url(cls, url : str, use_cache : bool = True):
        """Scrapes the curricular unit webpage from the given url and returns a CurricularUnit object"""
        
        matches = _re.findall(r"pv_ocorrencia_id=(\d+)$", url)
        
        if len(matches) == 0:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid curricular unit url")
        
        pv_ocorrencia_id = int(matches[0])

        return CurricularUnit(pv_ocorrencia_id, use_cache)
    
    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True):
        """Scrapes the curricular unit webpage from the given anchor tag and returns a CurricularUnit object"""
        
        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return CurricularUnit.from_url(bs4_tag["href"], use_cache)
    
    # Comparisons between curricular units are made with the pv_ocorrencia_id
    def __eq__(self, other):
        if isinstance(other, CurricularUnit):
            return self.pv_ocorrencia_id == other.pv_ocorrencia_id
        else:
            return NotImplementedError
        
    def __gt__(self, other):
        if isinstance(other, CurricularUnit):
            return self.pv_ocorrencia_id > other.pv_ocorrencia_id
        else:
            return NotImplementedError
    
    def __ge__(self, other):
        if isinstance(other, CurricularUnit):
            return self.pv_ocorrencia_id >= other.pv_ocorrencia_id
        else:
            return NotImplementedError
    
    def __lt__(self, other):
        if isinstance(other, CurricularUnit):
            return self.pv_ocorrencia_id < other.pv_ocorrencia_id
        else:
            return NotImplementedError
    
    def __le__(self, other):
        if isinstance(other, CurricularUnit):
            return self.pv_ocorrencia_id <= other.pv_ocorrencia_id
        else:
            return NotImplementedError
    
    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}

    def __hash__(self):
        return hash(self.pv_ocorrencia_id)
    
    def __repr__(self):
        return f"CurricularUnit({self.pv_ocorrencia_id})"
    
    def __str__(self):
        return f"{self.acronym} ({self.academic_year}/{self.academic_year + 1})" # e.g. ALGE (2019/2019)
