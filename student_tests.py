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
        self.assertFalse(is_valid("https://ics.uci.edu/events/2024-05"))
        self.assertTrue(is_valid("https://ics.uci.edu/events"))
        self.assertFalse(is_valid("https://swiki.ics.uci.edu/events"))
        self.assertFalse(is_valid("https://cbcl.ics.uci.edu/doku.php/"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.apk"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.img"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.sql"))
        self.assertFalse(is_valid("https://ics.uci.edu/events.war"))
        self.assertFalse(is_valid("https://gitlab.ics.uci.edu/test/commit"))
        self.assertFalse(is_valid("https://ics.uci.edu/~eppstein/ca"))
        self.assertFalse(is_valid("https://plrg.eecs.uci.edu/"))
        self.assertFalse(is_valid("https://grape.ics.uci.edu/wiki/public/wiki/cs222-2017-fall?version=31&format=txt"))

    def test_calendar_patterns(self):
        matches = [
            "https://site.com/page?date=2024-05-01",
            "https://site.com/calendar/2024/05/",
            "https://site.com/calendar/2024-05",
            "https://site.com/calendar/1-1-2024",
            "https://site.com/calendar/2024-05-01"
        ]
        for url in matches:
            self.assertTrue(find_calendar(url), msg=f"Should match calendar pattern: {url}")

        non_matches = [
            "https://site.com/news",
            "https://site.com/page?m=202405"
        ]
        for url in non_matches:
            self.assertFalse(find_calendar(url), msg=f"Should NOT match calendar pattern: {url}")

    def test_find_traps(self):
        self.assertTrue(find_traps("http://www.ics.uci.edu/doku.php?id=start"))
        self.assertTrue(find_traps("http://www.ics.uci.edu/~eppstein"))
        self.assertTrue(find_traps("http://www.ics.uci.edu/page?tribe-bar-date=2024-01-01"))
        self.assertFalse(find_traps("http://www.ics.uci.edu/page?view=normal"))

    def test_filtered_words(self):
        sample_text = """
            The quick brown fox jumps over 2023 lazy dogs. AI, ML, and NLP are cool.
            a i UCI 中国 日本 Привет abc123 hello world banana 42 z!
        """
        # Tokenize using \w+ which includes Unicode
        tokens = re.findall(r'\b\w+\b', sample_text.lower())  # Unicode-aware
        filtered_words = [
            word for word in tokens
            if word not in STOPWORDS and len(word) > 1 and word.isalpha()
        ]

        # Expected results include Unicode alphabetic words
        expected = {
            'quick', 'brown', 'fox', 'jumps', 'lazy', 'dogs', 'cool', 'hello',
            'world', 'banana', 'uci', '中国', '日本', 'привет', 'ai', 'ml', 'nlp'
        }

        self.assertEqual(set(filtered_words), expected)

    
if __name__ == '__main__':
    unittest.main()