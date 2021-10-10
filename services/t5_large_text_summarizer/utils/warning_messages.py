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

"""Warning messages."""

__version__ = '0.1.0'

import re
from enum import Enum
from default_params import DefaultParam
from typing import Union


class WarningMessage(Enum):
    """Warning messages for incorrect parameters."""

    # int value
    INT = "The specified value must be an int. Using default value instead."
    # float value
    FLOAT = "The specified value must be a float. Using default value instead."
    # numeric vaule with a lower bound (inclusive)
    LOWER_BOUNDED = ("The specified value must be greater or equal to "
                     "{lower_bound}. Using default value instead.")
    # numeric vaule with lower and upper bounds (inclusive)
    BOUNDED = ("The specified value must be in the range [{lower_bound}, "
               "{upper_bound}]. Using default values instead.")
    # bool value
    BOOL = "The specified value must be a bool. Using default value instead."
    # unsupported parameter
    UNSUPPORTED = "Parameter not supported. It will be ignored."
    # relative_max_length
    MAX_LENGTH = ("This parameter must be greater than 'relative_min_length'. Using "
                  "default value instead.")
    # relative_min_length
    MIN_LENGTH = ("This parameter must be smaller than 'relative_max_length'. Using "
                  "default value instead.")
    # default relative_max_length
    MAX_LENGTH_DEFAULT = (f"This parameter must be greater than the default "
                          f"'relative_min_length' "
                          f"({DefaultParam.RELATIVE_MIN_LENGTH.value}). Using "
                          f"default value instead.")
    # default relative_min_length
    MIN_LENGTH_DEFAULT = (f"This parameter must be smaller than the default "
                          f"'relative_max_length' "
                          f"({DefaultParam.RELATIVE_MAX_LENGTH.value}). Using "
                          f"default value instead.")


class ValidationWarning:
    """Validation warnings."""

    def __call__(
        self,
        warning_message: WarningMessage,
        **kwargs
    ) -> str:
        """Get a validation warning message.

        Example of use:

        ::

            validation_warning = ValidationWarning()
            warning_str = validation_warning(
                WarningMessage.LOWER_BOUNDED,
                lower_bound=0
            )
            # "The specified value must be greater or equal to 0. "
            # "Using default value instead."

        Args:
            warning_message(:obj:`WarningMessage`):
                The warning message to get.
            **kwargs:
                Additional info, the bounds of the parameter in case of it being a
                numerical value.

        Returns:
            :obj:`str`: The warning message.
        """

        return self._build_message(warning_message, **kwargs)

    @classmethod
    def _build_message(
        cls,
        warning_message: WarningMessage,
        lower_bound: Union[int, float] = None,
        upper_bound: Union[int, float] = None,
    ) -> str:
        """Build the warning message.

        Args:
            warning_message (:obj:`WarningMessage`):
                The warning message to build.
            lower_bound (:obj:`int` or :obj:`float`, `optional`, defaults to :obj:`None`):
                The lower bound of the parameter.
            upper_bound (:obj:`int` or :obj:`float`, `optional`, defaults to :obj:`None`):
                The upper bound of the parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        message = warning_message.value

        if lower_bound is not None:
            message = re.sub(r'{lower_bound}', str(lower_bound), message)

        if lower_bound is not None:
            message = re.sub(r'{upper_bound}', str(upper_bound), message)

        return message
