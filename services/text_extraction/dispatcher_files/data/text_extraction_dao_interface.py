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

# TODO: everything

"""TextExtraction Data Access Object (DAO) Interface."""

__version__ = '0.1.3'

from datetime import datetime
from schemas import ExtractedTextDoc
from extracted_text_status import ExtractedTextStatus
from supported_file_types import SupportedFileType


class TextExtractionDAOInterface:
    """DAO Interface for access to :obj:`ExtractedText` objects."""

    def get_extracted_text(self, id_: str):
        """Retrieve an extracted text from the database.

        Args:
            id_ (:obj:`str`):
                The extracted text id.

        Returns:
            Union[:obj:`ExtractedText`, :obj:`None`]: the extracted text or
            :obj:`None` if it doesn't exist in the database.
        """

    def insert_extracted_text(self, extracted_text: ExtractedTextDoc,
                              file_extension: SupportedFileType, cache: bool):
        """Insert a new extracte text to the database.

        Args:
            extracted_text (:obj:`ExtractedTextDoc`):
                The extracted text to be saved.
            file_extension (:obj:`SupportedFileType`):
                The file type of the document, e.g., ``SuportedFileType.PDF``.
            cache (:obj:`bool`):
                Whether the extracted text must be cached, i.e., permanently
                stored in the database.
        """

    def delete_summary(self, id_: str, delete_source: bool):
        """Delete a summary.

        Args:
            id_ (:obj:`str`):
                The summary id.
            delete_source (:obj:`bool`):
                Whether to also delete the source.
        """

    def update_summary(self,
                       id_: str,
                       summary: str,  # output
                       params: dict,
                       status: str,
                       started_at: datetime,
                       ended_at: datetime,
                       warnings: dict):
        """Update an existing summary.

        Args:
            See :py:class:`data.schemas.Summary`.

        Returns:
            :obj:tuple(:obj:`Summary`, :obj:`dict`): A tuple with the updated summary
            and its associated warnings (if there are no warnings then they will be
            :obj:`None`) or a tuple containing two :obj:`None`s if there
            is not any summary with the specified id.
        """

    def update_source(self,
                      old_source: str,
                      new_source: str,
                      old_summary_id: str,
                      new_summary_id: str):
        """Update a source text.

        Args:
            old_source (:obj:`str`):
                The previous source.
            new_source (:obj:`str`):
                The new source.
            old_summary_id (:obj:`str`):
                The old summary id.
            new_summary_id (:obj:`str`):
                The new summary id. As the source changes, so does the summary id.
                That is why this and the previous parameter must be provided.
        """

    def update_preprocessed_id(self,
                               raw_id: str,
                               new_preprocessed_id: str):
        """Update binding between a raw id and the preprocessed id.

        Aditionally to udating the binding, the summary corresponding to the old
        preprocessed id is deleted.

        Args:
            raw_id (:obj:`str`):
                The id of the summary before its source has been preprocessed.
            preprocessed_id (:obj:`str`):
                The id of the summary once its source has been preprocessed.
        """

    def update_cache_true(self, id_: str):
        """Start caching an extracted text.

        If a user requests the extracted text from their files not to be cached,
        the extracted text's cache value will be set to :obj:`False`. However,
        if later on another user requests the same exact extracted text to be
        cached, the cache value will be set to :obj:`True`.

        The oppsite is not possible, i.e., if a user requests the extracted
        text to be cached, and then another user requests the same exact summary
        not to be cached, the cache value will still be :obj:`True`, since we
        need to keep the extracted text for the user that did request the
        caching.

        Args:
            id_ (:obj:`str`):
                The file id (not to be confused with the content id).
        """

    def extracted_text_exists(self, id_: str):
        """Check whether an extracted text already exists in the DB.

        Args:
            id_ (:obj:`str`):
                The extracted text id.

        Returns:
            :obj:`bool`: Whether the extracted text exists or not.
        """

    def source_exists(self, source: str):
        """Check whether a source (original text) already exists in the DB.

        Args:
            source (:obj:`str`):
                The source.

        Returns:
            :obj:`bool`: Whether the source exists or not.
        """

    def increment_extracted_text_count(self, id_: str):
        """Increments the extracted text count.

        This count represent the number of times the same text has been
        extracted from different files.

        Args:
            id_ (:obj:`str`):
                The content id.

        Returns:
            :obj:`int`: the extracted text count.
        """

    def delete_if_not_cache(self, id_: str):
        """Check if an extracted text should be cached and if not delete it.

        When requesting an extracted text, clients can request not to cache it.
        This is useful when the user's text contains sensitive data, or when
        they simply do not want their text to be permanently stored in the
        database.

        Args:
            id_ (:obj:`str`):
                The file id (not to be confused with the content id).
        """

    def cleanup_cache(self, older_than_seconds: int):
        """Delete summaries with cache set to ``False`` with a certain age in seconds.

        Args:
            older_than_seconds (:obj:`int`):
                Maximum age in seconds of that completed summaries with cache set to
                ``False`` can have not to be deleted, i.e., completed summaries with
                cache set to ``False``and requested before ``older_than_seconds``
                seconds will be deleted when calling this method.
        """
