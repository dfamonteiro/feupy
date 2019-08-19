import re as _re
import urllib as _urllib

import bs4 as _bs4

from . import _Credentials
from . import _internal_utils as _utils
from . import cache as _cache
from . import _CurricularUnit
from . import exams as _exams
from . import _Teacher

__all__ = ["Course"]

class Course:
    """This class represents a course as seen from its sigarra webpage.

    Properties:
        pv_curso_id      (int) # e.g. 742
        pv_ano_lectivo   (int) # e.g. 2018
        url              (str) # e.g. 'https://sigarra.up.pt/feup/en/cur_geral.cur_view?pv_curso_id=742&pv_ano_lectivo=2018'
        name             (str) # e.g. 'Master in Informatics and Computing Engineering'
        official_code    (int) # e.g. 9459
        directors        (tuple of Teacher objects) # e.g. (Teacher(210006), Teacher(209566))
        acronym          (str) # e.g. 'MIEIC'
        text             (str or None)

    Methods:
        from_url   (class method)
        from_a_tag (class method)
        classes
        curricular_units
        syllabus
    
    Operators:
        __repr__, __str__
        __eq__, __le__, __lt__, __ge__, __gt__ (Courses are sorted firstly by pv_curso_id and secondly by year)
        __hash__
    """
    __slots__ = ["pv_curso_id","pv_ano_lectivo", "url", "name", "official_code", "directors", "acronym", "text"]

    def __init__(self, pv_curso_id : int, pv_ano_lectivo : int = None, use_cache : bool = True):
        """Parses the webpage of the course with the given pv_curso_id.
        If a pv_ano_lectivo (e.g. 2019) is not used, the current academic year will be used.
        The cache can be bypassed by setting use_cache to False.
        """
        
        if pv_ano_lectivo == None:
            pv_ano_lectivo = _utils.get_current_academic_year()

        self.pv_curso_id    = pv_curso_id
        self.pv_ano_lectivo = pv_ano_lectivo

        payload = {
            "pv_curso_id"    : str(pv_curso_id),
            "pv_ano_lectivo" : str(pv_ano_lectivo)
        }
        self.url = _utils.SIG_URLS["course"] + "?" + _urllib.parse.urlencode(payload)
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Course/Cycle of Studies nonexistent." in html or "The Organic Unit is not involved in teaching the course/CS." in html:
            raise ValueError(f"Course with pv_curso_id {pv_curso_id} and pv_ano_lectivo {pv_ano_lectivo} doesn't exist")
       
        contents = soup.find("div", {"id" : "conteudoinner"})

        self.name = contents.find_all("h1")[1].string

        info_box = contents.find("div", {"class" : "caixa-informativa"})

        directors_ids = _re.findall(r"vld_entidades_geral.entidade_pagina\?pct_codigo=(\d+)", html)
        self.directors  = tuple(_Teacher.Teacher(int(_id)) for _id in directors_ids)

        for row in info_box.find_all("tr"):
            if "Acronym:" in str(row):
                self.acronym = row.find_all("td")[1].string
            
            elif "Official Code:" in str(row):
                self.official_code = int(row.find_all("td")[1].string)
        
        try:
            self.text = contents.find("div", {"class" : "col-md-8 col-sm-6 col-xs-12"}).text
        except:
            self.text = None


    def classes(self, credentials : _Credentials.Credentials) -> dict:
        """Returns a dictionary which maps the courses' classes
        to their corresponding timetable links.
        Example:
            {'1MIEIC01':'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000001&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC02': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000002&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC03': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000003&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC04': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000004&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC05': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000005&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC06': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000006&pv_periodos=1&pv_ano_lectivo=2018',
            ...                                                                                                                   }
        You may be interested on the functions provided by timetable.py
        """

        payload = {
            "pv_curso_id"    : str(self.pv_curso_id),
            "pv_ano_lectivo" : str(self.pv_ano_lectivo),
            "pv_periodos"    : "1" # All the classes in that year
        }

        html = credentials.get_html(_utils.SIG_URLS["course classes"], payload)
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Não existem dados para este ano letivo." in html:
            raise ValueError("No classes were available to be parsed")

        classes_tags = soup.find_all("a", {"class" : "t"})

        return {tag.string : _utils.BASE_URL_PT + tag["href"] for tag in classes_tags}


    def curricular_units(self, use_cache : bool = True) -> tuple:
        """Returns a tuple of CurricularUnit objects representing
        the curricular units of the course. Curricular units without
        a link are not included.
        Example:
            (CurricularUnit(419981),
             CurricularUnit(419982),
             CurricularUnit(419983),
             CurricularUnit(419984),
             CurricularUnit(419985),
             CurricularUnit(419986),
             CurricularUnit(419987),
             CurricularUnit(419988),
             CurricularUnit(419989),
             CurricularUnit(419990),
             CurricularUnit(419991),
             CurricularUnit(419992),
             CurricularUnit(419993),
             CurricularUnit(419994),
             CurricularUnit(419995),
             CurricularUnit(419996),
             ...                   )
        """
        html = _cache.get_html(self.url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        for tag in soup.find_all("a"):
            if "cur_geral.cur_planos_estudos_view" in str(tag):
                url = _utils.BASE_URL + tag["href"]
                break
        else:
            raise ValueError("No study plan link was found on the course page")
        
        html = _cache.get_html(url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        curricular_units_tags = (tag for tag in soup.find_all("a") if "ucurr_geral.ficha_uc_view" in str(tag))
        curricular_units_urls = [_utils.BASE_URL + tag["href"] for tag in curricular_units_tags]

        # The following block of code assynchronously loads both the curricular units' and the teachers' webpages
        teachers_urls = []
        for uc_html in _cache.get_html_async(curricular_units_urls, use_cache = use_cache):
            uc_soup = _bs4.BeautifulSoup(uc_html, "lxml")

            for tag in uc_soup.find_all("a"):
                if "func_geral.formview" in str(tag):
                    teachers_urls.append(_utils.BASE_URL + tag["href"])
        _cache.get_html_async(teachers_urls, use_cache = use_cache)

        return tuple(set(_CurricularUnit.CurricularUnit.from_url(url) for url in curricular_units_urls))

    
    def syllabus(self, use_cache : bool = True) -> list:
        """Returns a list of tuples.
        Example of a tuple:
        (
            'Software Engineering', # keyword (str)
            None,                   # branch (either str or None, depending on whether or not the curricular unit belongs to a specific branch)
            CurricularUnit(420015), # the curricular unit (CurricularUnit)
            True                    # whether or not it is mandatory (bool)
        )

        Example of the output:
        [
            ('Automation', 'Automation', CurricularUnit(418771), False),
            ('Automation', 'Automation', CurricularUnit(418770), False),
            ('Automation', 'Automation', CurricularUnit(418737), True),
            ('Automation', 'Automation', CurricularUnit(418746), True),
            ('Automation', 'Automation', CurricularUnit(418747), False),
            ('Automation', 'Automation', CurricularUnit(418736), True),
            ('Automation', 'Thermal Energy', CurricularUnit(418773), False),
            ('Automation', 'Thermal Energy', CurricularUnit(418736), False),
            ('Automation', 'Production Management', CurricularUnit(418773), False),
            ('Automation', 'Production Management', CurricularUnit(418736), False),
            ('Automation', 'Production, Conception and Manufacturing', CurricularUnit(418773), False),
            ('Automation', 'Structural Engineering and Machine Design', CurricularUnit(418736), False),
            ('Automation', None, CurricularUnit(418722), True),
            ('Personal and Interpersonal Skills', 'Automation', CurricularUnit(418787), False),
            ...
        ]
        """

        html = _cache.get_html(self.url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        for tag in soup.find_all("a"):
            if "cur_geral.cur_planos_estudos_view" in str(tag):
                url = _utils.BASE_URL + tag["href"]
                break
        else:
            raise ValueError("No study plan link was found on the course page")
        
        html = _cache.get_html(url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        code_to_uc = {uc.code : uc for uc in self.curricular_units(use_cache = use_cache)}
        result = []

        tables = soup.find_all("table", {"class" : "dados"})

        for table in tables:
            for row in table.find_all("tr")[1:]: # Ignore the header row
                
                keyword, branch, code, acronym, name, _credits, mandatory = (tag.string for tag in row.find_all("td"))

                try:
                    result.append((keyword, branch, code_to_uc[code], "Yes" in str(mandatory)))
                except KeyError: # The curricular unit doesn't have a page
                    continue
        
        return result

    def exams(self, use_cache : bool = False):
        """Returns a tuple of dictionaries (See exams.exams() for further information)"""
        url = _utils.SIG_URLS["curricular unit exams"] + "?" + _urllib.parse.urlencode({"p_curso_id" : str(self.pv_curso_id)})

        return _exams.exams(url, use_cache)


    @classmethod
    def from_url(cls, url : str, use_cache : bool = True):
        """Scrapes the course webpage from the given url and returns a Course object"""
        
        try:
            pv_curso_id    = int(_re.findall(r"pv_curso_id=(\d+)"   , url)[0])
            pv_ano_lectivo = int(_re.findall(r"pv_ano_lectivo=(\d+)", url)[0])
        except:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid course url")

        return Course(pv_curso_id, pv_ano_lectivo, use_cache)


    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True):
        """Scrapes the course webpage from the given anchor tag and returns a Course object"""
        
        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return Course.from_url(bs4_tag["href"], use_cache)

    
    # Comparisons between curricular units are made with the pv_curso_id and pv_ano_lectivo
    def _unique_value(self):
        return self.pv_curso_id * 10000 + self.pv_ano_lectivo

    def __eq__(self, other):
        if isinstance(other, Course):
            return self._unique_value() == other._unique_value()
        else:
            return NotImplementedError
        
    def __gt__(self, other):
        if isinstance(other, Course):
            return self._unique_value() > other._unique_value()
        else:
            return NotImplementedError
    
    def __ge__(self, other):
        if isinstance(other, Course):
            return self._unique_value() >= other._unique_value()
        else:
            return NotImplementedError
    
    def __lt__(self, other):
        if isinstance(other, Course):
            return self._unique_value() < other._unique_value()
        else:
            return NotImplementedError
    
    def __le__(self, other):
        if isinstance(other, Course):
            return self._unique_value() <= other._unique_value()
        else:
            return NotImplementedError
    
    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}

    def __hash__(self):
        return hash(self._unique_value())
    
    def __repr__(self):
        return f"Course({self.pv_curso_id}, {self.pv_ano_lectivo})"
    
    def __str__(self):
        return f"{self.acronym} ({self.pv_ano_lectivo}/{self.pv_ano_lectivo + 1})"
