import re as _re
import urllib as _urllib

import bs4 as _bs4
import PIL as _PIL

from . import _internal_utils as _utils
from . import cache as _cache

__all__ = ["Teacher"]

class Teacher:
    """This class represents a FEUP teacher as seen from their sigarra webpage.

    Please note that some attributes may be set to None, depending on whether or not
    that attribute was able to be parsed. For example: personal_webpage, email, and
    presentation are not always available in teacher pages.

    Properties:
        p_codigo         (int) # e.g. 230756
        name             (str) # e.g. 'João António Correia Lopes'
        acronym          (str) # e.g. 'JCL'
        status           (str) # e.g. 'Active'
        links            (tuple of strings) # e.g. ('http://www.fe.up.pt/~jlopes/', 'https://www.authenticus.pt/R-000-6RX', 'http://orcid.org/0000-0002-9040-0889')
        personal_webpage (str) # e.g. 'http://www.fe.up.pt/~jlopes/'
        url              (str) # e.g. 'https://sigarra.up.pt/feup/en/func_geral.formview?p_codigo=230756'
        voip             (int) # e.g. 3375
        email            (str) # e.g. None (This particular attribute could not be parsed from the page)
        rooms            (str) # e.g. 'I129'
        category         (str) # e.g. 'Professor Auxiliar'
        career           (str) # e.g. 'Pessoal Docente de Universidades'
        profession       (str) # e.g. 'Docente'
        department       (str) # e.g. 'Department of Informatics Engineering'
        presentation     (str) # e.g. 'Personal Presentation\\nJoão Correia Lopes is an Assistant Professor in Informatics Engineering...'

    Methods:
        from_url   (class method)
        from_a_tag (class method)
        picture
    
    Operators:
        __repr__, __str__
        __eq__, __le__, __lt__, __ge__, __gt__ (Comparisons between teachers and hashing are made with the p_codigo)
        __hash__
    """
    __slots__ = ["p_codigo", "name", "acronym", "status", "links", "personal_webpage", "url", "voip",
                 "email", "rooms", "category", "career", "profession", "department", "presentation"]

    def __init__(self, p_codigo : int, use_cache : bool = True):
        """Parses the webpage of the teacher with the given p_codigo.
        The cache can be bypassed by setting use_cache to False.
        If a given attribute can't be parsed (or is nonexistent),
        it will be set to None.
        """

        for attribute in self.__slots__:
            setattr(self, attribute, None)

        self.p_codigo = p_codigo
        self.url = _utils.SIG_URLS["teacher"] + "?" + _urllib.parse.urlencode({"p_codigo" : str(p_codigo)})
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "O funcionário indicado não foi encontrado." in html:
            raise ValueError(f"Teacher with p_codigo {p_codigo} doesn't exist")
        
        personal_info = soup.find("div", {"class" : "informacao-pessoal-dados-dados"})

        for row in personal_info.find_all("tr"):
            if "Name:" in str(row):
                self.name = row.find_all("td")[1].b.string

                if row.find("a") != None:
                    self.personal_webpage = row.a["href"]
            
            elif "Acronym:" in str(row):
                self.acronym = row.find_all("td")[1].string
            
            elif "Status:" in str(row):
                self.status = row.find_all("td")[1].string

            elif "Institutional E-mail:" in str(row):
                self.email = row.a.contents[0] + "@" + row.a.contents[-1]
                
            elif "Voip:" in str(row):
                self.voip = int(row.find_all("td")[1].string)

            elif "Rooms:" in str(row):
                self.rooms = row.find_all("td")[1].a.string

        self.links = tuple(tag["href"] for tag in soup.find("table", {"class" : "tabelasz"}).find_all("a"))

        functions_div = soup.find("div", {"class" : "informacao-pessoal-funcoes"})

        for td in functions_div.find_all("td", {"class" : "topo"}):

            if "Department:" in str(td):

                for row in td.find_all("tr"):
                    if "Category:" in str(row):
                        self.category = row.find_all("td")[1].string
                    
                    elif "Career:" in str(row):
                        self.career = row.find_all("td")[1].string

                    elif "Professional Group:" in str(row):
                        self.profession = row.find_all("td")[1].string
                    
                    elif "Department:" in str(row):
                        self.department = row.find_all("td")[1].string.strip()
                
                break
            
        
        personal_presentation = soup.find("div", {"class" : "informacao-pessoal-apresentacao"})

        if personal_presentation != None:
            self.presentation = personal_presentation.text.strip()
    
    def picture(self) -> _PIL.Image:
        """Returns a picture of the teacher as a PIL.Image object"""
        return _utils.get_image(_utils.SIG_URLS["picture"], {"pct_cod" : str(self.p_codigo)})

    @classmethod
    def from_url(cls, url : str, use_cache : bool = True):
        """Scrapes the teacher webpage from the given url and returns a Teacher object"""
        
        matches = _re.findall(r"p_codigo=(\d+)$", url)
        
        if len(matches) == 0:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid teacher url")
        
        p_codigo = int(matches[0])

        return Teacher(p_codigo, use_cache)
    
    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True):
        """Scrapes the teacher webpage from the given anchor tag and returns a Teacher object"""
        
        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return Teacher.from_url(bs4_tag["href"], use_cache)
    
    
    # Comparisons between teachers are made with the p_codigo
    def __eq__(self, other):
        if isinstance(other, Teacher):
            return self.p_codigo == other.p_codigo
        else:
            return NotImplementedError
        
    def __gt__(self, other):
        if isinstance(other, Teacher):
            return self.p_codigo > other.p_codigo
        else:
            return NotImplementedError
    
    def __ge__(self, other):
        if isinstance(other, Teacher):
            return self.p_codigo >= other.p_codigo
        else:
            return NotImplementedError
    
    def __lt__(self, other):
        if isinstance(other, Teacher):
            return self.p_codigo < other.p_codigo
        else:
            return NotImplementedError
    
    def __le__(self, other):
        if isinstance(other, Teacher):
            return self.p_codigo <= other.p_codigo
        else:
            return NotImplementedError
    
    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}

    def __hash__(self):
        return hash(self.p_codigo)
    
    def __repr__(self):
        return f"Teacher({self.p_codigo})"
    
    def __str__(self):
        return f"{self.name} ({self.acronym})"
