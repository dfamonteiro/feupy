"""The sigarra scraping library no one asked for

Objects:
    Student
    Teacher
    CurricularUnit
    Course
    Credentials
    User

Modules:
    exams
    timetable
    cache
"""
from . _Student import Student
from . _Teacher import Teacher
from . _CurricularUnit import CurricularUnit
from . _Course import Course

from . _Credentials import Credentials
from . _User import User

from . import exams
from . import timetable