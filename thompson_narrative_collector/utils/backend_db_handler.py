from sqlitedict import SqliteDict
from pathlib import Path
from datetime import datetime
from marshmallow import Schema, fields, pprint


class TargetPage(Schema):
    page_url = fields.Str()
    status = fields.Bool()
    note = fields.Str()
    extracted_at = fields.DateTime()


class ExtractedPage(Schema):
    page_url = fields.Str()
    status = fields.Bool()
    note = fields.Str()
    html_document = fields.Str()
    extracted_at = fields.DateTime()


class BackendDbHandler(object):
    def __init__(self, path_db_file: str):
        self.backend_db = SqliteDict(path_db_file)


    # todo target_pagesを保存するやつ。

    # todo 獲得されたページを保存するやつ。

