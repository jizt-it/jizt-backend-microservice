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

"""Text Summarizer."""

__version__ = '0.1.5'

import os
import argparse
import logging
import pickle
from text_summarization import Summarizer
from kafka.kafka_topics import KafkaTopic
from kafka.kafka_producer import Producer
from kafka.kafka_consumer import Consumer
from confluent_kafka import Message, KafkaError, KafkaException
from schemas import (TextSummarizationConsumedMsgSchema,
                     DispatcherProducedMsgSchema,
                     TextPostprocessingProducedMsgSchema)
from utils.param_validation import validate_params
from utils.summary_status import SummaryStatus
from pathlib import Path

TOKENIZER_PATH = (
    Path(os.environ['MODELS_MOUNT_PATH']) / Path(os.environ['TOKENIZER_PATH'])
)

MODEL_PATH = (
    Path(os.environ['MODELS_MOUNT_PATH']) / Path(os.environ['MODEL_PATH'])
)

parser = argparse.ArgumentParser(description='Text summarizer service. '
                                             'Default log level is WARNING.')
parser.add_argument('-i', '--info', action='store_true',
                    help='turn on python logging to INFO level')
parser.add_argument('-d', '--debug', action='store_true',
                    help='turn on python logging to DEBUG level')


class TextSummarizerService:
    """Text summarizer service."""

    def __init__(self, log_level):
        self.log_level = log_level
        logging.basicConfig(
            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
            level=self.log_level,
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )
        self.logger = logging.getLogger("TextSummarizer")

        self.logger.debug("Loading t5-large models...")
        self.summarizer = Summarizer(TOKENIZER_PATH, MODEL_PATH)
        self.logger.debug("Models loaded!")

        self.producer = Producer()
        self.consumer = Consumer()
        self.consumed_msg_schema = TextSummarizationConsumedMsgSchema()
        self.disp_produced_msg_schema = DispatcherProducedMsgSchema()
        self.post_produced_msg_schema = TextPostprocessingProducedMsgSchema()

    def run(self):
        try:
            topics_to_subscribe = [KafkaTopic.TEXT_SUMMARIZATION.value]
            self.consumer.subscribe(topics_to_subscribe)
            self.logger.debug(f'Consumer subscribed to topic(s): '
                              f'{topics_to_subscribe}')

            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        self.logger.error(f'{msg.topic()} in partition {msg.partition} '
                                          f'{msg.partition()} reached end at offset '
                                          f'{msg.offset()}')
                    elif msg.error():
                        self.logger.error(f"Error in consumer loop: {msg.error()}")
                        raise KafkaException(msg.error())
                else:
                    self.logger.debug(f'Message consumed: [key]: {msg.key()}, '
                                      f'[value]: "{msg.value()[:500]} [...]"')

                    update_status = {"summary_status": SummaryStatus.SUMMARIZING.value}
                    self._produce_message(
                        KafkaTopic.DISPATCHER.value,
                        msg.key(),
                        self.disp_produced_msg_schema.dumps(update_status)
                    )

                    data = self.consumed_msg_schema.loads(msg.value())
                    topic = KafkaTopic.TEXT_POSTPROCESSING.value
                    serialized_encoded_text = data.pop('text_encodings')
                    encoded_text = pickle.loads(serialized_encoded_text)

                    params, invalid_params, warnings = validate_params(data['params'])
                    self.logger.debug(f"Valid params: {params}")
                    self.logger.debug(f"Invalid params: {invalid_params}")
                    self.logger.debug(f"Warnings: {warnings}")
                    data['params'] = params  # update params to keep only the valid ones
                    summarized_text = self.summarizer.summarize(encoded_text, **params)
                    data['summary'] = summarized_text
                    message_value = self.post_produced_msg_schema.dumps(data)
                    self._produce_message(
                        topic,
                        msg.key(),
                        message_value
                    )
                    self.logger.debug(
                        f'Message produced: [topic]: "{topic}", '
                        f'[key]: {msg.key()}, [value]: '
                        f'"{message_value[:500]} [...]'
                    )

                    update_status['warnings'] = warnings
                    self._produce_message(
                        KafkaTopic.DISPATCHER.value,
                        msg.key(),
                        self.disp_produced_msg_schema.dumps(update_status)
                    )
        finally:
            self.logger.debug("Consumer loop stopped. Closing consumer...")
            self.consumer.close()  # close down consumer to commit final offsets

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
            message_key (:obj:`str`);
                The Kafka message key.
            message_value (:obj:`str`);
                The Kafka message value.
        """

        try:
            self.producer.produce(
                topic,
                key=message_key,
                value=message_value,
                on_delivery=self._kafka_delivery_callback
            )
        except BufferError as err:
            error_msg = (f"Local producer queue is full ({len(self.producer)} "
                         f"messages awaiting delivery)")
            self.logger.error(error_msg)
            raise Exception(error_msg) from err

        # Wait up to 1 second for events. Callbacks will
        # be invoked during this method call.
        self.producer.poll(1)

    def _kafka_delivery_callback(self, err: KafkaError, msg: Message):
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


if __name__ == "__main__":
    args = parser.parse_args()
    info_log_level = args.info
    debug_log_level = args.debug

    log_level = logging.WARNING
    if info_log_level:
        log_level = logging.INFO
    if debug_log_level:
        log_level = logging.DEBUG

    text_summarizer_service = TextSummarizerService(log_level)
    text_summarizer_service.run()
