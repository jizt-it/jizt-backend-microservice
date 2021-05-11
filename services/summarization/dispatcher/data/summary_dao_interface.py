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

"""Summary Data Access Object (DAO) Interface."""

__version__ = '0.1.3'

from datetime import datetime
from schemas import Summary
from summary_status import SummaryStatus
from supported_models import SupportedModel
from supported_languages import SupportedLanguage
from warning_messages import WarningMessage


class SummaryDAOInterface:
    """DAO Interface for access to :obj:`Summary` objects."""

    def get_summary(self, id_: str):
        """Retrieve a summary from the database.

        Args:
            id_ (:obj:`str`):
                The summary id.

        Returns:
            :obj:tuple(:obj:`Summary`, :obj:`dict`): A tuple with the summary with the
            specified id and its associated warnings (if there are no warnings then
            they will be :obj:`None`) or a tuple containing two :obj:`None`s if there
            is not any summary with the specified id.
        """

    def insert_summary(self, summary: Summary, cache: bool, warnings: dict):
        """Insert a new summary to the database.

        Args:
            summary (:obj:`Summary`):
                The summary to be saved.
            cache (:obj:`bool`):
                Whether the summary must be cached, i.e., permanently stored in the
                database.
            warnings (:obj:`dict`):
                The warnings derived from the user request.
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
        """Start caching a summary.

        If a user requests their summary not to be cached, the summary's cache value
        will be set to False. However, if later on another user requests the same
        exact summary to be cached, the cache value will be set to True.

        The oppsite is not possible, i.e., if a user requests their summary to be
        cached, and then another user requests the same exact summary not to be
        cached, the cache value will still be True, since we need to keep the summary
        for the user that did request the caching.

        Args:
            id_ (:obj:`str`):
                The raw id (not to be confused with the preprocessed id).
        """

    def summary_exists(self, id_: str):
        """Check whether a summary already exists in the DB.

        Args:
            id_ (:obj:`str`):
                The summary id.

        Returns:
            :obj:`bool`: Whether the summary exists or not.
        """

    def source_exists(self, source: str):
        """Check whether a source (original text) already exists in the DB.

        Args:
            source (:obj:`str`):
                The source.

        Returns:
            :obj:`bool`: Whether the source exists or not.
        """

    def increment_summary_count(self, id_: str):
        """Increments the summary count, i.e., the times a summary has been requested.

        Args:
            id_ (:obj:`str`):
                The summary id.

        Returns:
            :obj:`int`: the summary count.
        """

    def delete_if_not_cache(self, id_: str):
        """Check if a summary should be cached and if not delete it.

        When requesting a summary, clients can request not to cache their summary.
        This is useful when the user's text contains sensitive data, or when they
        simply do not want their text to be permanently stored in the database.

        Args:
            id_ (:obj:`str`):
                The raw id (not to be confused with the preprocessed id).
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
