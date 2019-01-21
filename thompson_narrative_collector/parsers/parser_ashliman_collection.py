from typing import List
from thompson_narrative_collector.parsers.base import BaseParser
from bs4 import BeautifulSoup, Tag
import itertools
import requests
import time
import string
import os


class AshlimanCollectionParser(BaseParser):
    def __init__(self,
                 domain: str='http://www.pitt.edu/~dash/',
                 interval: int=15):
        self.domain = domain
        self.interval = interval

    @staticmethod
    def is_classification_alphabet(candidate_node: Tag)->bool:
        """Get only Node having link into tales."""
        if candidate_node.find('a') is None:
            return False

        if candidate_node.find('a').text in string.ascii_uppercase:
            return True
        else:
            return False

    @staticmethod
    def get_folklore_set_link(folklore_set_block: Tag)->List[str]:
        """Get URL link into folklore page"""
        ul_node = folklore_set_block.find_next('ul')
        li_nodes = ul_node.find_all('li')
        url_link_folklore_page = [node.find('a').get('href') for node in li_nodes
                                  if node.find('a') is not None and node.find('a').get('href') is not None]
        return url_link_folklore_page

    @staticmethod
    def is_out_domain_page(url_link: str):
        """checks if folklore-link is from outer-domain page."""
        if 'http://www.' in url_link:
            return True
        else:
            return False

    def parse_index_page(self, index_html: str)->List[str]:
        """Get links into a page where folklore story is.

        :param index_html:
        :return: [link_into_folklore_page]
        """
        soup_obj = BeautifulSoup(index_html, 'html.parser')
        __seq_h1_node = soup_obj.find_all('h1')
        seq_h1_node = [node_obj for node_obj in __seq_h1_node if self.is_classification_alphabet(node_obj)]
        seq_links_folklore_page = itertools.chain.from_iterable([self.get_folklore_set_link(header_node)
                                                                 for header_node in seq_h1_node])
        __seq_url_links = [url_link for url_link in seq_links_folklore_page if self.is_out_domain_page(url_link) is False]
        seq_url_links = [os.path.join(self.domain, u) for u in __seq_url_links]
        return seq_url_links


