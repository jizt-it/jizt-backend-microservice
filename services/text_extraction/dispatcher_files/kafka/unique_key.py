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

"""Unique key calculation for Kafka messages."""

__version__ = '0.1.0'

import hashlib


def get_unique_key(file: bytes, start_page: int, end_page: int) -> str:
    """Get a unique key for a file.

    This method hashes the file bytes. SHA-256 algorithm is used.

    Args:
        file (:obj:`bytes`):
            The file to get the unique key for.
        start_page (:obj:`int`):
            The first page (1-indexed) from which to extract the text. 
        end_page (:obj:`int`):
            The last page (1-indexed) until which to extract the text. 

    Returns:
        :obj:`str`: The unique, SHA-256 encrypted key.
    """

    return hashlib.sha256(f"{file}{start_page}{end_page}".encode()).hexdigest()
