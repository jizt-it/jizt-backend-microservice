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

"""Warning messages."""

__version__ = '0.1.0'

import re
from enum import Enum
from supported_models import SupportedModel
from supported_languages import SupportedLanguage
from typing import Union


class WarningMessage(Enum):
    """Warning messages for incorrect attributes."""

    # Model not supported
    UNSUPPORTED_MODEL = (f"The specified model is not supported. "
                         f"Defaulting to '{SupportedModel.T5_LARGE.value}'.")

    # Language not supported
    UNSUPPORTED_LANGUAGE = (f"The specified language is not supported. "
                            f"Defaulting to '{SupportedLanguage.ENGLISH.value}'.")
