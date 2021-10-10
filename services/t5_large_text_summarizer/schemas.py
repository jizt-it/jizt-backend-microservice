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

"""Marshmallow Schemas for TextSummarizerService."""

import base64
from marshmallow import Schema, fields

__version__ = '0.1.6'


class JSONSerializableBytesField(fields.Field):
    """A JSON serializable :obj:`bytes` field.

    For more info, see the
    `Marshmallow docs <https://marshmallow.readthedocs.io/en/stable/marshmallow.fields.html>`__.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize :obj:`bytes` to :obj:`string`.

        For more info, see base class.
        """

        if value is None:
            return None
        b64_encoded = base64.b64encode(value)
        return b64_encoded.decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize :obj:`bytes` from :obj:`str`.

        For more info, see base class.
        """

        if isinstance(value, str):
            b64_encoded_str = value.encode('utf-8')
            return base64.decodebytes(b64_encoded_str)
        raise super(JSONSerializableBytesField,
                    self).make_error('Value must be a string.')


class TextSummarizationConsumedMsgSchema(Schema):
    """Schema for the consumed messages from the topic :attr:`KafkaTopic.TEXT_SUMMARIZATION`.

    Fields:
        text_encodings (:obj:`JSONSerializableBytesField`):
            The encoded text to be summarized.
        params (:obj:`dict`):
            The params used in the summary generation.
    """

    text_encodings = JSONSerializableBytesField(required=True)
    params = fields.Dict(required=True)


class TextPostprocessingProducedMsgSchema(Schema):
    """Schema for the produced messages to the topic :attr:`KafkaTopic.TEXT_POSTPROCESSING`.

    Fields:
        summary (:obj:`str`):
            The generated summary.
        params (:obj:`dict`):
            The valid params, onced checked by the summarizer.
    """

    summary = fields.Str(required=True)
    params = fields.Dict(required=True)


class DispatcherProducedMsgSchema(Schema):
    """Schema for the produced messages to the topic :attr:`KafkaTopic.DISPATCHER`.

    Fields:
        summary_status (:obj:`str`):
            The status of the summary.
        warnings (:obj:`dict`):
            The warnings derived from the client's request (if any).
    """

    summary_status = fields.Str(required=True)
    warnings = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
