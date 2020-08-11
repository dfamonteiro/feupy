import unittest
from datetime import datetime

from .FeupyTestCase import FeupyTestCase
from feupy import CurricularUnit, Teacher
from . import creds

class TestFpro(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.fpro = CurricularUnit(419983)

    def test_attributes(self):
        expected_output = {
            'ECTS_credits': 6.0,
            'academic_year': 2018,
            'acronym': 'FPRO',
            'base_url': 'https://sigarra.up.pt/feup/en/',
            'code': 'EIC0005',
            'curricular_years': (1,),
            'has_moodle': True,
            'name': 'Programming Fundamentals',
            'number_of_students': 182,
            'pv_ocorrencia_id': 419983,
            'regents': (Teacher(230756),),
            'semester': '1',
            'teachers': (
                Teacher(209847), 
                Teacher(230756), 
                Teacher(520205), 
                Teacher(552793)
            ),
            'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=419983',
            'webpage_url': 'https://web.fe.up.pt/~jlopes/doku.php/teach/fpro/index',
        }
        
        self.assertObjectAttributes(self.fpro, expected_output)


class TestIope(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.iope = CurricularUnit(436840)
    
    def test_attributes(self):
        expected_output = {
            'ECTS_credits': 6.0,
            'academic_year': 2019,
            'acronym': 'IOPE',
            'base_url': 'https://sigarra.up.pt/feup/en/',
            'code': 'EEC0017',
            'curricular_years': (3, 4),
            'has_moodle': True,
            'name': 'Operations Research',
            'number_of_students': 148,
            'pv_ocorrencia_id': 436840,
            'regents': (Teacher(209980), Teacher(233753), Teacher(452947)),
            'semester': '1',
            'teachers': (
                Teacher(209980), 
                Teacher(233753), 
                Teacher(452947), 
                Teacher(468729)
            ),
            'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=436840',
            'webpage_url': 'https://sites.google.com/g.uporto.pt/io-or',
            }

        self.assertObjectAttributes(self.iope, expected_output)

class TestPF(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.pf = CurricularUnit(420521)
    
    def test_attributes(self):
        expected_output = {
            'ECTS_credits': 1.5,
            'academic_year': 2018,
            'acronym': 'PF',
            'base_url': 'https://sigarra.up.pt/feup/en/',
            'code': 'FEUP002',
            'curricular_years': (1,),
            'has_moodle': True,
            'name': 'Project FEUP',
            'number_of_students': 930,
            'pv_ocorrencia_id': 420521,
            'regents': (Teacher(322605), Teacher(245546)),
            'semester': '1',
            'teachers': (
                Teacher(207140), Teacher(208327), Teacher(208947), 
                Teacher(209784), Teacher(209810), Teacher(209821), 
                Teacher(209876), Teacher(210017), Teacher(210158), 
                Teacher(210176), Teacher(210660), Teacher(210741), 
                Teacher(210893), Teacher(211430), Teacher(211795), 
                Teacher(230756), Teacher(235777), Teacher(239083), 
                Teacher(243027), Teacher(245546), Teacher(246626), 
                Teacher(249340), Teacher(249597), Teacher(322605), 
                Teacher(384641), Teacher(400655), Teacher(472718), 
                Teacher(500614), Teacher(555321)
            ),
            'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=420521',
            'webpage_url': 'http://www.fe.up.pt/projfeup~',
            }

        self.assertEqual(len(self.pf.teachers), len(set(self.pf.teachers)))

        self.assertObjectAttributes(self.pf, expected_output)

class TestPDMPAThesis(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.thesis = CurricularUnit(436365)
    
    def test_attributes(self):
        expected_output = {
                'ECTS_credits': 198.0,
                'academic_year': 2019,
                'acronym': 'TESE',
                'base_url': 'https://sigarra.up.pt/feup/en/',
                'code': 'PDMPA31',
                'curricular_years': (1, 2, 3, 4),
                'has_moodle': False,
                'name': 'Thesis',
                'number_of_students': 8,
                'pv_ocorrencia_id': 436365,
                'regents': (Teacher(209625),),
                'semester': 'A',
                'teachers': (
                    Teacher(207878), 
                    Teacher(207894), 
                    Teacher(209625),
                    Teacher(231674), 
                    Teacher(245140), 
                    Teacher(424026)
                ),
                'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=436365',
                'webpage_url': None,
            }

        self.assertObjectAttributes(self.thesis, expected_output)

class TestClass(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.vcom = CurricularUnit(446081)
    
    def test_attributes(self):
        self.assertEqual(len(self.vcom.classes(creds)["4MIEIC01"]), 33)

        students = self.vcom.classes(creds, full_info=True)["4MIEIC01"]

        self.assertEqual(students[0][1], datetime(2020, 2, 5, 15, 47))
        self.assertFalse(students[0][2])
        self.assertTrue(students[0][3])

        self.assertTrue(students[2][2])
        self.assertFalse(students[3][3])

class TestAwkardSemester(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.uc = CurricularUnit(445082)
    
    def test_attributes(self):
        expected_output = {
            'ECTS_credits': 2.0,
            'academic_year': 2019,
            'acronym': 'EBECGC',
            'base_url': 'https://sigarra.up.pt/feup/en/',
            'code': 'EBECGC01',
            'curricular_years': (1,),
            'has_moodle': False,
            'is_active': True,
            'name': 'EBEC Porto 24h - Competition Management',
            'number_of_students': 0,
            'pv_ocorrencia_id': 445082,
            'regents': (Teacher(210909),),
            'semester': 'SP',
            'teachers': (Teacher(210909),),
            'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=445082',
            'webpage_url': None
        }

        self.assertObjectAttributes(self.uc, expected_output)

class TestNoTimetable(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.dissertation = CurricularUnit(436404)
    
    def test_attributes(self):
        self.assertEqual(self.dissertation.timetable(creds), None)

class TestNoStudents(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.pesi = CurricularUnit(436409)
    
    def test_attributes(self):
        self.assertEqual(len(self.pesi.students(creds)), 0)

class TestAwkwardCourseTable(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.uc = CurricularUnit(444284)

    def test_attributes(self):
        self.assertEqual(self.uc.curricular_years, (1, 3))

class Test200Students(FeupyTestCase):
    @classmethod
    def setUpClass(cls):
        cls.uc = CurricularUnit(436427)

    def test_attributes(self):
        self.assertEqual(len(self.uc.students(creds)), 200)

if __name__ == '__main__':
    unittest.main()
