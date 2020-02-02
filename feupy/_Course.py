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

    Args:
        pv_curso_id (int): The id of the course, for example MIEIC's id is 742
        pv_ano_lectivo (:obj:`int`, optional): The year of this course. It defaults to the current year (i.e. 2019, at the time of writing)
        use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
        base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")

    Attributes:
        pv_curso_id            (int): The id of the course
        pv_ano_lectivo         (int): The year of this course's page
        url                    (str): Url of the course's sigarra page
        name                   (str): The name the course
        official_code          (str): The official code
        directors              (tuple(:obj:`Teacher`)): The directors of this course
        acronym                (str): The acronym of this course
        text                   (str or None): The text that can be found in the course's page
        base_url               (str): The url of the course's faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        involved_organic_units (tuple(str)): All the faculties involved with this course

    Example::

        from feupy import Course

        mieic = Course(742)

        print(mieic.name)
        # Master in Informatics and Computing Engineering

        print(mieic.acronym)
        # MIEIC

        for director in mieic.directors:
            print(director.name)
        # João Carlos Pascoal Faria
        # Maria Cristina de Carvalho Alves Ribeiro
    """
    __slots__ = ["pv_curso_id","pv_ano_lectivo", "url", "name", "official_code", "directors", "acronym", "text", "base_url", "involved_organic_units"]

    def __init__(self, pv_curso_id : int, pv_ano_lectivo : int = None, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        
        if pv_ano_lectivo == None:
            pv_ano_lectivo = _utils.get_current_academic_year()

        self.pv_curso_id    = pv_curso_id
        self.base_url = base_url
        self.pv_ano_lectivo = pv_ano_lectivo

        payload = {
            "pv_curso_id"    : str(pv_curso_id),
            "pv_ano_lectivo" : str(pv_ano_lectivo)
        }
        self.url = self.base_url + _utils.SIG_URLS["course"] + "?" + _urllib.parse.urlencode(payload)
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Course/Cycle of Studies nonexistent." in html or "The Organic Unit is not involved in teaching the course/CS." in html:
            raise ValueError(f"Course with pv_curso_id {pv_curso_id} and pv_ano_lectivo {pv_ano_lectivo} doesn't exist")
       
        contents = soup.find("div", {"id" : "conteudoinner"})

        self.name = contents.find_all("h1")[1].string

        info_box = contents.find("div", {"class" : "caixa-informativa"})

        directors_ids = _re.findall(r"vld_entidades_geral.entidade_pagina\?pct_codigo=(\d+)", html)
        self.directors  = tuple(_Teacher.Teacher(int(_id), base_url = self.base_url) for _id in directors_ids)

        for row in info_box.find_all("tr"):
            if "Acronym:" in str(row):
                self.acronym = row.find_all("td")[1].string
            
            elif "Official Code:" in str(row):
                self.official_code = row.find_all("td")[1].string
        
        try:
            self.text = contents.find("div", {"class" : "col-md-8 col-sm-6 col-xs-12"}).text
        except:
            self.text = None
        
        for h3 in soup.find_all("h3"):
            if h3.text == "Involved Organic Units":
                involved_organic_units = []

                div = h3.find_next("div")
                for a in div.find_all("a"):
                    # I'm well aware that hardcoding values is not good practice.
                    # However, trying to follow all the redirects has turned out to be rather unfeasable.
                    # Trust me, I tried and thoroughly failed:(
                    # If you think you can do better, PRs are always welcome:)

                    if "href" not in a.attrs:
                        continue

                    if   "letras.up.pt" in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/flup/en/")
                    elif "fe.up.pt"     in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/feup/en/")
                    elif "fep.up.pt"    in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/fep/en/")
                    elif "fba.up.pt"    in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/fbaup/en/")
                    elif "icbas.up.pt"  in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/icbas/en/")
                    elif "fc.up.pt"     in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/fcup/en/")
                    elif "fa.up.pt"     in a["href"]:
                        involved_organic_units.append("https://sigarra.up.pt/faup/en/")
                
                self.involved_organic_units = tuple(involved_organic_units)
                break
        else:
            self.involved_organic_units = (self.base_url,)

    def classes(self, credentials : _Credentials.Credentials) -> dict:
        """Returns a dictionary which maps the course's classes
        to their corresponding timetable links.

        Args:
            credentials (:obj:`Credentials`): A :obj:`Credentials` object
        
        Returns:
            A dictionary
        
        Example::

            from feupy import Course, Credentials
            from pprint import pprint

            mieic = Course(742)

            creds = Credentials()

            pprint(mieic.classes(creds))

            # You will get something like this:
            {'1MIEIC01':'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000001&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC02': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000002&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC03': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000003&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC04': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000004&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC05': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000005&pv_periodos=1&pv_ano_lectivo=2018',
            '1MIEIC06': 'https://sigarra.up.pt/feup/pt/hor_geral.turmas_view?pv_turma_id=000006&pv_periodos=1&pv_ano_lectivo=2018',
            ...                                                                                                                   }
        
        You can use the functions provided by :doc:`timetable` to get the timetables from the urls.
        """

        payload = {
            "pv_curso_id"    : str(self.pv_curso_id),
            "pv_ano_lectivo" : str(self.pv_ano_lectivo),
            "pv_periodos"    : "1" # All the classes in that year
        }

        html = self.base_url.replace("/en/", "/pt/") + credentials.get_html(_utils.SIG_URLS["course classes"], payload)
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Não existem dados para este ano letivo." in html:
            raise ValueError("No classes were available to be parsed")

        classes_tags = soup.find_all("a", {"class" : "t"})

        return {tag.string : self.base_url.replace("/en/", "/pt/") + tag["href"] for tag in classes_tags}


    def curricular_units(self, use_cache : bool = True) -> list:
        """Returns a list of :obj:`CurricularUnit` objects representing
        the curricular units of the course. Curricular units without
        a link are not included.
        
        Args:
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra

        Returns:
            A list of :obj:`CurricularUnit` objects


        Example::

            from feupy import Course
            from pprint import pprint

            mieic = Course(742)

            pprint(mieic.curricular_units())

            # You will get something like this:
            [CurricularUnit(419981),
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
             ...                   ]
        """
        html = _cache.get_html(self.url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        for tag in soup.find_all("a"):
            if "cur_geral.cur_planos_estudos_view" in str(tag):
                url = self.base_url + tag["href"]
                break
        else:
            raise ValueError("No study plan link was found on the course page")
        
        html = _cache.get_html(url, use_cache = use_cache)
        soup = _bs4.BeautifulSoup(html, "lxml")

        curricular_units_tags = (tag for tag in soup.find_all("a") if "ucurr_geral.ficha_uc_view" in str(tag))
        curricular_units_urls = [self.base_url + tag["href"] for tag in curricular_units_tags]

        # The following block of code assynchronously loads both the curricular units' and the teachers' webpages
        teachers_urls = []
        for uc_html in _cache.get_html_async(curricular_units_urls, use_cache = use_cache):
            uc_soup = _bs4.BeautifulSoup(uc_html, "lxml")

            for tag in uc_soup.find_all("a"):
                if "func_geral.formview" in str(tag):
                    teachers_urls.append(self.base_url + tag["href"])
        _cache.get_html_async(teachers_urls, use_cache = use_cache)

        res = set()
        for url in curricular_units_urls:
            try:
                res.add(_CurricularUnit.CurricularUnit.from_url(url, base_url = self.base_url))

            except ValueError as e:
                # It is possible that Sigarra can have dead links in the study plan
                if "Curricular unit with pv_ocorrencia_id" not in str(e):
                    raise e

        return list(res)

    
    def syllabus(self, use_cache : bool = True) -> list:
        """Returns a list of tuples containing more information about the curricular units of the course.
        
        Each tuple has 4 elements:
            0. keyword (str)
            1. course branch (either str or None, depending on whether or not the curricular unit belongs to a specific branch)
            2. curricular unit (:obj:`CurricularUnit`)
            3. is mandatory (bool)
        
        Args:
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra

        Returns:
            A list of tuples

        Example::

            from feupy import Course
            from pprint import pprint

            miem = Course(743)

            pprint(miem.syllabus())

            # You will get something like this:
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
                url = self.base_url + tag["href"]
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

    def exams(self, use_cache : bool = True) -> list:
        """Returns a list of the exams of this course.
        
        Args:
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra

        Returns:
            A list of dictionaries (see :func:`exams.exams` for more information about the dictionaries)
        """
        res = []
        
        for faculty_url in self.involved_organic_units:
            url = faculty_url.replace("/en/", "/pt/") +\
                  _utils.SIG_URLS["course exams"] + "?" +\
                  _urllib.parse.urlencode({"p_curso_id" : str(self.pv_curso_id)})
            
            res.extend(_exams.exams(url, use_cache, faculty_url))

        return res


    @classmethod
    def from_url(cls, url : str, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the course webpage from the given url and returns a :obj:`Course` object.

        Args:
            url (str): The url of the course's sigarra page
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Course` object

        Example::
        
            from feupy import Course

            url = "https://sigarra.up.pt/feup/pt/cur_geral.cur_view?pv_curso_id=742&pv_ano_lectivo=2018"
            mieic = Course.from_url(url)

            print(mieic.name)
            # Master in Informatics and Computing Engineering
        """

        try:
            pv_curso_id    = int(_re.findall(r"pv_curso_id=(\d+)"   , url)[0])
            pv_ano_lectivo = int(_re.findall(r"pv_ano_lectivo=(\d+)", url)[0])
        except:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid course url")

        matches = _re.findall(r"^https?://sigarra\.up\.pt/(\w+)/", url)
        if len(matches) == 1:
            base_url = f"https://sigarra.up.pt/{matches[0]}/en/"

        return Course(pv_curso_id, pv_ano_lectivo, use_cache, base_url = base_url)


    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the course webpage from the given :obj:`bs4.tag` object and returns a :obj:`Course` object.
        
        Args:
            bs4_tag (:obj:`bs4.tag`):
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Course` object
        """

        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return Course.from_url(bs4_tag["href"], use_cache, base_url = base_url)

    
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
        if self.base_url == "https://sigarra.up.pt/feup/en/":
            return f"Course({self.pv_curso_id}, {self.pv_ano_lectivo})"
        else:
            return f"Course({self.pv_curso_id}, {self.pv_ano_lectivo}, base_url = {self.base_url})"
    
    def __str__(self):
        return f"{self.acronym} ({self.pv_ano_lectivo}/{self.pv_ano_lectivo + 1})"
