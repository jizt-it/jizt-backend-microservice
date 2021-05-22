# Copyright (C) 2020 Diego Miguel Lozano <dml1001@alu.ubu.es>
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


"""Text extraction from documents."""

__version__ = '0.1.0'

import base64
import binascii
import fitz  # PyMuPDF
from io import StringIO
from supported_file_types import SupportedFileType as sf
from exceptions import (Base64DecodingError,
                        FormatNotSupportedException,
                        TextExtractionError,
                        PageOutOfRangeError)


class TextExtractor:
    """Base class for text extraction."""

    @classmethod
    def get_text(
        cls,
        b64file: bytes,
        extension: str,
        start_page: int = None,
        end_page: int = None
    ) -> str:
        """Extract the text from a document.

        Args:
            b64file (:obj:`bytes`):
                The file from which to extract the text, encoded in base64.
            extension (:obj:`str`):
                The extension of the file, without the leading dot, e.g., 'pdf'.
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


        Returns:
            :obj:`str`: the extracted text.

        Raises: 
            :obj:`PageOutOfRangeError`: if any of the pages is smaller than 1, or the
                                        ``page[1]`` is smaller than ``page[0]``.
            :obj:`FormatNotSupportedException`: if the specified format is not
                                                supported.
            :obj:`Base64DecodingError`: if there was an error decoding the file.
            :obj:`TextExtractionError`: see child classes.
        """

        start_page = start_page if start_page is not None else 1
        end_page = end_page if end_page is not None else len(doc)
        if start_page < 1 or end_page < 1 or start_page > end_page:
            raise PageOutOfRangeError(start_page, end_page)

        try:
            decoded_file = base64.b64decode(b64file)
        except (TypeError, binascii.Error):
            raise Base64DecodingError()

        try:
            supported_format = sf(extension)
        except ValueError:
            raise FormatNotSupportedException(extension)

        # if supported_file_type in (sf.PDF, sf.XPS, sf.OXPS,
        #                         sf.CBS, sf.FB2, sf.EPUB):
        return MuPDFTextExtractor.get_text(decoded_file, supported_format.value,
                                           start_page, end_page)

        # elif supported_file_type in `future supported file types`


class MuPDFTextExtractor(TextExtractor):
    """Text extractor for the typefiles supported by the ``PyMuPDF`` module.
    
    See the `PyMuPDF repo <https://github.com/pymupdf/PyMuPDF#introduction>`__ for
    more information.

    The extensions currently supported by ``PyMuPDF`` are:

    * ``.pdf``
    * ``.xps``
    * ``.oxps``
    * ``.cbz``
    * ``.fb2``
    * ``.epub``
    """

    @classmethod
    def get_text(
        cls,
        stream: bytes,
        extension: str,
        start_page: int = None,
        end_page: int = None
    ) -> str:
        """Extract the text from a document.

        Args:
            stream (:obj:`bytes`):
                The file in memory from which to extract the text.
            extension (:obj:`str`):
                The extension of the file, without the leading dot, e.g., 'pdf'.
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

        Returns:
            :obj:`str`: the extracted text.

        Raises: 
            :obj:`PageOutOfRangeError`: if any of the pages is smaller than 1, or the
                                        ``page[1]`` is smaller than ``page[0]`` or
                                        the document has less pages than specified by
                                        ``pages[1]``.
            :obj:`TextExtractionError`: if the text could not be extracted.
        """

        text = StringIO()

        try:
            with fitz.open(stream=stream, filetype=extension) as doc:
                start_page = start_page if start_page is not None else 1
                end_page = end_page if end_page is not None else len(doc)
                text.write(' '.join([word_info[4]
                                     for i in range(start_page, end_page+1)
                                     for word_info in doc[i-1].get_text("words")]))
        except IndexError:
            raise PageOutOfRangeError(start_page, end_page)
        except RuntimeError:
            raise TextExtractionError()

        return text.getvalue()
