from thompson_narrative_collector.parsers.parser_ashliman_collection import AshlimanCollectionParser
import unittest


class TestAshlimanCollectionParser(unittest.TestCase):
    def test_parse_index_page(self):
        parser = AshlimanCollectionParser()
        page_1 = "http://www.pitt.edu/~dash/folktexts.html"
        seq_target_url = parser.parse_index_page(parser.get_html(page_1))
        self.assertTrue(len(seq_target_url) > 1)
        page_2 = "http://www.pitt.edu/~dash/folktexts2.html"
        seq_target_url_2 = parser.parse_index_page(parser.get_html(page_2))
        self.assertTrue(len(seq_target_url_2) > 1)


if __name__ == '__main__':
    unittest.main()
