from thompson_narrative_collector.parsers.base import BaseParser
from thompson_narrative_collector.parsers.parser_ashliman_collection import AshlimanCollectionParser
from thompson_narrative_collector.utils.backend_db_handler import BackendDbHandler
from typing import List
from thompson_narrative_collector.logger import logger


def interface(backend_db_handler: BackendDbHandler,
              page_parsers: List[BaseParser],
              is_force_retry: bool=False):
    # Get all target-URL and save them into DB
    for parser_obj in page_parsers:
        seq_target_url = parser_obj.parse_index_page()
        backend_db_handler.save_target_urls(seq_target_url)

    # Gets pages
    backend_db_handler.run_html_extraction(limit=2)
    seq_extracted_pages = backend_db_handler.show_extracted_html()
    for parser_obj in page_parsers:
        for extracted_page_obj in seq_extracted_pages:
            if parser_obj.domain in extracted_page_obj['page_url']:

                print()
                pass

    print()



def main():
    # CLインタフェース用
    pass
