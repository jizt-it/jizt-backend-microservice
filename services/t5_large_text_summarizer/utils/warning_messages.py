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
from default_params import DefaultParam


class WarningMessage(Enum):
    """Warning messages for incorrect parameters."""

    # int value
    INT = "The parameter '{param}' must be an int. Using default value instead."
    # int with a lower bound (inclusive)
    LOWER_BOUNDED_INT = ("The parameter '{param}' must be an int >= {lower_bound}. "
                         "Using default value instead.")
    # float value
    FLOAT = "The parameter '{param}' must be a float. Using default value instead."
    # float with lower and upper bounds (inclusive)
    BOUNDED_FLOAT = ("The parameter '{param}' must be a float in the range "
                    "[{lower_bound}, {upper_bound}]. Using default values instead.")
    # bool value
    BOOL = ("The parameter '{param}' must be a bool value. "
            "Using default value instead.")


class ValidationWarning:
    """Validation warnings."""

    def __call__(
        self,
        warning_message: WarningMessage,
        param: DefaultParam,
        **kwargs
    ) -> str:
        """Get a validation warning message.

        Example of use:

        ::

            validation_warning = ValidationWarning()
            warning_str = validation_warning(
                WarningMessage.LOWER_BOUNDED_INT,
                DefaultParam.NUM_BEAMS,
                lower_bound=0
            )
            # "The parameter 'num_beams' must be an int >= 0. "
            # "Using default values instead."

        Args:
            warning_message(:obj:`WarningMessage`):
                The warning message to get.
            param (:obj:`DefaultParam`):
                The name of invalid parameter.
            **kwargs:
                Additional info, the bounds of the parameter in case of it being a
                numerical value.

        Returns:
            :obj:`str`: The warning message.
        """

        if warning_message == WarningMessage.INT:
            return self._int(param, **kwargs)
        elif warning_message == WarningMessage.LOWER_BOUNDED_INT:
            return self._lower_bounded_int(param, **kwargs)
        elif warning_message == WarningMessage.FLOAT:
            return self._float(param, **kwargs)
        elif warning_message == WarningMessage.BOUNDED_FLOAT:
            return self._bounded_float(param, **kwargs) 
        elif warning_message == WarningMessage.BOOL:
            return self._bool(param, **kwargs)
        else:
            raise NameError(f'${warning_message} is not defined')

    @classmethod
    def _int(cls, param: DefaultParam) -> str:
        """Get a warning message for an unbounded :obj:`int`.

        Args:
            param (:obj:`DefaultParam`):
                The name of invalid parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        return re.sub(r'{param}', param.name.lower(), WarningMessage.INT.value)

    @classmethod
    def _lower_bounded_int(cls, param: DefaultParam, lower_bound: int) -> str:
        """Get a warning message for an :obj:`int` with a lower bound.

        Args:
            param (:obj:`DefaultParam`):
                The name of invalid parameter.
            lower_bound (:obj:`int`):
                The lower bound of the parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        return re.sub(
            r'{param}',
            param.name.lower(),
            re.sub(
                r'{lower_bound}',
                str(lower_bound),
                WarningMessage.LOWER_BOUNDED_INT.value
            )
        )

    @classmethod
    def _float(cls, param: DefaultParam) -> str:
        """Get a warning message for an unbounded :obj:`float`.

        Args:
            param (:obj:`DefaultParam`):
                The name of invalid parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        return re.sub(r'{param}', param.name.lower(), WarningMessage.FLOAT.value)

    @classmethod
    def _bounded_float(
        cls,
        param: DefaultParam,
        lower_bound: float,
        upper_bound: float
    ) -> str:
        """Get a warning message for a :obj:`float` with lower and upper bounds.

        Args:
            param (:obj:`DefaultParam`):
                The name of invalid parameter.
            lower_bound (:obj:`int`):
                The lower bound of the parameter.
            upper_bound (:obj:`int`):
                The upper bound of the parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        return re.sub(
            r'{param}',
            param.name.lower(),
            re.sub(
                r'{lower_bound}',
                str(lower_bound),
                re.sub(
                    r'{upper_bound}',
                    str(upper_bound),
                    WarningMessage.BOUNDED_FLOAT.value
                )
            )
        )

    @classmethod
    def _bool(cls, param: DefaultParam) -> str:
        """Get a warning message for a :obj:`bool`.

        Args:
            param (:obj:`DefaultParam`):
                The name of invalid parameter.

        Returns:
            :obj:`str`: The warning message.
        """

        return re.sub(r'{param}', param.name.lower(), WarningMessage.BOOL.value)
