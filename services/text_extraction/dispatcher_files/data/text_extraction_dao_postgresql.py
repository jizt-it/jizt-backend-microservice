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

# TODO: pretty much everything

"""Summary Data Access Object (DAO) Implementation."""

__version__ = '0.1.8'

import logging
import psycopg2
import hashlib
from io import StringIO
from collections import OrderedDict
from psycopg2.extras import Json
from summary_dao_interface import SummaryDAOInterface
from schemas import DocExtractedText
from extracted_text_status import ExtractedTextStatus
from supported_file_types import SupportedFileType
from datetime import datetime


# PostgreSQL schema
SCHEMA = 'files'


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

    def get_extracted_text(self, id_: str):
        """See base class."""

        SQL = f"""SELECT id, content, status, file_type, start_page, end_page,
                         started_at, ended_at, errors
                  FROM {SCHEMA}.extracted_text
                  WHERE id = %s;"""

        SQL_UPDATE_LAST_ACCESSED = f"""UPDATE {SCHEMA}.extracted_text
                                       SET last_accessed = %s
                                       WHERE id = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_UPDATE_LAST_ACCESSED, (datetime.now(), id_))
                cur.execute(SQL, (id_,))
                extracted_text_row = cur.fetchone()
                conn.commit()
                if extracted_text_row is not None:
                    return DocExtractedText(
                        id_=extracted_text_row[0],
                        content=extracted_text_row[1],
                        status=extracted_text_row[2],
                        file_type=extracted_text_row[3],
                        start_page=extracted_text_row[4],
                        end_page=extracted_text_row[5],
                        started_at=extracted_text_row[6],
                        ended_at=extracted_text_row[7],
                        errors=extracted_text_row[8]
                    )
                return None
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def insert_extracted_text(self, extracted_text: DocExtractedText):
        """See base class."""

        SQL_INSERT_EXTRACTED_TEXT = f"""INSERT INTO {SCHEMA}.extracted_text
                                        VALUES (%s, %s, %s, %s, %s, %s,
                                                %s, %s, %s, %s);"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(
                    SQL_INSERT_EXTRACTED_TEXT,
                    (extracted_text.id_, extracted_text.content,
                     extracted_text.status, extracted_text.file_type,
                     extracted_text.start_page, extracted_text.end_page,
                     extracted_text.started_at, extracted_text.ended_at,
                     datetime.now(), extracted_text.errors)
                )
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
        SQL_DELETE_ALSO_SOURCE = f"""DELETE FROM {SCHEMA}.source
                                     WHERE source_id = (
                                         SELECT source_id FROM {SCHEMA}.summary
                                         WHERE summary_id = %s
                                     );"""

        # This will not delete the source
        SQL_DELETE_SUMMARY = f"""DELETE FROM {SCHEMA}.summary
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

    def update_extracted_text(self,
                              id_: str,
                              content: str = None,
                              status: ExtractedTextStatus = None,
                              file_type: SupportedFileType = None,
                              start_page: int = None,
                              end_page: int = None,
                              started_at: datetime = None,
                              ended_at: datetime = None,
                              errors: dict = None):
        """See base class."""

        args = OrderedDict({key: value for key, value in locals().items()
                            if value is not None and key not in ('self', 'id_')})

        # Convert dicts to Json
        dicts = [key for key in args if isinstance(args[key], dict)]
        for key in dicts:
            args[key] = Json(args[key])

        keys = list(args.keys())
        values = list(args.values()) + [id_]
        concat = StringIO()
        concat.write(f"UPDATE {SCHEMA}.extracted_text SET ")
        for field in keys[:-1]:
            concat.write(f"{field} = %s, ")
        concat.write(f"{keys[-1]} = %s ")
        concat.write("WHERE id = %s;")

        SQL_UPDATE_EXTRACTED_TEXT = concat.getvalue()

        if self.summary_exists(id_):
            conn = None
            try:
                conn = self._connect()
                with conn.cursor() as cur:
                    cur.execute(SQL_UPDATE_EXTRACTED_TEXT, values)  # values is a list!
                    conn.commit()
                    return self.get_extracted_text(id_)
            except (Exception, psycopg2.DatabaseError) as error:
                self.logger.error(error)
            finally:
                if conn is not None:
                    conn.close()
        else:
            return (None, None)

    def extracted_text_exists(self, id_: str):
        """See base class."""

        SQL_SELECT = f"""SELECT id FROM {SCHEMA}.extracted_text
                         WHERE id = %s;"""

        SQL_UPDATE_LAST_ACCESSED = f"""UPDATE {SCHEMA}.extracted_text
                                       SET last_accessed = %s
                                       WHERE id = %s;"""

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

        SQL = f"""SELECT source_id FROM {SCHEMA}.source
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

    def increment_extracted_text_count(self, id_: str):
        """See base class."""

        SQL = f"""UPDATE {SCHEMA}.extracted_text_doc
                  SET request_count = request_count + 1
                  FROM {SCHEMA}.file_id_extracted_text_id
                  WHERE file_id = %s AND
                  {SCHEMA}.extracted_text_doc.content_id = {SCHEMA}.extracted_text_doc.content_id
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

        SQL_DELETE = f"""DELETE FROM {SCHEMA}.file_id_extracted_text_id
                         WHERE file_id = %s AND cache = FALSE
                         RETURNING content_id;"""

        # Check if the content id has to be cached
        SQL_CACHE = f"""SELECT cache FROM {SCHEMA}.file_id_extracted_text_id
                        WHERE file_id = %s;"""

        # Because of ON DELETE CASCADE, this will delete both the
        # source and the summary
        SQL_DELETE_EXTRACTED_TEXT = f"""DELETE FROM {SCHEMA}.extracted_text_doc
                                        WHERE content_id = %s;"""

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_DELETE, (id_,))
                content_id = cur.fetchone()
                if content_id is not None:
                    if id_ == content_id[0]:  # content_id is a tuple
                        # We have already checked that cache was False
                        cur.execute(SQL_DELETE_EXTRACTED_TEXT, content_id)
                    else:
                        cur.execute(SQL_CACHE, content_id)
                        cache = cur.fetchone()
                        if cache is not None and not cache[0]:
                            cur.execute(SQL_DELETE_EXTRACTED_TEXT, content_id)
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(error)
        finally:
            if conn is not None:
                conn.close()

    def cleanup_cache(self, older_than_seconds: int):
        """See base class."""

        SQL_CLEANUP = f"""
                 DELETE FROM {SCHEMA}.extracted_text
                 WHERE last_accessed < NOW() - (%s::TEXT || ' seconds')::INTERVAL;
                 """

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(SQL_CLEANUP, (older_than_seconds,))
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
            :obj:`str`: The unique, SHA-256 encrypted key.
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
