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

"""Kafka Consumer."""

__version__ = '0.1.0'

import logging
import socket
from datetime import datetime
from threading import Thread, Event
from kafka_topics import KafkaTopic
from unique_key import get_unique_key
from confluent_kafka import DeserializingConsumer, Message, KafkaError, KafkaException
from confluent_kafka.serialization import StringDeserializer
from kafka_producer import Producer
from data.summary_status import SummaryStatus
from data.summary_dao_factory import SummaryDAOFactory
from data.schemas import ConsumedMsgSchema, TextEncodingProducedMsgSchema


class StoppableThread(Thread):
    """Stoppable Thread.

    Threads that inherit from this class, once started with the method
    :meth:`Thread.start`, can be stopped calling the :meth:`StoppableThread.stop`
    method.
    """

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self):
        """Stop the thread."""

        self._stop_event.set()

    def stopped(self):
        """Check whether the thread is stopped.

        Returns:
            :obj:`bool`: Whether the thread is stopped or not.
        """

        return self._stop_event.is_set()


class ConsumerLoop(StoppableThread):
    """Kafka consumer loop.

    This class implements a :class:`confluent_kafka.Consumer`.

    For more information, see the official Confluent Kafka
    `Consumer documentation
    <https://docs.confluent.io/platform/current/clients/confluent-kafka-python/#pythonclient-consumer>`__.
    """

    def __init__(self, db: SummaryDAOFactory):
        super(ConsumerLoop, self).__init__()

        logging.basicConfig(
            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )
        self.logger = logging.getLogger("DispatcherConsumerLoop")

        # Consumer configuration. Must match Stimzi/Kafka configuration.
        config = {'bootstrap.servers': "jizt-cluster-kafka-bootstrap:9092",
                  'client.id': socket.gethostname(),
                  'group.id': "dispatcher",
                  'auto.offset.reset': "earliest",
                  'session.timeout.ms': 10000,
                  'enable.auto.commit': True,  # default
                  'auto.commit.interval.ms': 5000,  # default
                  'key.deserializer': StringDeserializer('utf_8'),
                  'value.deserializer': StringDeserializer('utf_8')}
        self.consumer = DeserializingConsumer(config)
        self.producer = Producer()
        self.db = db
        self.consumed_msg_schema = ConsumedMsgSchema()
        self.text_encoding_produced_msg_schema = TextEncodingProducedMsgSchema()

    def run(self):
        try:
            topics_to_subscribe = [KafkaTopic.DISPATCHER.value]
            self.consumer.subscribe(topics_to_subscribe)
            self.logger.debug(f'Consumer subscribed to topic(s): '
                              f'{topics_to_subscribe}')

            while not self.stopped():
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
                        self.logger.error("Undefined error in consumer loop")
                        raise KafkaException(msg.error())
                else:
                    self.logger.debug(
                        f'Message consumed: [key]: {msg.key()}, '
                        f'[value]: "{msg.value()[:500]} [...]"'
                    )

                    data = self.consumed_msg_schema.loads(msg.value())

                    if data["summary_status"] == SummaryStatus.PREPROCESSING.value:
                        id_preprocessed = get_unique_key(
                            data["text_preprocessed"],
                            data["model"],
                            data["params"]
                        )
                        if self.db.summary_exists(id_preprocessed):
                            self.db.update_preprocessed_id(msg.key(), id_preprocessed)
                            self.logger.debug("Preprocessed text already exists. "
                                              "Not producing to Encoder.")
                        else:
                            old_source = self.db.get_summary(msg.key()).source
                            self.db.update_source(old_source,
                                                  data["text_preprocessed"],
                                                  msg.key(),
                                                  id_preprocessed)
                            del data["summary_status"]
                            message_value = self.text_encoding_produced_msg_schema.dumps(data)
                            self._produce_message(KafkaTopic.TEXT_ENCODING.value,
                                                  msg.key(),
                                                  message_value)
                            self.logger.debug(f"Preprocessed text does not exist. "
                                              f"Producing to Encoder.")
                    else:
                        # Important: keys must match DB columns
                        update_columns = {"status": data["summary_status"]}
                        if data["summary_status"] == SummaryStatus.COMPLETED.value:
                            update_columns.update({
                                "ended_at": datetime.now(),
                                "summary": data["output"],
                                "params": data["params"]  # validated params
                            })
                        summary = self.db.update_summary(msg.key(), **update_columns)
                        self.logger.debug(f"Consumer message processed. "
                                          f"Summary updated: {summary}")
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
            message_key (:obj:`int`);
                The Kafka message key.
            message_value (:obj:`str`);
                The Kafka message value.
        """

        try:
            self.producer.produce(
                topic,
                key=str(message_key),
                value=message_value,
                on_delivery=self.kafka_delivery_callback
            )
        except BufferError:
            error_msg = (f"Local producer queue is full ({len(self.producer)} "
                         f"messages awaiting delivery)")
            self.logger.error(error_msg)

        # Wait up to 1 second for events. Callbacks will
        # be invoked during this method call.
        self.producer.poll(1)
    
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
