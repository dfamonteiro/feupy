import re as _re
import urllib as _urllib

import bs4 as _bs4

from . import _Credentials
from . import _internal_utils as _utils
from . import _Course
from . import cache as _cache

__all__ = ["Student"]

class Student:
    """This class represents a FEUP student as seen from their sigarra webpage.

    Args:
        username (int): The username of the student, e.g. 201806185
        use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
        base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")

    
    Attributes:
        name             (str): The name of the student
        links            (tuple(str)): Urls from the student page (including :any:`Student.personal_webpage`, if present)
        personal_webpage (str): Url of the student's personal page, if present. Otherwise it is set to None
        username         (int): The student's "pv_num_unico"
        url              (str): Url of the student's sigarra page
        base_url         (str): The url of the student's faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        courses          (tuple(dict)): The courses this student is enrolled in
    
        Each dictionary from the courses tuple has 3 keys:
            - "course"              (a :obj:`Course` object or a string (if a link to a course wasn't available))
            - "first academic year" (int): if your first year is 2019/2020, then "first academic year" will be 2019
            - "institution"         (string)
    
    Example::
        
        from feupy import Student

        daniel = Student(201806185)

        print(daniel.name)
        # Daniel Filipe Amaro Monteiro

        print(daniel.username)
        # 201806185

        print(daniel.courses)
        # ({'course': Course(742, 2019), 'institution': 'Faculty of Engineering', 'first academic year': 2018},)
    """

    __slots__ = ["name", "links", "personal_webpage", "username", "courses", "url", "base_url"]

    def __init__(self, username : int, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):

        self.username = username
        self.base_url = base_url
        self.url = self.base_url + _utils.SIG_URLS["student page"] + "?" + _urllib.parse.urlencode({"pv_num_unico" : str(username)})
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "Estudante não encontrado." in html:
            raise ValueError(f"Student with username '{username}' doesn't exist")
        
        if "Problem found" in html: # the only info we can get is the name (I don't think it's even the entire name)
            content_soup = soup.find("div", {"id" : "conteudoinner"})
            self.name = content_soup.contents[5].string

            self.links = () # empty tuple
            self.personal_webpage = None
            self.courses = ()

            return
        
        # Otherwise, it's a normal student page

        self.name = soup.find("div", {"class" : "estudante-info-nome"}).string.strip()
        
        personal_webpage_div = soup.find("div", {"class" : "pagina-pessoal"})
        if personal_webpage_div == None:                              # Does the student have a webpage?
            self.personal_webpage = None
        else:
            self.personal_webpage = personal_webpage_div.a["href"]
        
        self.links = []
        username_link = soup.find("div", {"class" : "estudante-info-numero"})
        for div in username_link.find_next_siblings("div"):
            link = div.a
            if link == None:
                continue
            else:
                self.links.append(link["href"])
        self.links = tuple(self.links)
        
        self.courses = []
        for course_div in soup.find_all("div", {"class" : "estudante-lista-curso-activo"}): # Iterate over the courses "boxes"

            name_div = course_div.find("div", {"class" : "estudante-lista-curso-nome"})
            if name_div.a == None: # There is no link
                course = name_div.string
            else:
                course = _Course.Course.from_a_tag(name_div.a, use_cache, base_url = base_url) # If there is a link, get the Course object
            
            institution = course_div.find("div", {"class" : "estudante-lista-curso-instit"}).string

            first_academic_year = _utils.parse_academic_year(course_div)

            self.courses.append({"course" : course, "institution" : institution, "first academic year" : first_academic_year})
        self.courses = tuple(self.courses)

    @classmethod
    def from_url(cls, url : str, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the student webpage from the given url and returns a :obj:`Student` object.

        Args:
            url (str): The url of the student's sigarra page
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Student` object

        Example::
        
            from feupy import Student

            url = "https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico=201806185"
            daniel = Student.from_url(url)

            print(daniel.name)
            # Daniel Filipe Amaro Monteiro
        """
        
        matches = _re.findall(r"pv_num_unico=(\d+)$", url)
        
        if len(matches) == 0:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid student url")
        
        username = int(matches[0])

        matches = _re.findall(r"^https?://sigarra\.up\.pt/(\w+)/", url)
        if len(matches) == 1:
            base_url = f"https://sigarra.up.pt/{matches[0]}/en/"

        return Student(username, use_cache, base_url = base_url)
    
    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the student webpage from the given :obj:`bs4.tag` object and returns a :obj:`Student` object.
        
        Args:
            bs4_tag (:obj:`bs4.tag`):
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Student` object
        """
        
        if not isinstance(bs4_tag, _bs4.Tag):
            raise TypeError(f"from_a_tag() 'bs4_tag' argument must be a bs4.Tag, not '{type(bs4_tag).__name__}'")
        
        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return Student.from_url(bs4_tag["href"], use_cache, base_url = base_url)
    
    def full_info(self, credentials : _Credentials.Credentials) -> dict:
        """Returns a dictionary with the information that one can get when it is logged in.

        The dictionary has 7 keys:
            - "courses" (list(dict))
            - "email"   (str)
            - "links"   (tuple(str))
            - "name"    (str)
            - "personal_webpage" (str)
            - "url"     (str)
            - "username" (int)

        Args:
            credentials (:obj:`Credentials`): A :obj:`Credentials` object
        
        Returns:
            A dictionary

        Example::

            from feupy import Student, Credentials
            from pprint import pprint

            daniel = Student(201806185)

            creds = Credentials()

            pprint(daniel.full_info(creds))

            # You will get something like this:
            {'courses': [ # A list of dictionaries representing the courses' information
                         {'course': Course(742, 2019), # A Course object. If a link to an object isn't available, it's just a string
                          'current year': 2,   # Could be None if a number isn't present (or couldn't be parsed)
                          'first academic year': 2018,
                          'institution': 'Faculty of Engineering', # Best faculty
                          'status': 'A Frequentar'}],
            'email': 'up201806185@fe.up.pt',
            'links': (),                      # personal_webpage is included in links
            'name': 'Daniel Filipe Amaro Monteiro', # people tend to have a name
            'personal_webpage': None,
            'url': 'https://sigarra.up.pt/feup/en/fest_geral.cursos_list?pv_num_unico=201806185',
            'username': 201806185}
        """

        if not isinstance(credentials, _Credentials.Credentials):
            raise TypeError(f"full_info() 'credentials' argument must be a Credentials object, not '{type(credentials).__name__}'")
        
        info = {
            "name"             : self.name,
            "links"            : self.links,
            "personal_webpage" : self.personal_webpage,
            "username"         : self.username,
            "url"              : self.url
        }

        html = credentials.get_html(self.url)
        soup = _bs4.BeautifulSoup(html, "lxml")

        email_div = soup.find("div", {"class" : "email-institucional"})
        email = email_div.a.contents[0] + "@" + email_div.a.contents[-1]
        info["email"] = email

        courses = [_parse_course_box(div) for div in soup.find_all("div", {"class" : "estudante-lista-curso-activo"})]
        info["courses"] = courses

        return info
    
    # Comparisons between students are made with the username
    def __eq__(self, other):
        if isinstance(other, Student):
            return self.username == other.username
        else:
            return NotImplementedError
        
    def __gt__(self, other):
        if isinstance(other, Student):
            return self.username > other.username
        else:
            return NotImplementedError
    
    def __ge__(self, other):
        if isinstance(other, Student):
            return self.username >= other.username
        else:
            return NotImplementedError
    
    def __lt__(self, other):
        if isinstance(other, Student):
            return self.username < other.username
        else:
            return NotImplementedError
    
    def __le__(self, other):
        if isinstance(other, Student):
            return self.username <= other.username
        else:
            return NotImplementedError
    
    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}

    def __hash__(self):
        return hash(self.username)
    
    def __repr__(self):
        if self.base_url == "https://sigarra.up.pt/feup/en/":
            return f"Student({self.username})"
        else:
            return f"Student({self.username}, base_url = {self.base_url})"
    
    def __str__(self):
        return f"{self.name} ({self.username})"


def _parse_course_box(bs_course_div):
    """Parses the the information available in the "estudante-lista-curso-activo" div.
    NOTE: Doesn't work with unpriviledged access to the student page
    It returns a dictionary like this: 
    {
        "course" : Course,
        "institution" : str,
        "current year": int, (None if a number couldn't be parsed)
        "status"      : str,
        "first academic year" : int
    }
    """
    
    if not isinstance(bs_course_div, _bs4.BeautifulSoup) and not isinstance(bs_course_div, _bs4.element.Tag):
        raise TypeError(f"parse_course_box() 'bs_course_div' argument must either be a bs4.element.Tag or a bs4.BeautifulSoup, not '{type(bs_course_div).__name__}'")
    
    name_div = bs_course_div.find("div", {"class" : "estudante-lista-curso-nome"})
    if name_div.a == None:  # There is no link
        course = name_div.string
    else:
        course = _Course.Course.from_a_tag(name_div.a)
        
    institution = bs_course_div.find("div", {"class": "estudante-lista-curso-instit"}).string
    
    table = bs_course_div.find("table", {"class" : "formulario"})
    table_data = _utils.scrape_html_table(table)
            
    current_year, status, first_academic_year = [row[1] for row in table_data]
    
    try:
        current_year = int(current_year)
    except Exception:
        current_year = None
        
    # status is fine as it is
    
    first_academic_year = _utils.parse_academic_year(first_academic_year)
    
    result = {
        "course"              : course,
        "institution"         : institution,
        "current year"        : current_year,
        "status"              : status,
        "first academic year" : first_academic_year
    }
    
    return result
    
