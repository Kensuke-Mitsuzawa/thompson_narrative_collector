import unittest
import os
from thompson_narrative_collector.parsers.parser_ashliman_collection import AshlimanCollectionParser
from thompson_narrative_collector.utils.backend_db_handler import BackendDbHandler
from thompson_narrative_collector.interface import interface


class TestInterface(unittest.TestCase):
    def setUp(self):
        self.path_backend_db = ''

    def tearDown(self):
        if os.path.exists(self.path_backend_db):
            os.remove(self.path_backend_db)

    def test_interface(self):
        self.path_backend_db = './backend_db.sqlite3'
        backend_db_handler = BackendDbHandler(self.path_backend_db)
        interface(backend_db_handler, page_parsers=[AshlimanCollectionParser()])


if __name__ == '__main__':
    unittest.main()
