import re as _re

import bs4 as _bs4

from . import _Credentials
from . import _internal_utils as _utils
from . import _Course
from . import _CurricularUnit
from . import timetable as _timetable

__all__ = ["User"]

class User:
    """This class represents the information that can be extracted
    from your personal webpage.

    Properties:
        pv_fest_id      (int) # A sort of course specific student identification number.
                              # See from_credentials() and get_pv_fest_ids() for ways to get
                              # this number
        course          (Course object) # The course related to this pv_fest_id
        credentials     (Credentials object) # The credentials argument from the __init__ function
                                             # (This is done to avoid having to pass the same
                                             # Credentials object to every function)

    Methods:
        from_credentials (class  method)
        get_pv_fest_ids  (static method)
        courses_units
        timetable
        all_timetables
        classes
    """

    __slots__ = ["pv_fest_id", "course", "credentials"]

    def __init__(self, pv_fest_id : int, credentials: _Credentials.Credentials):
        """Parses your personal webpage. See User.get_pv_fest_ids() and User.from_credentials()
        for ways to get your pv_fest_id. A pv_fest_id is like a "course specific student id",
        from what I can tell.
        """
        self.pv_fest_id = pv_fest_id
        self.credentials = credentials # Note, this is only a reference

        html = credentials.get_html(_utils.SIG_URLS["courses units"], {"pv_fest_id" : str(pv_fest_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")
        
        if "Não tem permissões para aceder a este conteúdo." in html:
            raise ValueError("Your Credentials object does not have permission to access the page related to this pv_fest_id")

        for tag in soup.find_all("h2"):
            if "cur_geral.cur_view" in str(tag):
                self.course = _Course.Course.from_a_tag(tag.a)
                break
        else:
            raise Exception("No course was found")

    def courses_units(self) -> list:
        """Returns a list of tuples. Each tuple contains a Curricular unit which represents
        a curricular unit that you have had in a previous year or you currently enrolled in,
        and either an int which represents the grade you got at that curricular unit or None
        if a grade is not available.

        Example:
            [(CurricularUnit(419981), 10),
             (CurricularUnit(419982), 11),
             (CurricularUnit(419983), 12),
             (CurricularUnit(419984), 13),
             (CurricularUnit(419985), 14),
             (CurricularUnit(420521), 15),
             (CurricularUnit(419986), None),
             (CurricularUnit(419987), None),
             (CurricularUnit(419988), None),
             (CurricularUnit(419989), None),
             (CurricularUnit(419990), None)]
        """
        html = self.credentials.get_html(_utils.SIG_URLS["courses units"], {"pv_fest_id" : str(self.pv_fest_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        result = []
        for row in soup.find_all("tr", {"class" : "d"}):
            curricular_unit = _CurricularUnit.CurricularUnit.from_a_tag(row.a)
            
            try:
                grade = int(row.find("td", {"class" : "n"}).string)
            except:
                grade = None
            
            result.append((curricular_unit, grade))
        
        return result

    def timetable(self) -> list:
        """Returns the current user timetable 
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
        html = self.credentials.get_html(_utils.SIG_URLS["personal timetable"], {"pv_fest_id" : str(self.pv_fest_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        return _timetable.parse_current_timetable(self.credentials, soup.a["href"])
    
    def all_timetables(self) -> dict:
        """Parses all the timetables related to this user.
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
        html = self.credentials.get_html(_utils.SIG_URLS["personal timetable"], {"pv_fest_id" : str(self.pv_fest_id)})
        soup = _bs4.BeautifulSoup(html, "lxml")

        return _timetable.parse_timetables(self.credentials, soup.a["href"])

    def classes(self):
        """Returns a list of tuples, each tuple containing a CurricularUnit object
        and the class name as a string.
        """
        raise NotImplementedError("No idea if this works or not")
        html = self.credentials.get_html(_utils.SIG_URLS["classes data"] , params = {"pv_estudante_id" : str(self.pv_fest_id)})
        soup = _bs4.BeautifulSoup(html, 'lxml')
    
        tables = soup.find_all("table", {"class" : "tabela"})[1:] # Forget first table

        result = []
        for table in tables:
            for row in table.find_all("tr")[2:]: #Forget the header rows
                curricular_unit = _CurricularUnit.CurricularUnit.from_a_tag(row.find("a"))
                class_name = row.find_all("td")[3].string

                result.append((curricular_unit, class_name))
        
        return result

    @classmethod
    def from_credentials(cls, credentials: _Credentials.Credentials):
        """Returns a User object made from the first result from get_pv_fest_ids().
        Usually, students are enrolled in only one course, which means that
        get_pv_fest_ids() tends to be a tuple with a single int.
        """
        return User(User.get_pv_fest_ids(credentials)[0], credentials)


    @staticmethod
    def get_pv_fest_ids(credentials: _Credentials.Credentials) -> tuple:
        """Returns a tuple of ints, each representing a pv_fest_id."""
        payload = {"pv_num_unico" : str(credentials.username)}
        html = credentials.get_html(_utils.SIG_URLS["student page"], payload)
    
        matches = _re.findall(r"pv_fest_id=(\d+)", html)

        if len(matches) == 0:
            raise ValueError("No pv_fest_id's were found")
    
        return tuple(int(match) for match in matches)

    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}
