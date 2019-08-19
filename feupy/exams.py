import datetime as _datetime

import bs4 as _bs4

from . import _internal_utils as _utils
from . import cache as _cache
from . import _CurricularUnit

__all__ = ["exams"]

def exams(url : str, use_cache : bool = False) -> tuple:
    """Returns a tuple made of dictionaries.
    Example of a dictionary:

        {'curricular unit': CurricularUnit(420037),
         'finish': datetime.datetime(2019, 9, 6, 20, 0),
         'observations': 'Tenho um exame de outra disciplina marcado para esse horário e assim juntava os dois.\\r\\nJosé Luís Moura Borges\\r\\n',
         'rooms': None, # A tuple of strings, if available
         'season': 'Especial de Conclusão - SET-E-ESPECIAL',
         'start': datetime.datetime(2019, 9, 6, 17, 0)}
     
    If a value is not available (like 'rooms', in this case), it will be set to none.
    Important note: use_cache = True will only apply to the exams pages, not the curricular units in those exams pages.
    """
    html = _cache.get_html(url, use_cache = use_cache)
    soup = _bs4.BeautifulSoup(html, 'lxml')
    content = soup.find("div", {"id" : "conteudoinner"})

    tags = [tag for tag in content.find_all("a")]
    tags.pop(0)

    urls = [_utils.BASE_URL_PT + tag["href"] for tag in tags if "exa_geral.exame_view" in tag["href"]]
    _cache.get_html_async(urls, use_cache = use_cache) # Refresh the cache
    return tuple(_parse_exam_page(url) for url in urls)

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

    length_hour, length_minute = map(int, length.find_all("td")[1].string.split(":"))

    delta = _datetime.timedelta(hours = length_hour, minutes = length_minute)

    finish = start + delta

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
