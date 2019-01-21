from typing import List, Optional, Dict
import requests


class FolkloreDocument(object):
    def __init__(self,
                 title: str,
                 body: str,
                 author: str,
                 atu_label: str,
                 language: str,
                 source_url: str,
                 source_article: str,
                 attributes: Dict[str, str]):
        self.title = title
        self.body = body
        self.author = author
        self.atu_label = atu_label
        self.language = language
        self.source_url = source_url
        self.source_article = source_article
        self.attributes = attributes


class BaseParser(object):
    @staticmethod
    def get_html(page_url: str)->str:
        return requests.get(page_url).text

    def parse_index_page(self, index_html: str)->List[str]:
        """

        :param index_html: Index of folklore collection-website.
        :return: [URL where folklore is]
        """
        raise NotImplemented()

    def parse_folklore_page(self, folklore_html: str)->List[FolkloreDocument]:
        raise NotImplemented()



