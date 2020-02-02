import re as _re
import urllib as _urllib

import bs4 as _bs4
import PIL as _PIL

from . import _internal_utils as _utils
from . import cache as _cache

__all__ = ["Teacher"]

class Teacher:
    """This class represents a FEUP teacher as seen from their sigarra webpage.

    Note:
        Some attributes may be set to None, depending on whether or not
        that attribute was able to be parsed. For example: personal_webpage, email, and
        presentation are not always available in teacher pages.

    Args:
        p_codigo (int): The id of the teacher
        use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
        base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")


    Attributes:
        p_codigo         (int): The id of the teacher
        name             (str): The name of the teacher
        acronym          (str): The acronym of the teacher
        status           (str): The status of the teacher
        links            (tuple(str)): Urls from the teacher page (including :any:`Teacher.personal_webpage`, if present)
        personal_webpage (str): Url of the teacher's personal page
        url              (str): Url of the teacher's sigarra page
        voip             (int)
        email            (str)
        rooms            (str)
        category         (str)
        career           (str)
        profession       (str)
        department       (str)
        presentation     (str): The presentation of this teacher
        base_url         (str): The url of the teacher's faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")

    Example::

        from feupy import Teacher

        jlopes = Teacher(230756)

        print(jlopes.name)
        # João António Correia Lopes

        print(jlopes.acronym)
        # JCL

        print(jlopes.personal_webpage)
        # http://www.fe.up.pt/~jlopes/
    """
    __slots__ = ["p_codigo", "name", "acronym", "status", "links", "personal_webpage", "url", "voip",
                 "email", "rooms", "category", "career", "profession", "department", "presentation", "base_url"]

    def __init__(self, p_codigo : int, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):

        for attribute in self.__slots__:
            setattr(self, attribute, None)

        self.p_codigo = p_codigo
        self.base_url = base_url
        self.url = self.base_url + _utils.SIG_URLS["teacher"] + "?" + _urllib.parse.urlencode({"p_codigo" : str(p_codigo)})
        
        html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
        soup = _bs4.BeautifulSoup(html, "lxml")

        if "O funcionário indicado não foi encontrado." in html:
            # The teacher's page is not here
            # Maybe it could be in another faculty?
            try:
                html = _cache.get_html(url = self.base_url + _utils.SIG_URLS["redirection page"] + "?" + _urllib.parse.urlencode({"pct_codigo" : str(p_codigo)}), use_cache = use_cache)
                soup = _bs4.BeautifulSoup(html, "lxml")
                self.url = soup.find("a")["href"]
                #########################
                if "/pt/" in self.url:
                    self.url = self.url.replace("/pt/", "/en/") # I want the page in english
                else:
                    index = self.url.index(_utils.SIG_URLS["teacher"])
                    self.url = self.url[:index] + "en/" + self.url[index:]
                #########################
                index = self.url.index(_utils.SIG_URLS["teacher"])
                self.base_url = self.url[:index]

                html = _cache.get_html(url = self.url, use_cache = use_cache) # Getting the html
                soup = _bs4.BeautifulSoup(html, "lxml")
            except:
                raise ValueError(f"Teacher with p_codigo {p_codigo} doesn't exist")

        personal_info = soup.find("div", {"class" : "informacao-pessoal-dados-dados"})

        for row in personal_info.find_all("tr"):
            if "Name:" in str(row):
                self.name = row.find_all("td")[1].b.string

                if row.find("a") != None:
                    self.personal_webpage = row.a["href"]
            
            elif "Acronym:" in str(row) or "Sigla:" in str(row):
                self.acronym = row.find_all("td")[1].string
            
            elif "Status:" in str(row) or "Estado:" in str(row):
                self.status = row.find_all("td")[1].string

            elif "Institutional E-mail:" in str(row) or "Email" in str(row):
                self.email = row.a.contents[0] + "@" + row.a.contents[-1]
                
            elif "Voip:" in str(row):
                self.voip = int(row.find_all("td")[1].string)

            elif "Rooms:" in str(row) or "Salas:" in str(row):
                self.rooms = row.find_all("td")[1].a.string

        self.links = tuple(tag["href"] for tag in soup.find("table", {"class" : "tabelasz"}).find_all("a"))

        functions_div = soup.find("div", {"class" : "informacao-pessoal-funcoes"})

        for td in functions_div.find_all("td", {"class" : "topo"}):

            if "Department:" in str(td):

                for row in td.find_all("tr"):
                    if "Category:" in str(row) or "Categoria:" in str(row):
                        self.category = row.find_all("td")[1].string
                    
                    elif "Career:" in str(row) or "Carreira:" in str(row):
                        self.career = row.find_all("td")[1].string

                    elif "Professional Group:" in str(row):
                        self.profession = row.find_all("td")[1].string
                    
                    elif "Department:" in str(row):
                        self.department = row.find_all("td")[1].string.strip()
                
                break
            
        
        personal_presentation = soup.find("div", {"class" : "informacao-pessoal-apresentacao"})

        if personal_presentation != None:
            self.presentation = personal_presentation.text.strip()
    
    def picture(self) -> _PIL.Image.Image:
        """Returns a picture of the teacher as a :obj:`PIL.Image.Image` object.
        
        Returns:
            A :obj:`PIL.Image.Image` object
        """
        return _utils.get_image(self.base_url + _utils.SIG_URLS["picture"], {"pct_cod" : str(self.p_codigo)})

    @classmethod
    def from_url(cls, url : str, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the teacher webpage from the given url and returns a :obj:`Teacher` object.

        Args:
            url (str): The url of the teacher's sigarra page
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Teacher` object

        Example::
        
            from feupy import Teacher

            url = "https://sigarra.up.pt/feup/en/func_geral.formview?p_codigo=230756"
            jlopes = Teacher.from_url(url)

            print(jlopes.name)
            # João António Correia Lopes
        """        
        matches = _re.findall(r"p_codigo=(\d+)$", url)
        
        if len(matches) == 0:
            raise ValueError(f"from_url() 'url' argument \"{url}\" is not a valid teacher url")
        
        p_codigo = int(matches[0])

        matches = _re.findall(r"^https?://sigarra\.up\.pt/(\w+)/", url)
        if len(matches) == 1:
            base_url = f"https://sigarra.up.pt/{matches[0]}/en/"

        return Teacher(p_codigo, use_cache, base_url = base_url)
    
    @classmethod
    def from_a_tag(cls, bs4_tag : _bs4.Tag, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/"):
        """Scrapes the teacher webpage from the given :obj:`bs4.tag` object and returns a :obj:`Teacher` object.
        
        Args:
            bs4_tag (:obj:`bs4.tag`):
            use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra
            base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
        
        Returns:
            A :obj:`Teacher` object
        """

        if bs4_tag.name != "a":
            raise ValueError(f"from_a_tag() 'bs4_tag' argument must be an anchor tag, not '{bs4_tag.name}'")
        
        return Teacher.from_url(bs4_tag["href"], use_cache, base_url = base_url)
    
    
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
        if self.base_url == "https://sigarra.up.pt/feup/en/":
            return f"Teacher({self.p_codigo})"
        else:
            return f"Teacher({self.p_codigo}, base_url = {self.base_url})"
    
    def __str__(self):
        return f"{self.name} ({self.acronym})"
