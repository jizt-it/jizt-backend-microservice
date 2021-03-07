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


def get_unique_key(source: str, model: str, params: dict) -> str:
    """Get a unique key for a message.

    This method hashes the string formed by concatenating the
    :attr:`source`, :attr:`model` and :attr:`param` attributes.
    SHA-256 algorithm is used.

    Args:
        source (:obj:`str`):
            ``source`` attribute in the JSON body of the request.
        model (:obj:`str`):
            ``model`` attribute in the JSON body of the request.
        params (:obj:`params`):
            ``params`` attribute in the JSON body of the request.

    Returns:
        :obj:`str`: The unique, SHA-256 ecrypted key.
    """

    return hashlib.sha256(
        ("".join([source, model, str(params)])).encode()
    ).hexdigest()
