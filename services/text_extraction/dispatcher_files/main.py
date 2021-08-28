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

"""Text Extraction Dispatcher REST API v1."""

__version__ = '0.1.10'

import os
import re
import argparse
import filetype
import logging
from datetime import datetime
from werkzeug import serving
from flask import Flask, request
from flask_restful import Api, Resource, abort
from flask_cors import CORS
from confluent_kafka import Message, KafkaError
from kafka.kafka_topics import KafkaTopic
from kafka.kafka_producer import Producer
from kafka.kafka_consumer import ConsumerLoop
from kafka.unique_key import get_unique_key
from data.extracted_text_status import ExtractedTextStatus
from data.text_extraction_dao_factory import TextExtractionDAOFactory
from data.schemas import (DocExtractedText, DocTextExtractionRequestSchema,
                          DocResponseSchema)
from data.supported_file_types import SupportedFileType
from pathlib import Path

# Flask config
FLASK_HOST = "0.0.0.0"
FLASK_PORT = os.environ['FLASK_SERVER_PORT']

# Args for Python script execution
parser = argparse.ArgumentParser(description='Text Extraction Dispatcher '
                                             'service. Default log level is '
                                             'WARNING.')
parser.add_argument('-i', '--info', action='store_true',
                    help='turn on Python logging to INFO level')
parser.add_argument('-d', '--debug', action='store_true',
                    help='turn on Python logging and Flask to DEBUG level')


class DispatcherService:
    """Dispatcher service.

    This service carries out several tasks:

        * Validate the clients' requests, making sure the body contains
          the necessary fields.
        * Publish messages to the proper microservice Kafka topic, in order
          to begin the text processing.
        * Manage the extracted texts, storing them in a DB for cache purposes.
    """

    def __init__(self, log_level):
        self.app = Flask(__name__)
        self.api = Api(self.app)

        self.cors = CORS(self.app, resources={
            # Origins examples: http://jizt.it, https://app.jizt.it, http://jizt.it/hi
            r"*": {"origins": r"https?://\w*\.?jizt\.it/?.*",
                   "allow_headers": ['Content-Type']}
        })

        logging.basicConfig(
            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
            level=log_level,
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )
        self.logger = logging.getLogger("Text Extraction Dispatcher")
        # Comment out next line to turn on flask_cors logs
        # logging.getLogger("flask_cors").level = log_level

        self.db = self._connect_to_database(log_level)

        # Create Kafka Producer and ConsumerLoop
        self.kafka_producer = Producer()
        self.kafka_consumerloop = ConsumerLoop(self.db)

        # Endpoints
        self.api.add_resource(
            TextExtraction,
            "/v1/text-extraction/doc",
            endpoint="text-extraction",
            resource_class_kwargs={'dispatcher_service': self,
                                   'kafka_producer': self.kafka_producer}
        )

        self.api.add_resource(
            Health,
            "/",
            "/healthz",
            endpoint="readiness-liveness-probe",
            resource_class_kwargs={'dispatcher_service': self,
                                   'kafka_producer': self.kafka_producer}
        )

    def run(self):
        try:
            self.kafka_consumerloop.start()
            self.app.run(host=FLASK_HOST,
                         port=FLASK_PORT,
                         debug=(self.logger.level == "DEBUG"))
        finally:
            self.kafka_consumerloop.stop()

    def kafka_delivery_callback(self, err: KafkaError, msg: Message):
        """Kafka per-message delivery callback.

        When passed to :meth:`confluent_kafka.Producer.produce` through
        the :attr:`on_delivery` attribute, this method will be triggered
        by :meth:`confluent_kafka.Producer.poll` or
        :meth:`confluent_kafka.Producer.flush` when wither a message has
        been successfully delivered or the delivery failed (after
        specified retries).

        Args:
            err (:obj:`confluent_kafka.KafkaError`):
                The Kafka error.
            msg (:obj:`confluent_kafka.Message`):
                The produced message, or an event.
        """

        if err:
            self.logger.debug(f'Message delivery failed: {err}')
        else:
            self.logger.debug(f'Message delivered sucessfully: [topic]: '
                              f'"{msg.topic()}", [partition]: "{msg.partition()}"'
                              f', [offset]: {msg.offset()}')

    @classmethod
    def _connect_to_database(cls, log_level):
        """Manage connection with the database.

        Args:
            log_level (:obj:`int`):
                The log level.

        Returns:
            :obj:`TextExtractionDAOFactory`: an instance to the database.
        """

        # PostgreSQL connection data
        with open((Path(os.environ['PG_SECRET_PATH'])
                   / Path(os.environ['PG_USERNAME_FILE'])), 'r') as username:
            pg_username = username.readline().rstrip('\n')
        with open((Path(os.environ['PG_SECRET_PATH'])
                   / Path(os.environ['PG_PASSWORD_FILE'])), 'r') as password:
            pg_password = password.readline().rstrip('\n')

        return TextExtractionDAOFactory(
            os.environ['PG_HOST'],
            os.environ['PG_DBNAME'],
            pg_username,
            pg_password,
            log_level
        )


class TextExtraction(Resource):
    """Resource for text extraction requests."""

    def __init__(self, **kwargs):
        self.request_schema = DocTextExtractionRequestSchema()
        self.doc_produced_msg_schema = DocTextExtractionRequestSchema()
        self.ok_response_schema = DocResponseSchema()
        self.dispatcher_service = kwargs['dispatcher_service']
        self.kafka_producer = kwargs['kafka_producer']

    def post(self):
        """HTTP POST.

        Submit a request for text extraction. When a client first makes a POST
        request, a response is given with a unique id. The client must then make
        periodic GET requests with the specific id to check the status of the
        text extraction status. Once the text extraction is completed, the GET
        request will contain the extracted text.

        Returns:
            :obj:`dict`: A 202 Accepted response with a JSON body containing a
            unique id, e.g., {'id_': 73c3de4175449987ef6047f6e0bea91c1036a8599b}.

        Raises:
            :class:`http.client.HTTPException`: If the request body
            JSON is not valid.
        """

        # Check if the post request has the file part
        if 'file' not in request.files:
            abort(400, errors=f'No file was sent')

        data = request.json
        # The validation will modify the data (i.e. it already loads it)
        self._validate_post_request_json(data)

        file = request.files['file'].read()  # type(file) -> ``bytes``
        data["file"] = file
        start_page = data['start_page']  # either ``int`` or ``None``
        end_page = data['end_page']  # either ``int`` or ``None``

        file_extension = filetype.guess(file).extension
        supported_extensions = [f.value for f in SupportedFileType]
        if file_extension not in supported_extensions:
            abort(400, errors=f'The file extension {file_extension} is '
                               'currently not supported. Supported file types: '
                              f'{supported_extensions}')
        else:
            file_extension = SupportedFileType(file_extension)

        message_key = get_unique_key(file, start_page, end_page)

        # ``None`` if it does not exist
        extracted_text = self.dispatcher_service.db.get_extracted_text(message_key)

        if (extracted_text is not None
                and extracted_text.status != ExtractedTextStatus.FAILED.value):
            self.dispatcher_service.logger.debug(
                f'Extracted text already exists: [id] {extracted_text.id_}, '
                f'[content] '
                f'{extracted_text.content[:50] if extracted_text.content is not None else None}, ' 
                f'[status] {extracted_text.status}, [file_type] '
                f'{extracted_text.file_type}, [start_page] '
                f'{extracted_text.start_pagee}, [end_page] '
                f'{extracted_text.end_page}, [started_at] '
                f'{extracted_text.started_at}, [ended_at] '
                f'{extracted_text.ended_at}, [errors] {extracted_text.errors}'
            )
        else:
            extracted_text = DocExtractedText(
                id_=message_key,
                content=None,
                status=ExtractedTextStatus.EXTRACTING,
                file_type=file_extension,
                start_page=start_page,
                end_page=end_page,
                started_at=datetime.now(),
                ended_at=None,
                errors=None
            )
            self.dispatcher_service.db.insert_extracted_text(extracted_text)

            topic = KafkaTopic.DOC_TEXT_EXTRACTION.value
            message_value = self.doc_produced_msg_schema.dumps(data)
            self._produce_message(topic,
                                  message_key,
                                  message_value)

            self.dispatcher_service.logger.debug(
                f'Message produced: [topic]: "{topic}", '
                f'[key]: {message_key}, [value]: '
                f'"{message_value[:500]} [...]"'
            )

        response = self.ok_response_schema.dump(extracted_text)
        return response, 202  # ACCEPTED

    def get(self, document_id):
        """HTTP GET.

        Gives a response with the text extraction status and, in case the text
        extraction is completed, the extracted text itself.

        Args:
            document_id (:obj:`str`):
                The id of the requested document.

        Returns:
            :obj:`dict`: A ``200 OK`` response with a JSON body containing the
            extracted text. For info on the extracted text fields, see
            :class:`data.schemas.DocExtractedText`.

        Raises:
            :class:`http.client.HTTPException`: If there exists no extracted
            text with the specified id.
        """

        extracted_text = self.dispatcher_service.db.get_extracted_text(document_id)
        if extracted_text is None:
            abort(404, errors=f'Extracted text "{document_id}" not found.')  # NOT FOUND
        response = self.ok_response_schema.dump(extracted_text)
        return response, 200  # OK

    def _validate_post_request_json(self, json):
        """Validate JSON in a POST request body.

        The JSON will not be valid if it does not contain
        all the mandatory fields defined in the
        :class:`.schemas.DocTextExtractionRequestSchema` class.

        Args:
            json (:obj:`dict`):
                The JSON to be validated.

        Raises:
            :class:`http.client.HTTPException`: If the JSON
            is not valid.
        """

        errors = self.request_schema.validate(json)
        if errors:
            abort(400, errors=errors)  # 400 Bad Request

    def _produce_message(self,
                         topic: str,
                         message_key: int,
                         message_value: str):
        """Produce Kafka message.

        If the local producer queue is full, the request will be
        aborted.

        Args:
            topic (:obj:`str`):
                The topic to produce the message to.
            message_key (:obj:`int`);
                The Kafka message key.
            message_value (:obj:`str`);
                The Kafka message value.
        """

        try:
            self.kafka_producer.produce(
                topic,
                key=str(message_key),
                value=message_value,
                on_delivery=self.dispatcher_service.kafka_delivery_callback
            )
        except BufferError:
            error_msg = (f"Local producer queue is full ({len(self.kafka_producer)} "
                         f"messages awaiting delivery)")
            self.dispatcher_service.logger.error(error_msg)
            abort(503, error=error_msg)  # 503 Service Unavailable

        # Wait up to 1 second for events. Callbacks will
        # be invoked during this method call.
        self.kafka_producer.poll(1)


class Health(Resource):
    """Resource for probing service liveness."""

    def __init__(self, **kwargs):
        self.dispatcher_service = kwargs['dispatcher_service']
        self.kafka_producer = kwargs['kafka_producer']

    def get(self):
        """Check service health.

        Returns:
            :obj:`dict`: A ``200 OK`` response if everything is working, otherwise
            a ``500 INTERNAL SERVER ERROR``.
        """

        return 200 if (self._is_kafka_producer_alive()
                       and self._is_kafka_consumer_alive()) else 500

    def _is_kafka_producer_alive(self):
        """Check if Kafka producer is up and running.

        Returns:
            :obj:`bool`: whether the producer is alive or not.
        """

        return (self.kafka_producer is not None
                and self.kafka_producer.list_topics().topics)

    def _is_kafka_consumer_alive(self):
        """Check if Kafka consumer is up and running.

        Returns:
            :obj:`bool`: whether the consumer is alive or not.
        """
        return not self.dispatcher_service.kafka_consumerloop.stopped()


def disable_endpoint_logs():
    """Disable logs for requests to specific endpoints."""

    disabled_endpoints = ('/', '/healthz', '/v1/text-extraction/.+')

    parent_log_request = serving.WSGIRequestHandler.log_request

    def log_request(self, *args, **kwargs):
        """See `base class <https://github.com/pallets/werkzeug/blob/71cf9902012338f8ee98338fa7bba50572606637/src/werkzeug/serving.py#L378>`__."""

        if not any(re.match(f"{de}$", self.path) for de in disabled_endpoints):
            parent_log_request(self, *args, **kwargs)

    serving.WSGIRequestHandler.log_request = log_request


if __name__ == "__main__":
    args = parser.parse_args()
    info_log_level = args.info
    debug_log_level = args.debug

    log_level = logging.WARNING
    if info_log_level:
        log_level = logging.INFO
    if debug_log_level:
        log_level = logging.DEBUG

    disable_endpoint_logs()

    dispatcher_service = DispatcherService(log_level)
    dispatcher_service.run()
