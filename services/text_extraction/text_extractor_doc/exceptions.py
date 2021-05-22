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
# For license information on the libraries used, see LICENSE

"""Exceptions in text extraction from docs."""

__version__ = '0.1.0'


class FormatNotSupportedException(Exception):
    """Exception raised for non-supported file formats.

    Attributes:
        extension (obj:`str`):
            The unsupported file extension without the leading dot, e.g., 'tex'.
        message (obj:`str`):
            Information about the exception.
    """

    def __init__(self, extension: str, message: str = None):
        self._extension = extension
        self._message = (f"the file format '.{extension}' is currently not supported"
                         if message is None else message)
        super().__init__(self._message)

    @property
    def extension(self):
        return self._extension

    @property
    def message(self):
        return self._message


class TextExtractionError(RuntimeError):
    """Error raised when there was an error in the text extraction.

    Attributes:
        message (obj:`str`):
            Information about the error.
    """

    def __init__(self, message: str = None):
        self._message = ("couldn't extract the text"
                         if message is None else message)
        super().__init__(self._message)

    @property
    def message(self):
        return self._message


class PageOutOfRangeError(IndexError):
    """Error raised when the specified page is out of the document page range.

    Attributes:
        start_page (obj:`int`):
            The start page that originated the error.
        end_page (obj:`int`):
            The end page that originated the error.
        message (obj:`str`):
            Information about the error.
    """

    def __init__(self, start_page: int, end_page: int, message: str = None):
        self._start_page = start_page
        self._end_page = end_page
        self._message = (f"pages ({start_page}, {end_page}) out of range"
                         if message is None else message)
        super().__init__(self._message)

    @property
    def start_page(self):
        return self._start_page

    @property
    def end_page(self):
        return self._end_page

    @property
    def message(self):
        return self._message


class Base64DecodingError(Exception):
    """Error raised when there was an error in the file decoding.

    Attributes:
        message (obj:`str`):
            Information about the error.
    """

    def __init__(self, message: str = None):
        self._message = ("couldn't decode the file"
                         if message is None else message)
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
