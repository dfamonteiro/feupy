# Changelog

## 0.4.3
* Renamed a `CurricularUnit` attribute: `curricular_year`, which was previously an `int`, has been renamed to `curricular_years`, now a `tuple` of `int`s

## 0.4.8
* Fixed a bug regarding the presence of duplicate `Teacher` objects in a curricular unit

## 0.5.0
* Added a `full_info` optional argument to `CurricularUnit.classes()` that returns more information per student

## 0.5.1
* Fixed an infinite recursion bug regarding `timetable.all_timetables()`

## 0.5.2
* Fixed bug regarding too many lines in a student's course box

## 0.5.3
* Fixed bug regarding students with no email

## 0.5.4
* Fixed bug regarding curricular units with no students

## 0.5.5
* Fixed bug regarding curricular units with a number of students divisible by 50

## 0.5.6
* Fixed bug regarding curricular units with an awkward semester value

## 0.5.7
* Refactored `timetables.py`

## 0.5.8
* Added support for students from other faculties

## 0.5.9
* Bugfixes and performance improvements (I've reached peak changelog)

## 0.5.12
* Fixed bug regarding FCUP classes not loading correctly