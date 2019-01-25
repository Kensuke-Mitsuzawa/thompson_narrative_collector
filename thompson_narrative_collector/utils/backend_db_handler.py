from sqlitedict import SqliteDict
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from marshmallow import Schema, fields, pprint
from thompson_narrative_collector.logger import logger
import json
import requests
import time
from tqdm import tqdm


class TargetPage(Schema):
    page_url = fields.Str()
    status = fields.Bool()
    note = fields.Str()
    extracted_at = fields.Str()


class ExtractedPage(Schema):
    page_url = fields.Str()
    status = fields.Bool()
    note = fields.Str()
    html_document = fields.Str()
    extracted_at = fields.Str()


class BackendDbHandler(object):
    """Table structure

    target_pages: A table to save URL where folklore is. Key-value pair. {url_string: TargetPage object}
    target_html: A table to save HTML of folklore. Key-value pair. {url_string: ExtractedPage object}
    """
    def __init__(self, path_db_file: str, interval: int=3):
        self.db_target_pages = SqliteDict(path_db_file, autocommit=True, tablename='target_pages',
                                          encode=json.dumps, decode=json.loads)
        self.db_html = SqliteDict(path_db_file, autocommit=True, tablename='target_html',
                                  encode=json.dumps, decode=json.loads)
        self.interval = interval

    def save_target_urls(self, target_urls: List[str]):
        """Save target URL into DB."""
        for url in target_urls:
            if url not in self.db_target_pages:
                data, errs = TargetPage(strict=True).load({'page_url': url,
                                                           'status': False,
                                                           'note': '',
                                                           'extracted_at': ''})
                self.db_target_pages[url] = data
            else:
                logger.info('URL={} is already in target. Skip.'.format(url))
        else:
            self.db_target_pages.commit()

    def run_html_extraction(self, is_force_retry: bool=False, limit: int=-1):
        """Gets all target page and save them into DB."""
        default_i = 0
        for url, page_obj in tqdm(list(self.db_target_pages.items())):
            _obj = TargetPage(strict=True).load(page_obj)
            if page_obj['status'] is False or is_force_retry is True:
                try:
                    html_doc = requests.get(url).text
                    error_msg = ''
                    status = True
                except ExtractedPage as e:
                    html_doc = ''
                    error_msg = e.__str__()
                    status = False

                data, errs = ExtractedPage(strict=True).load({'page_url': url,
                                                              'status': status,
                                                              'html_document': html_doc,
                                                              'note': error_msg,
                                                              'extracted_at': datetime.now().__str__()})
                page_obj['status'] = True
                page_obj['extracted_at'] = datetime.now().__str__()
                self.db_target_pages[url] = data
                default_i += 1
                time.sleep(self.interval)
                if default_i == limit:
                    logger.info('Terminated by limit={}'.format(limit))
                    break
            else:
                logger.info('URL={} is already in target. Skip.'.format(url))
        else:
            self.db_target_pages.commit()
            self.db_html.commit()

    def show_extracted_html(self)->List[Dict[str, Any]]:
        __ = []
        for url, obj_ in self.db_target_pages.items():
            data, errs = ExtractedPage(strict=True).load(obj_)
            if data['status']:
                __.append(obj_)
        else:
            return __





    # todo 獲得されたページを保存するやつ。

