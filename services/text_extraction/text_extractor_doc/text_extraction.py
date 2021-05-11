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
from supported_formats import SupportedFormat as sf
from exceptions import (Base64DecodingError,
                        FormatNotSupportedException,
                        TextExtractionError,
                        PageOutOfRangeError)


class TextExtractor:
    """Base class for text extraction."""

    @classmethod
    def get_text(cls, b64file: bytes, extension: str, pages: tuple = None) -> str:
        """Extract the text from a document.

        Args:
            b64file (:obj:`bytes`):
                The file from which to extract the text, encoded in base64.
            extension (:obj:`str`):
                The extension of the file, without the leading dot, e.g., 'pdf'.
            pages (:obj:`tuple`):
                The pages (1-indexed) from which to extract the text, e.g., (1, 40).
                The bounds are both inclusive.

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

        if pages[0] < 1 or pages[1] < 1 or pages[0] > pages[1]:
            raise PageOutOfRangeError(pages)

        try:
            decoded_file = base64.b64decode(b64file)
        except (TypeError, binascii.Error):
            raise Base64DecodingError()

        try:
            supported_format = sf(extension)
        except ValueError:
            raise FormatNotSupportedException(extension)

        # if supported_format in (sf.PDF, sf.XPS, sf.OXPS,
        #                         sf.CBS, sf.FB2, sf.EPUB):
        return MuPDFTextExtractor.get_text(decoded_file, supported_format.value, pages)

        # elif supported_format in `future supported formats`


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
    def get_text(cls, stream: bytes, extension: str, pages: tuple = None) -> str:
        """Extract the text from a document.

        Args:
            stream (:obj:`bytes`):
                The file in memory from which to extract the text.
            extension (:obj:`str`):
                The extension of the file, without the leading dot, e.g., 'pdf'.
            pages (:obj:`tuple`):
                The pages (1-indexed) from which to extract the text, e.g., (1, 40).
                The bounds are both inclusive.

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
                pages = pages if pages is not None else (0, len(doc))
                text.write(' '.join([word_info[4]
                                     for i in range(pages[0], pages[1]+1)
                                     for word_info in doc[i-1].get_text("words")]))
        except IndexError:
            raise PageOutOfRangeError(pages)
        except RuntimeError:
            raise TextExtractionError()

        return text.getvalue()
