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

"""Summary Data Access Object (DAO) Implementation."""

__version__ = '0.1.7'

import logging
import psycopg2
import hashlib
from io import StringIO
from collections import OrderedDict
from psycopg2.extras import Json
from summary_dao_interface import SummaryDAOInterface
from schemas import Summary
from summary_status import SummaryStatus
from supported_models import SupportedModel
from supported_languages import SupportedLanguage
from datetime import datetime


class SummaryDAOPostgresql(SummaryDAOInterface):  # TODO: manage errors in excepts
    """Summary DAO implementation for Postgresql.

    For more information, see base class.
    """

    def __init__(self, host, dbname, user, password, log_level):
        logging.basicConfig(
            format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
            level=log_level,
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )
        self.logger = logging.getLogger("SummaryDAOPostgresql")

        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password

    def get_summary(self, id_: str):
        """See base class."""

        SQL = """SELECT summary_id, content, summary, model_name, params,
                        status, started_at, ended_at, language_tag
                 FROM jizt.id_raw_id_preprocessed JOIN jizt.summary
                      ON id_preprocessed = summary_id JOIN jizt.source
                      USING (source_id)
                 WHERE id_raw = %s;"""

        SQL_UPDATE_LAST_ACCESSED = """UPDATE jizt.id_raw_id_preprocessed
                                      SET last_accessed = %s
                                      WHERE id_raw = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_UPDATE_LAST_ACCESSED, (datetime.now(), id_))
                cur.execute(SQL, (id_,))
                summary_row = cur.fetchone()
                conn.commit()
                if summary_row is not None:
                    return Summary(
                        id_=summary_row[0],
                        source=summary_row[1],
                        output=summary_row[2],
                        model=SupportedModel(summary_row[3]),
                        params=summary_row[4],
                        status=SummaryStatus(summary_row[5]),
                        started_at=summary_row[6],
                        ended_at=summary_row[7],
                        language=SupportedLanguage(summary_row[8])
                    )
                return None  # summary doesn't exist
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def insert_summary(self, summary: Summary, cache: bool):
        """See base class."""

        SQL_GET_SOURCE = """SELECT source_id
                            FROM jizt.source
                            WHERE source_id = %s;"""

        SQL_INSERT_SOURCE = """INSERT INTO jizt.source
                               VALUES (%s, %s, %s);"""

        SQL_INSERT_SUMMARY = """INSERT INTO jizt.summary
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        SQL_INSERT_ID = """INSERT INTO jizt.id_raw_id_preprocessed
                           VALUES (%s, %s, %s, %s);"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                source_id = self._get_unique_key(summary.source)
                cur.execute(SQL_GET_SOURCE, (source_id,))
                retrieved_source_id = cur.fetchone()
                if retrieved_source_id is None:
                    cur.execute(
                        SQL_INSERT_SOURCE,
                        (source_id, summary.source, len(summary.source))
                    )
                output_length = (len(summary.output) if summary.output is not None
                                 else None)
                cur.execute(
                    SQL_INSERT_SUMMARY,
                    (summary.id_, source_id,
                     summary.output, output_length,
                     summary.model, Json(summary.params),
                     summary.status, summary.started_at,
                     summary.ended_at, summary.language)
                )
                cur.execute(SQL_INSERT_ID, (summary.id_,
                                            summary.id_,
                                            cache,
                                            datetime.now()))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def delete_summary(self,
                       id_: str,
                       delete_source: bool = False):
        """See base class."""

        # Because of ON DELETE CASCADE, this will delete both the
        # source and the summary
        SQL_DELETE_ALSO_SOURCE = """DELETE FROM jizt.source
                                    WHERE source_id = (
                                        SELECT source_id FROM jizt.summary
                                        WHERE summary_id = %s
                                    );"""

        # This will not delete the source
        SQL_DELETE_SUMMARY = """DELETE FROM jizt.summary
                                WHERE summary_id = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                sql = SQL_DELETE_ALSO_SOURCE if delete_source else SQL_DELETE_SUMMARY
                cur.execute(sql, (id_,))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def update_summary(self, id_: str, **kwargs):
        """See base class."""

        ordered_kwargs = OrderedDict(kwargs)

        # Convert dicts to Json
        dicts = [key for key in ordered_kwargs
                 if isinstance(ordered_kwargs[key], dict)]
        for key in dicts:
            ordered_kwargs[key] = Json(ordered_kwargs[key])

        keys = list(ordered_kwargs.keys())
        values = list(ordered_kwargs.values()) + [id_]
        concat = StringIO()
        concat.write("UPDATE jizt.summary SET ")
        for field in keys[:-1]:
            concat.write(f"{field} = %s, ")
        concat.write(f"{keys[-1]} = %s ")
        concat.write("FROM jizt.id_raw_id_preprocessed ")
        concat.write("WHERE id_raw = %s AND id_preprocessed = summary_id;")

        SQL = concat.getvalue()

        if self.summary_exists(id_):
            conn = None
            try:
                conn = self._connect()
                with conn.cursor() as cur:
                    cur.execute(SQL, values)
                    if cur.rowcount == 0:  # nothing updated
                        return None
                    conn.commit()
                    return self.get_summary(id_)
            except (Exception, psycopg2.DatabaseError) as error:
                self.logger.error(error)
            finally:
                if conn is not None:
                    conn.close()
        else:
            return None

    def update_source(self,
                      old_source: str,
                      new_source: str,
                      old_summary_id: str,
                      new_summary_id: str):
        """See base class."""

        # The source id is also modified in the summary table
        # because of ON UPDATE CASCADE
        SQL_UPDATE_SOURCE = """UPDATE jizt.source
                               SET source_id = %s,
                                   content = %s,
                                   content_length = %s
                               WHERE source_id = %s;"""

        # The id in id_raw_id_preprocessed is also updated
        # because of ON UPDATE CASCADE
        SQL_UPDATE_SUMMARY_ID = """UPDATE jizt.summary
                                   SET summary_id = %s
                                   WHERE summary_id = %s;"""

        # We insert the binding (new_summary_id -> new_summary_id) so that a summary
        # can be also retrieved with its preprocessed id
        SQL_INSERT_PREPROCESSED_ID = """INSERT INTO jizt.id_raw_id_preprocessed
                                        (id_raw, id_preprocessed, cache, last_accessed)
                                        SELECT %s, %s, cache, %s
                                        FROM jizt.id_raw_id_preprocessed
                                        WHERE id_raw = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                old_source_id = self._get_unique_key(old_source)
                new_source_id = self._get_unique_key(new_source)
                cur.execute(SQL_UPDATE_SOURCE, (new_source_id, new_source,
                                                len(new_source), old_source_id))
                cur.execute(SQL_UPDATE_SUMMARY_ID, (new_summary_id, old_summary_id))
                cur.execute(SQL_INSERT_PREPROCESSED_ID, (new_summary_id,
                                                         new_summary_id,
                                                         datetime.now(),
                                                         old_summary_id))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def update_preprocessed_id(self,
                               raw_id: str,
                               new_preprocessed_id: str):
        """See base class."""

        SQL_UPDATE_ID = """UPDATE jizt.id_raw_id_preprocessed
                           SET id_preprocessed = %s,
                               last_accessed = %s
                           WHERE id_raw = %s
                           RETURNING cache;"""

        SQL_UPDATE_CACHE = """UPDATE jizt.id_raw_id_preprocessed
                              SET cache = %s,
                                  last_accessed = %s
                              WHERE id_raw = %s AND cache = FALSE;"""

        # Because of ON DELETE CASCADE, this will delete both the
        # source and the summary
        SQL_DELETE_SUMMARY_OLD = """DELETE FROM jizt.source
                                    WHERE source_id = (
                                        SELECT source_id FROM jizt.summary
                                        WHERE summary_id = %s
                                    );"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_UPDATE_ID, (new_preprocessed_id,
                                            datetime.now(),
                                            raw_id))
                cache = cur.fetchone()
                if cache is not None:
                    cur.execute(SQL_UPDATE_CACHE, (cache[0],
                                                   datetime.now(),
                                                   new_preprocessed_id))
                    cur.execute(SQL_DELETE_SUMMARY_OLD, (raw_id,))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def update_cache_true(self, id_: str):
        """See base class."""

        SQL = """UPDATE jizt.id_raw_id_preprocessed
                 SET cache = TRUE,
                     last_accessed = %s
                 WHERE CACHE = FALSE AND (id_raw = %s OR id_raw IN (
                     SELECT id_preprocessed
                     FROM jizt.id_raw_id_preprocessed
                     WHERE id_raw = %s
                 ));"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL, (datetime.now(), id_, id_))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def summary_exists(self, id_: str):
        """See base class."""

        SQL_SELECT = """SELECT id_raw FROM jizt.id_raw_id_preprocessed
                        WHERE id_raw = %s;"""

        SQL_UPDATE_LAST_ACCESSED = """UPDATE jizt.id_raw_id_preprocessed
                                      SET last_accessed = %s
                                      WHERE id_raw = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_UPDATE_LAST_ACCESSED, (datetime.now(), id_))
                cur.execute(SQL_SELECT, (id_,))
                conn.commit()
                return cur.fetchone() is not None
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def source_exists(self, source: str):
        """See base class."""

        SQL = """SELECT source_id FROM jizt.source
                 WHERE source_id = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                source_id = self._get_unique_key(source)
                cur.execute(SQL, (source_id,))
                return cur.fetchone() is not None
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def increment_summary_count(self, id_: str):
        """See base class."""

        SQL = """UPDATE jizt.summary
                 SET request_count = request_count + 1
                 FROM jizt.id_raw_id_preprocessed
                 WHERE id_raw = %s AND id_preprocessed = summary_id
                 RETURNING request_count;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL, (id_,))
                conn.commit()
                return cur.fetchone()[0]
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def delete_if_not_cache(self, id_: str):
        """See base class."""

        SQL_DELETE = """DELETE FROM jizt.id_raw_id_preprocessed
                        WHERE id_raw = %s AND cache = FALSE
                        RETURNING id_preprocessed;"""

        # Check if the preprocessed id has to be cached
        SQL_CACHE = """SELECT cache FROM jizt.id_raw_id_preprocessed
                       WHERE id_raw = %s;"""

        # Because of ON DELETE CASCADE, this will delete both the
        # source and the summary
        SQL_DELETE_SUMMARY = """DELETE FROM jizt.source
                                WHERE source_id = (
                                    SELECT source_id FROM jizt.summary
                                    WHERE summary_id = %s
                                );"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_DELETE, (id_,))
                preprocessed_id = cur.fetchone()
                if preprocessed_id is not None:
                    if id_ == preprocessed_id[0]:  # preprocessed_id is a tuple
                        # We have already checked that cache was False
                        cur.execute(SQL_DELETE_SUMMARY, preprocessed_id)
                    else:
                        cur.execute(SQL_CACHE, preprocessed_id)
                        cache = cur.fetchone()
                        if cache is not None and not cache[0]:
                            cur.execute(SQL_DELETE_SUMMARY, preprocessed_id)
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def cleanup_cache(self, older_than_seconds: int):
        """See base class."""

        SQL_DELETE_ID_RAW = """
                 DELETE FROM jizt.id_raw_id_preprocessed
                 USING jizt.summary
                 WHERE id_preprocessed = summary_id AND
                 cache = FALSE AND status = 'completed' AND
                 last_accessed < NOW() - (%s::TEXT || ' seconds')::INTERVAL;"""

        # Delete summaries that do not correspond to any request
        SQL_DELETE_SUMMARY = """
                DELETE FROM jizt.summary
                WHERE summary_id IN (
                    SELECT summary_id
                    FROM jizt.summary
                    WHERE NOT EXISTS (SELECT 1 FROM jizt.id_raw_id_preprocessed
                                      WHERE id_preprocessed = summary_id)
                )
                RETURNING source_id;"""

        # Delete sources that do not correspond to any summary
        SQL_DELETE_SOURCE = """DELETE FROM jizt.source
                               WHERE source_id IN (%s);"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_DELETE_ID_RAW, (older_than_seconds,))
                cur.execute(SQL_DELETE_SUMMARY, (older_than_seconds,))
                summaries_id = cur.fetchall()
                if summaries_id:
                    # Transform from e.g., [(1,), (1,), (2,)] to (1, 2, 3)
                    summaries_id = tuple(i for tuple in set(summaries_id) for i in tuple)
                    cur.execute(SQL_DELETE_SOURCE, summaries_id)
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    @classmethod
    def _get_unique_key(cls, text: str) -> str:
        """Get a unique key for a text.

        SHA-256 algorithm is used.

        Args:
            text (:obj:`str`):
                The text to get the unique id from.

        Returns:
            :obj:`str`: The unique, SHA-256 ecrypted key.
        """

        return hashlib.sha256(text.encode()).hexdigest()

    def _connect(self):
        """Connect to the PostgreSQL database.

        Returns:
            :obj:`psycopg2.extensions.connection`: The connection
            to the PostgreSQL database.
        """

        try:
            return psycopg2.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
