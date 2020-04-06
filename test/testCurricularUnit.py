import unittest

from .FeupyTestCase import FeupyTestCase
from feupy import CurricularUnit, Teacher

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
            'teachers': (Teacher(230756),
                        Teacher(230756),
                        Teacher(520205),
                        Teacher(552793),
                        Teacher(209847)),
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
            'teachers': (Teacher(209980),
                        Teacher(233753),
                        Teacher(452947),
                        Teacher(468729),
                        Teacher(468729),
                        Teacher(452947),
                        Teacher(209980),
                        Teacher(233753)),
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
                Teacher(210017), Teacher(239083), Teacher(210893), 
                Teacher(207140), Teacher(209784), Teacher(209810), 
                Teacher(322605), Teacher(210741), Teacher(472718), 
                Teacher(245546), Teacher(211430), Teacher(230756), 
                Teacher(555321), Teacher(210176), Teacher(208327), 
                Teacher(207140), Teacher(249597), Teacher(246626), 
                Teacher(209784), Teacher(209810), Teacher(500614), 
                Teacher(210741), Teacher(208947), Teacher(472718), 
                Teacher(211430), Teacher(249340), Teacher(243027), 
                Teacher(400655), Teacher(210158), Teacher(209821), 
                Teacher(211795), Teacher(210660), Teacher(209876), 
                Teacher(384641), Teacher(235777)
                ),
            'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=420521',
            'webpage_url': 'http://www.fe.up.pt/projfeup~',
            }

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
                'teachers': (Teacher(207878),
                            Teacher(207894),
                            Teacher(231674),
                            Teacher(245140),
                            Teacher(424026),
                            Teacher(209625)),
                'url': 'https://sigarra.up.pt/feup/en/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=436365',
                'webpage_url': None,
            }

        self.assertObjectAttributes(self.thesis, expected_output)

if __name__ == '__main__':
    unittest.main()
