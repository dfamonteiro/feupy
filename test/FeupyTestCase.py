import unittest
from sys import argv

def verbosity() -> bool:
    return ('-v' in argv) or ('--verbose' in argv)

class FeupyTestCase(unittest.TestCase):
    """This class is unittest.TestCase plus a few utility methods, pretty much
    """
    def assertObjectAttributes(self, test_object, test_vars : dict) -> None:
        """Tests all the attributes of object specified in test_vars.
        test_vars is something akin to vars(object). Another note: test_vars
        only needs to contain the object attributes that you want to test."""
                
        for key in test_vars:
            if verbosity():
                print(f"Testing attribute '{key}'")
            self.assertEqual(getattr(test_object, key), test_vars[key])
    
    

if __name__ == '__main__':
    unittest.main()