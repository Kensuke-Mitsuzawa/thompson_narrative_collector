from typing import List, Optional, Tuple
from thompson_narrative_collector.parsers.base import BaseParser, FolkloreDocument
from bs4 import BeautifulSoup, Tag, NavigableString
import itertools
import requests
import time
import collections
import re
import string
import os


StoryMetaInformation = collections.namedtuple('StoryMetaInformation', ('body', 'source', 'note', 'atu'))


class AshlimanCollectionParser(BaseParser):
    def __init__(self,
                 domain: str='http://www.pitt.edu/~dash/',
                 interval: int=15):
        super(BaseParser, self).__init__()
        self.index_pages = ['http://www.pitt.edu/~dash/folktexts.html', 'http://www.pitt.edu/~dash/folktexts2.html']
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

    def __parse_index_page(self, index_html: str)->List[str]:
        soup_obj = BeautifulSoup(index_html, 'html.parser')
        __seq_h1_node = soup_obj.find_all('h1')
        seq_h1_node = [node_obj for node_obj in __seq_h1_node if self.is_classification_alphabet(node_obj)]
        seq_links_folklore_page = itertools.chain.from_iterable([self.get_folklore_set_link(header_node)
                                                                 for header_node in seq_h1_node])
        __seq_url_links = [url_link for url_link in seq_links_folklore_page if self.is_out_domain_page(url_link) is False]
        seq_url_links = [os.path.join(self.domain, u) for u in __seq_url_links]
        return seq_url_links

    def parse_index_page(self, index_html: List[str]=None)->List[str]:
        """Get links into a page where folklore story is.

        :param index_html: list of index page HTML document.
        :return: [link_into_folklore_page]
        """
        if index_html is None:
            index_html = [self.get_html(url) for url in self.index_pages]
        else:
            assert isinstance(index_html, list)

        return list(set(itertools.chain.from_iterable([self.__parse_index_page(url) for url in index_html])))

    def get_html_pattern(self, soup_obj: BeautifulSoup)->str:
        """classify pattern of HTML structure

        :return: pattern1: AT number is in top of a page.
        pattern2: AT number is in source information(multiple). pattern3: AT number is missing
        """
        if isinstance(soup_obj.find('center').find('h1').next_sibling, NavigableString) and \
                'Type' in soup_obj.find('center').find('h1').next_sibling.__str__():
            # Aarne-Thompson-Uther Type is in Top of a page
            return 'pattern1'

        seq_hr_node = soup_obj.find_all('hr')
        for hr_node in seq_hr_node:
            if isinstance(hr_node.next_sibling.next_sibling, Tag) and hr_node.next_sibling.next_sibling.name == 'ul':
                ul_node = hr_node.next_sibling.next_sibling
                if isinstance(ul_node.find_next('ol'), Tag) and ' type' in ul_node.find_next('ol').text:
                    return 'pattern2'

        return 'pattern3'

            # 本文取得パターン
            #if hr_node.next_sibling.next_sibling.name == 'h2' and hr_node.next_sibling.next_sibling.next_sibling.next_sibling.name == 'h3':
            #    print()

    def get_at_numbers(self):
        pass

    # todo ここらへんうまくいかない。
    def __get_source_information(self, node_end_story: Tag, html_pattern: str):
        """Extracts source information."""
        if node_end_story is None or node_end_story.next_sibling is None:
            return False
        if 'Source' in node_end_story.next_sibling.__str__():
            source_info_node = node_end_story
        else:
            source_info_node = node_end_story.next_sibling.next_sibling

        source_info_text = source_info_node.text if isinstance(source_info_node, Tag) else source_info_node.__str__()
        source_info = re.search(r'Source:[\s\w,\(\)\:]*', source_info_text)
        if html_pattern == 'pattern2':
            # extracts source information from html
            print(source_info_node)
            seq_li_nodes = source_info_node.find_all('li')
            for li_node in seq_li_nodes:
                print(li_node.text)

    def __clean_up_source(self, source_text: str)->str:
        """Removes all HTML tags from original HTML text.

        :param source_text: original HTML node of source information
        :return: cleaned-up source information
        """
        _ = re.sub(r'<.*?>', '', source_text)

        return _

    def __clean_up_note(self, note_string: str)->Tuple[str, Optional[List[str]]]:
        """

        :param note_string:
        :return: (cleaned-note-info, [ATU-info])
        """
        if 'aarne-thompson-uther' in note_string.lower():
            type_numbers = re.findall(r'type\s[0-9]+', note_string)
            atus = [__.strip('type ') for __ in type_numbers]
            return note_string, atus
        else:
            _ = re.sub(r'<.*?>', '', note_string)
            return (_, None)

    def __extract_story_broken_structure(self, seq_broken_nodes: List[str], body_text: str) -> StoryMetaInformation:
        """Extract (story-body, Source-info, note-info, ATU-info) when HTML structure is broken.

        :return: StoryMetaInformation
        """
        source_node = ''
        note_string_node = ''
        for broken_i, broken_node_string in enumerate(seq_broken_nodes):
            if re.search('.+<li>Source', broken_node_string):
                # keep getting nodes unti "return to the~"
                source_node = broken_node_string
                note_string_node = ''
                if broken_i == len(seq_broken_nodes) -1:
                    break

                while True:
                    if 'Return to the' in seq_broken_nodes[broken_i + 1]:
                        break
                    else:
                        note_string_node += seq_broken_nodes[broken_i + 1]
                        broken_i += 1
                break
            else:
                body_text += broken_node_string.replace('<p>', '').replace('</p>', '')

        cleaned_source = self.__clean_up_source(source_node)
        # extract ATU
        cleaned_note = self.__clean_up_note(note_string_node)

        return StoryMetaInformation(body=body_text,
                                    source=cleaned_source,
                                    note=cleaned_note[0],
                                    atu=cleaned_note[1])

    def __extract_story_body(self, start_node: Tag) -> StoryMetaInformation:
        """Extracts only (story-body, Source-info, ATU-number if exists)

        :param start_node:
        :return:
        """
        body_text = ''
        cleaned_source = ''
        cleaned_note = ('', [])
        seq_nodes = [start_node.__str__()] + [n.__str__() for n in start_node.next_siblings]
        for node_string in seq_nodes:
            __node_string = node_string.replace('\n', '')
            if re.search('<p>.+<li>Source', __node_string):
                # some story-blocks are missing </p> tag. Broken structure.
                seq_broken_nodes = __node_string.split('<p>')
                return self.__extract_story_broken_structure(seq_broken_nodes, body_text)
            if re.search(r'<li>Source:', node_string):
                cleaned_source = self.__clean_up_source(node_string)
                # extract ATU
                cleaned_note = self.__clean_up_note(node_string)
                break
            else:
                if re.search(r'<p>.+', node_string):
                    body_text += node_string.replace('<p>', '').replace('</p>', '')
                elif node_string == '\n':
                    continue
                elif node_string == '<hr/>':
                    continue
                elif re.search(r'\n.+', node_string):
                    body_text += node_string.replace('\n', '')
                elif re.search(r'<i>', node_string):
                    body_text += node_string.replace('<i>', '').replace('</i>', '')
                else:
                    body_text += node_string
                    # raise Exception('Unexpected case: ' + node_string)

        return StoryMetaInformation(body=body_text,
                                    source=cleaned_source,
                                    note=cleaned_note[0],
                                    atu=cleaned_note[1])

    def __get_folktale_unit(self, hr_node: Tag, html_pattern: str, atu_numbers: Optional[List[str]]=())->Optional[FolkloreDocument]:
        """Extracts folktale story text(one story) and meta information from Nodes."""

        if isinstance(hr_node.next_sibling.next_sibling, Tag) and hr_node.next_sibling.next_sibling.name == 'h2' and \
                isinstance(hr_node.next_sibling.next_sibling.next_sibling.next_sibling, Tag) and \
                hr_node.next_sibling.next_sibling.next_sibling.next_sibling.name == 'h3':
            h2_node_folktale_start = hr_node.next_sibling.next_sibling
            h3_node_folktale_area = hr_node.next_sibling.next_sibling.next_sibling.next_sibling
            folktale_name = h2_node_folktale_start.text.strip()
            folktale_area = h3_node_folktale_area.text.strip()

            start_node = h3_node_folktale_area.next_sibling
            story_meta_information = self.__extract_story_body(start_node)

            f_obj = FolkloreDocument(
                title=folktale_name,
                body=story_meta_information.body,
                author='',
                atu_labels=story_meta_information.atu,
                language='English',
                source_area=folktale_area,
                source_url='',  # put information later
                source_article=story_meta_information.source,
                attributes={'note': story_meta_information.note}
            )
            return f_obj
        else:
            return None

    def get_folktale_unit(self, soup_obj: BeautifulSoup, html_pattern: str)->List[FolkloreDocument]:
        seq_hr_node = soup_obj.find_all('hr')
        __return = []
        for hr_node in seq_hr_node:
            __ = self.__get_folktale_unit(hr_node, html_pattern)
            if __ is not None:
                __return.append(__)
        else:
            return __return

    def parse_folktale_page(self, folklore_html: str)->List[FolkloreDocument]:
        soup_obj = BeautifulSoup(folklore_html, 'html.parser')
        # pattern-1 <hr><h2><h3> tales... <hr><ul><li>tales meta data</li><hr>
        html_pattern = self.get_html_pattern(soup_obj)
        return self.get_folktale_unit(soup_obj, html_pattern)




