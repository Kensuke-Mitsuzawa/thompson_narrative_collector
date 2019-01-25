from thompson_narrative_collector.parsers.parser_ashliman_collection import AshlimanCollectionParser
import unittest
import pathlib
import codecs


class TestAshlimanCollectionParser(unittest.TestCase):
    def setUp(self):
        if 'test' in pathlib.Path().cwd().__str__():
            self.path_resource = '../resources/'
        else:
            self.path_resource = 'test/resources/'

    def test_parse_index_page(self):
        parser = AshlimanCollectionParser()
        page_1 = "http://www.pitt.edu/~dash/folktexts.html"
        seq_target_url = parser.parse_index_page()
        self.assertTrue(isinstance(seq_target_url, list))

    def test_parse_folktale_page(self):
        with codecs.open(pathlib.Path(self.path_resource).joinpath('abduct.html'), 'r', 'utf-16') as f:
            html_doc_pattern_1 = f.read()
        parser = AshlimanCollectionParser()
        parser.parse_folktale_page(html_doc_pattern_1)

        with codecs.open(pathlib.Path(self.path_resource).joinpath('type0910b.html'), 'r', 'utf-8') as f:
            html_doc_pattern_2 = f.read()
        parser = AshlimanCollectionParser()
        parser.parse_folktale_page(html_doc_pattern_2)

        with codecs.open(pathlib.Path(self.path_resource).joinpath('alibaba.html'), 'r', 'utf-8') as f:
            html_doc_pattern_3 = f.read()
        parser = AshlimanCollectionParser()
        parser.parse_folktale_page(html_doc_pattern_3)


if __name__ == '__main__':
    unittest.main()
