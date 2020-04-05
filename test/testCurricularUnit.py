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
            'curricular_year': (1,),
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
            'webpage_url': 'https://web.fe.up.pt/~jlopes/doku.php/teach/fpro/index'
        }
        
        self.assertObjectAttributes(self.fpro, expected_output)

    

if __name__ == '__main__':
    unittest.main()