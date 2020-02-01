import datetime as _datetime

import bs4 as _bs4

from . import cache as _cache
from . import _CurricularUnit

__all__ = ["exams"]

def exams(url : str, use_cache : bool = True, base_url : str = "https://sigarra.up.pt/feup/en/") -> list:
    """Returns a list of dictionaries.

    Each dictionary represents an exam and has 6 keys:

    =================== ==========================================================
     key                 value                                                    
    =================== ==========================================================
     "curricular unit"   (:obj:`feupy.CurricularUnit`) The subject being evaluated      
     "finish"            (:obj:`datetime.datetime`) The finish time of the exam   
     "observations"      (str)                                                    
     "rooms"             (tuple(str)) The rooms in which the exam will take place 
     "season"            (str)                                                    
     "start"             (:obj:`datetime.datetime`) The start time of the exam    
    =================== ==========================================================
    
    Note:
        If a value is not available, it will be set to None.
    
    Args:
        url       (str): The url of the page with the exams to be parsed
        use_cache (:obj:`bool`, optional): Attempts to use the cache if True, otherwise it will fetch from sigarra

    Returns:
        A list of dictionaries
    
    Example::

        from feupy.exams import exams
        from pprint import pprint

        mieic_exams_url = "https://sigarra.up.pt/feup/pt/exa_geral.mapa_de_exames?p_curso_id=742"

        pprint(exams(mieic_exams_url))
        # You'll get something like this:
        [{'curricular unit': CurricularUnit(420016),
        'finish': datetime.datetime(2019, 9, 4, 12, 0),
        'observations': 'Exame em comum com Mecanica.Exame em comum com o da Época '
                        'de Conclusão de Curso',
        'rooms': ('B222',),
        'season': 'Exames ao abrigo de estatutos especiais - Port.Est.Especiais 2ºS',
        'start': datetime.datetime(2019, 9, 4, 9, 0)},

        {'curricular unit': CurricularUnit(419990),
        'finish': datetime.datetime(2019, 9, 6, 17, 0),
        'observations': 'Sala de exame - Em principio 2 alunos ',
        'rooms': ('B222',),
        'season': 'Exames ao abrigo de estatutos especiais - Port.Est.Especiais 2ºS',
        'start': datetime.datetime(2019, 9, 6, 14, 0)},

        {'curricular unit': CurricularUnit(420021),
        'finish': datetime.datetime(2019, 9, 18, 17, 30),
        'observations': 'Sala de exame - possivelmente 3 alunos ',
        'rooms': None,
        'season': 'Exames ao abrigo de estatutos especiais - Port.Est.Especiais 2ºS',
        'start': datetime.datetime(2019, 9, 18, 14, 30)},

        {'curricular unit': CurricularUnit(438941),
        'finish': datetime.datetime(2019, 9, 25, 13, 0),
        'observations': None,
        'rooms': ('B104', 'B208', 'B213'),
        'season': 'Exames ao abrigo de estatutos especiais - Mini-testes (1ºS)',
        'start': datetime.datetime(2019, 9, 25, 9, 0)},

        {'curricular unit': CurricularUnit(438941),
        'finish': datetime.datetime(2019, 9, 25, 17, 30),
        'observations': None,
        'rooms': ('B104', 'B213', 'B208', 'B207'),
        'season': 'Exames ao abrigo de estatutos especiais - Mini-testes (1ºS)',
        'start': datetime.datetime(2019, 9, 25, 13, 30)},

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
    """
    html = _cache.get_html(url, use_cache = use_cache)
    soup = _bs4.BeautifulSoup(html, 'lxml')
    content = soup.find("div", {"id" : "conteudoinner"})

    tags = [tag for tag in content.find_all("a")]
    tags.pop(0)

    urls = [base_url.replace("/en/", "/pt/") + tag["href"] for tag in tags if "exa_geral.exame_view" in tag["href"]]
    _cache.get_html_async(urls, use_cache = use_cache) # Refresh the cache
    return [_parse_exam_page(url) for url in urls]

def _parse_exam_page(url : str):
    """Parses an exam page from the url and returns a dictionary"""

    html = _cache.get_html(url)
    soup = _bs4.BeautifulSoup(html, 'lxml')
    content = soup.find("div", {"id" : "conteudoinner"})
    table = content.find("table")

    rows = table.find_all("tr")

    code, _, season, date, start, length = rows[:6]

    curricular_unit = _CurricularUnit.CurricularUnit.from_a_tag(code.a)

    season = season.find_all("td")[1].string

    year, month, day = map(int, date.find_all("td")[1].string.split("-"))

    start_hour, start_minute = map(int, start.find_all("td")[1].string.split(":"))

    start = _datetime.datetime(year, month, day, start_hour, start_minute)

    try:
        length_hour, length_minute = map(int, length.find_all("td")[1].string.split(":"))

        delta = _datetime.timedelta(hours = length_hour, minutes = length_minute)

        finish = start + delta

    except AttributeError:
        finish = None

    rooms = observations = None
    for row in rows[6:]:
        if "Salas:" in str(row):
            rooms = tuple(tag.string for tag in row.find_all("a"))
        elif "Observações:" in str(row):
            observations = row.find_all("td")[1].string
    
    return {
        "curricular unit" : curricular_unit,
        "season"          : season,
        "start"           : start,
        "finish"          : finish,
        "rooms"           : rooms,
        "observations"    : observations
    }
