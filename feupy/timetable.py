import datetime as _datetime
import functools as _functools
import re as _re

import bs4 as _bs4

from . import _Credentials
from . import _internal_utils as _utils
from . import _CurricularUnit
from . import _Teacher

__all__ = ["parse_current_timetable", "parse_timetables", "parse_timetable"]

_weekdays = ("Monday", "Tuesday", "Wednesday",
             "Thursday", "Friday", "Saturday", "Sunday")

_weekdays_pt = ("Segunda", "Terça", "Quarta",
                "Quinta", "Sexta", "Sábado", "Domingo")

_weekdays_pt_to_en = {pt: en for pt, en in zip(_weekdays_pt, _weekdays)}


def parse_current_timetable(credentials: _Credentials.Credentials, url: str) -> list:
    """Attempts to parse the related timetable that is valid today.
    If no timetable is valid today, it returns None.
    (see parse_timetable for further info on the layout)
    """
    
    for (start, finish), url in _parse_side_bar(credentials, url).items():
        if start <= _datetime.date.today() <= finish:
            return parse_timetable(credentials, url)
    else:
        return None


def parse_timetables(credentials: _Credentials.Credentials, url: str) -> dict:
    """Parses the timetables related to this timetable (including).
    Returns a dictionary which maps a tuple with two datetime.date objects,
    start and finish (the time span in which this timetable is valid), to a
    list of dictionaries (see parse_timetable for further info).
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
    result = _parse_side_bar(credentials, url)

    for key in result:
        result[key] = parse_timetable(credentials, result[key])

    return result

def _parse_side_bar(credentials: _Credentials.Credentials, url: str) -> dict:
    """Returns a dictionary which maps a tuple with two datetime.date objects,
    start and finish, to a url of the corresponding timetable (string)"""
    html = credentials.get_html(url)
    soup = _bs4.BeautifulSoup(html, 'lxml')

    timetables_links_table = soup.find("table", {"class": "horario-semanas ecra"})

    if timetables_links_table == None:
        matches = _re.findall(r"Semanas de (\d\d)-(\d\d)-(\d\d\d\d) a (\d\d)-(\d\d)-(\d\d\d\d)", html)[0]
        start_day, start_month, start_year, finish_day, finish_month, finish_year  = map(int, matches)

        start = _datetime.date(start_year, start_month, start_day)
        finish = _datetime.date(finish_year, finish_month, finish_day)

        return {(start, finish) : url}
        

    # Only the rows that have links have timetables that we have to parse
    timetable_tags = timetables_links_table.find_all("a")

    result = {}
    for tag in timetable_tags:
        result[_parse_dates(tag.string)] = _utils.BASE_URL_PT + tag["href"]

    return result

def parse_timetable(credentials: _Credentials.Credentials, url: str) -> list:
    """Parses the events (including overlaps) of the timetable
    with the given url. Returns a list of dictionaries, each
    representing an event.
    An example:
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
    try:
        weeks_url_query = re.findall(r"&p_semana_inicio=\d+&p_semana_fim=\d+$", url)[0]
    except:
        weeks_url_query = ""

    html = credentials.get_html(url)
    soup = _bs4.BeautifulSoup(html, 'lxml')

    timetable_soup = soup.find("table", {"class": "horario"})

    if timetable_soup == None:
        raise ValueError("No timetable was found in the soup")

    result = []

    rows = timetable_soup.find_all("tr", recursive=False)[1:]  # Ignore the header

    for i, row in enumerate(rows):
        start_time = _datetime.timedelta(hours=8, minutes=i * 30)

        tds = row.find_all("td", recursive=False)[1:]  # Ignore the hour

        for n, td in enumerate(tds):
            if td["class"] in (["horas"], ["almoco"]):  # It's whitespace
                continue

            # Otherwise we have an event we need to parse

            # This for loop compensates n in order to reflect the actual weekday of the event
            for event in sorted(result, key=lambda a: _weekdays.index(a["weekday"])): # sort the events by weekday
                if event["start"] < _timedelta_to_time(start_time) < event["finish"]:
                    if _weekdays.index(event["weekday"]) <= n:
                        n += 1
            weekday = _weekdays[n]

            class_type = _re.findall(r"\((\w+)\)", str(td))[0]

            finish_time = start_time + _datetime.timedelta(minutes=int(td["rowspan"]) * 30)

            uc_tag, classes_tag, room_tag, teachers_tag = td.find_all("a")

            result.append(
                {
                    "weekday"        : weekday,
                    "class type"     : class_type,
                    "start"          : _timedelta_to_time(start_time),
                    "finish"         : _timedelta_to_time(finish_time),
                    "curricular unit": _CurricularUnit.CurricularUnit.from_a_tag(uc_tag),
                    "classes"        : _parse_classes(credentials, classes_tag),
                    "room"           : _parse_rooms(credentials, room_tag),
                    "teachers"       : _parse_teachers(credentials, teachers_tag)
                }
            )

    last_table = timetable_soup.find_next("table", {"class": "dados"})

    if "Aulas Sobrepostas" in str(last_table):
        rows = last_table("tr", {"class": "d"})

        for row in rows:
            weekday_pt = row.find("td", {"headers": "t2"}).string
            weekday = _weekdays_pt_to_en[weekday_pt]

            hour, minute = map(int, row.find(
                "td", {"headers": "t3"}).string.split(":"))
            start = _datetime.time(hour=hour, minute=minute)

            url = (_utils.BASE_URL_PT + row.find("td",
                                          {"headers": "t6"}).a["href"]).lower()

            if "hor_geral.composto_desc" in url:
                temp_html = credentials.get_html(url)
                temp_soup = _bs4.BeautifulSoup(temp_html, 'lxml')
                temp_content = temp_soup.find("div", {"id": "conteudoinner"})
                url = (_utils.BASE_URL_PT + temp_content.find_all("a")
                       [1]["href"]).lower()
            else:
                url+=weeks_url_query # For some odd reason, single classes' urls don't include the start and finish weeks, a bug on sigarra's side perhaps?

            for event in parse_timetable(credentials, url):
                if event["weekday"] == weekday and event["start"] == start:
                    result.append(event)
                    break
            else:
                raise Exception  # Something went wrong

    def sort_key(event): # Sort by day and then by hour
        return (_weekdays.index(event["weekday"]), event["start"])

    return sorted(result, key = sort_key)


def _timedelta_to_time(t: _datetime.timedelta) -> _datetime.time:
    return (_datetime.datetime.min + t).time()


def _parse_teachers(credentials: _Credentials.Credentials, a: _bs4.Tag) -> tuple:
    url = (_utils.BASE_URL_PT + a["href"]).lower()

    if "hor_geral.composto_doc" in url:
        html = credentials.get_html(url)
        soup = _bs4.BeautifulSoup(html, 'lxml')
        content = soup.find("div", {"id": "conteudoinner"})
        teachers_tags = content.find_all("a")[1:]
        return tuple(_Teacher.Teacher.from_a_tag(tag) for tag in teachers_tags)

    elif "func_geral.formview" in url:
        return (_Teacher.Teacher.from_a_tag(a),)

    else:
        raise Exception(f"unrecognized url: {url}")


def _parse_classes(credentials: _Credentials.Credentials, a: _bs4.Tag) -> tuple:
    url = (_utils.BASE_URL_PT + a["href"]).lower()

    if "hor_geral.composto_desc" in url:
        html = credentials.get_html(url)
        soup = _bs4.BeautifulSoup(html, 'lxml')
        content = soup.find("div", {"id": "conteudoinner"})
        classes_tags = content.find_all("a")[1:]
        return tuple(sorted(tag.string for tag in classes_tags))

    elif "hor_geral.turmas_view" in url:
        return (a.string,)

    else:
        raise Exception(f"unrecognized url: {url}")


def _parse_rooms(credentials: _Credentials.Credentials, a: _bs4.Tag) -> tuple:
    url = (_utils.BASE_URL_PT + a["href"]).lower()

    if "hor_geral.composto_salas" in url:
        html = credentials.get_html(url)
        soup = _bs4.BeautifulSoup(html, 'lxml')
        content = soup.find("div", {"id": "conteudoinner"})
        rooms_tags = content.find_all("a")[1:]
        return tuple(tag.string for tag in rooms_tags)

    elif "instal_geral.espaco_view" in url:
        return (a.string,)

    else:
        raise Exception(f"unrecognized url: {url}")


def _parse_dates(dates_string):
    result = []
    for date_str in dates_string.split("a"):
        day, month = map(int, date_str.split("-"))

        if month >= 9:  # 9 -> September
            year = _utils.get_current_academic_year()
        else:
            year = _utils.get_current_academic_year() + 1
        result.append(_datetime.date(year, month, day))

    return tuple(result)
