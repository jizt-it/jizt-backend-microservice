# Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
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

"""Marshmallow Schemas for TextPostprocessorService."""

from marshmallow import Schema, fields

__version__ = '0.1.5'


class TextPostprocessingConsumedMsgSchema(Schema):
    """Schema for the consumed messages from the topic :attr:`KafkaTopic.TEXT_POSTPROCESSING`.

    Fields:
        source (:obj:`str`):
            The text to be post-processed.
        params (:obj:`dict`):
            The valid params, onced checked by the summarizer.
    """

    summary = fields.Str(required=True)
    params = fields.Dict(required=True)


class DispatcherProducedMsgSchema(Schema):
    """Schema for the produced messages to the topic :attr:`KafkaTopic.DISPATCHER`.

    Fields:
        output (:obj:`str`):
            The post-processed text.
        params (:obj:`dict`):
            The valid params, onced checked by the summarizer.
        warnings (:obj:`dict`):
            The warnings derived from the client's request (if any).
    """

    summary_status = fields.Str(required=True)
    output = fields.Str(required=True)
    params = fields.Dict(required=True)
    warnings = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
