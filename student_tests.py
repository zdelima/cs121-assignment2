import unittest
from scraper import *

class TestScraper(unittest.TestCase):
    def test_is_valid(self): # test if is_valid finds all domains following assignment instructions
        self.assertTrue(is_valid("http://test.ics.uci.edu/robots.txt"))
        self.assertTrue(is_valid("http://test.cs.uci.edu/robots.txt"))
        self.assertTrue(is_valid("http://test.informatics.uci.edu/robots.txt"))
        self.assertTrue(is_valid("http://test.stat.uci.edu/robots.txt"))
        self.assertTrue(is_valid("http://today.uci.edu/department/information_computer_sciences/robots.txt"))
        self.assertFalse(is_valid("http://today.uci.edu/cs121/information_computer_sciences/robots.txt"))
        self.assertFalse(is_valid("https://canvas.eee.uci.edu/courses/72511/assignments/1584020#test"))
        self.assertFalse(is_valid("https://ics.uci.edu/events/2027-05-01"))
        self.assertFalse(is_valid("https://ics.uci.edu/events/2024-05-01"))
        self.assertTrue(is_valid("https://ics.uci.edu/events"))
        self.assertFalse(is_valid("https://swiki.ics.uci.edu/events"))
        self.assertFalse(is_valid("https://cbcl.ics.uci.edu/doku.php/"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.apk"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.img"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.sql"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.war"))
        self.assertFalse(is_valid("https://gitlab.ics.uci.edu/test/commit"))
        self.assertFalse(is_valid("https://ics.uci.edu/~eppstein/ca"))






    
if __name__ == '__main__':
    unittest.main()