# Copyright (C) 2021 Diego Miguel Lozano <dml1001@alu.ubu.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For license information on the libraries used, see LICENSE.

"""Marshmallow Schemas for DispatcherService."""

__version__ = '0.1.11'

from datetime import datetime
from marshmallow import Schema, fields, pre_dump, pre_load, EXCLUDE, INCLUDE
from werkzeug.datastructures import FileStorage
from extracted_text_status import ExtractedTextStatus
from supported_file_types import SupportedFileType
from typing import Tuple


class DocExtractedText():
    """Class for the extracted text from documents.

    An extracted text has the following attributes:

    * id_ (:obj:`str`): the id of the extracted text (hash of the document from which
      it was extracted).
    * content (:obj:`str`): the extracted text.
    * status (:obj:`data.extracted_text_status.ExtractedTextStatus`):
      the current status of the extracted text.
    * file_type (:obj:`data.supported_file_types.SupportedFileType`): the file
      type the extracted text came from.
    * start_page (:obj:`int`): the first page (1-indexed) from which the text
      was extracted.
    * end_page (:obj:`int`): the last page (1-indexed) until which the text was
      extracted.
    * started_at (:obj:`datetime.datetime`): the time when it was first
      requested to extract the text.
    * ended_at (:obj:`datetime.datetime`): the time when the text was finished to be
      extracted.
    * errors (:obj:`Union[dict, None]`): errors originated when extracting the
      text (if any).
    """

    def __init__(self,
                 id_: str,
                 content: str,
                 status: ExtractedTextStatus,
                 file_type: SupportedFileType,
                 start_page: int,
                 end_page: int,
                 started_at: datetime,
                 ended_at: datetime,
                 errors: dict):
        self.id_ = id_
        self.content = content
        self.status = status.value
        self.file_type = file_type.value
        self.start_page = start_page
        self.end_page = end_page
        self.started_at = started_at
        self.ended_at = ended_at
        self.errors = errors

    def __str__(self):
        return (f'EXTRACTED TEXT [id]: {self.id_}, [content]: "{self.content}", '
                f'[status]: {self.status}, [file_type]: {self.file_type}, '
                f'[start_page]: {self.start_page}, [end_page]: {self.end_page}, '
                f'[started_at]: {self.started_at}, '
                f'[ended_at]: {self.ended_at}')

    def __repr__(self):
        return (f'DocExtractedText({self.id_}, {self.content}, {self.status}, '
                f'{self.file_type}, {self.start_page}, {self.end_page}, '
                f'{self.started_at}, {self.ended_at}, {self.errors})')


class DocTextExtractionRequestSchema(Schema):
    """Schema for the clients' text extraction REST requests.

    :code:`/v1/text-extraction/doc - POST`

    Fields:
        start_page (:obj:`int`), `optional`, defaults to :obj:`None`:
            The first page (1-indexed) from which to extract the text. If
            the start page is not specified, the text will be extracted from
            the first page of the document.
        end_page (:obj:`int`), `optional`, defaults to :obj:`None`:
            The last page (1-indexed) until which to extract the text. If
            :param:`start_page` and :param:`end_page` are the same, only the
            text from that page is extracted. If the end page is not
            specified, the text will be extracted until the last page of the
            document.
    """

    start_page = fields.Int()
    end_page = fields.Int()

    @pre_load
    def validate_and_set_defaults(self, data, many, **kwargs):
        """Validate fields and substitute :obj:`None` or missing fields by default values."""

        # Check start page
        if ("start_page" not in data):
            data["start_page"] = None
        else:
            data["start_page"] = int(data["start_page"])

        # Check end page
        if ("end_page" not in data):
            data["end_page"] = None
        else:
            data["end_page"] = int(data["end_page"])

        return data

    class Meta:
        unknown = EXCLUDE


class DocResponseSchema(Schema):
    """Schema for the response to the clients' requests.

    :code:`/v1/text-extraction/doc - POST`

    Some of the fields might not be available during the extraction of
    the text, e.g. ``content`` or ``ended_at``. Once the text has been extracted
    the ``status`` will change to ``completed`` and the missing fields will be
    available.

    Fields:
        document_id (:obj:`str`):
            The ID of the document.
        started_at (:obj:`datetime.datetime`):
            The time when the extracted text was first created.
        ended_at (:obj:`datetime.datetime`):
            The time when the text first extracted.
        status (:obj:`str`):
            The current status of the extracted text.
        content (:obj:`str`):
            The extracted text itself.
        start_page (:obj:`int`):
            The first page the text was extracted from.
        end_page (:obj:`int`):
            The last page the text was extracted from.
    """

    document_id = fields.Str(required=True)
    started_at = fields.DateTime(required=True)
    ended_at = fields.DateTime(required=True)
    status = fields.Str(required=True)
    content = fields.Str(required=True)
    start_page = fields.Int(required=True)
    end_page = fields.Int(required=True)

    @pre_dump
    def build_reponse(self, extracted_text: DocExtractedText, **kwargs):
        """Build a response with the :obj:`ExtractedText`.

        For more information, see the
        `Marshmallow documentationn
        <https://marshmallow.readthedocs.io/en/stable/api_reference.html#marshmallow.pre_dump>`__.
        """

        response = {"document_id": extracted_text.id_,
                    "content": extracted_text.content,
                    "status": extracted_text.status,
                    "file_type": extracted_text.file_type,
                    "start_page": extracted_text.start_page,
                    "end_page": extracted_text.end_page,
                    "started_at": extracted_text.started_at,
                    "ended_at": extracted_text.ended_at}

        return response

    class Meta:
        ordered = True
        unknown = EXCLUDE


class DocTextExtractionProducedMsgSchema(Schema):
    """Schema for the produced messages to the topic :attr:`KafkaTopic.DOC_TEXT_EXTRACTION`.

    Fields:
        file (:obj:`bytes`):
            The file in bytes.
        start_page (:obj:`int`):
            The first page (1-indexed) from which the text will be extracted.
        end_page (:obj:`int`):
            The last page (1-indexed) until which the text will be extracted.
    """

    file = fields.Raw(required=True)
    start_page = fields.Int(required=True)
    end_page = fields.Int(required=True)


class ConsumedMsgSchema(Schema):
    """Schema for the consumed messages.

    Fields:
        content (:obj:`Union[str, None`):
            The extracted text. It will be :obj:`None` if the text could not be
            extracted.
        status (:obj:`str`):
            The status of the extracted text.
        errors (:obj:`Union[dict, None]`):
            The warnings derived from the client's request (if any).
    """

    content = fields.Str()
    status = fields.Str()
    errors = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
