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

"""Model parameter validation."""

__version__ = '0.1.1'

from default_params import DefaultParam
from warning_messages import ValidationWarning, WarningMessage
from typing import Union, Any, Tuple, List

# Requirements the different params must comply with
# The key 'type_' is always required; 'lower_bound' and 'upper_bound' are optional.
PARAMS_VALIDATION_REQUISITES = {
    DefaultParam.RELATIVE_MAX_LENGTH.name.lower(): {'type_': float,
                                                     'lower_bound': 0.1,
                                                     'upper_bound': 1.0},
    DefaultParam.RELATIVE_MIN_LENGTH.name.lower(): {'type_': float,
                                                     'lower_bound': 0.1,
                                                     'upper_bound': 1.0},
    DefaultParam.DO_SAMPLE.name.lower(): {'type_': bool},
    DefaultParam.EARLY_STOPPING.name.lower(): {'type_': (bool)},
    DefaultParam.NUM_BEAMS.name.lower(): {'type_': int,
                                          'lower_bound': 0},
    DefaultParam.TEMPERATURE.name.lower(): {'type_': float},
    DefaultParam.TOP_K.name.lower(): {'type_': int},
    DefaultParam.TOP_P.name.lower(): {'type_': float},
    DefaultParam.REPETITION_PENALTY.name.lower(): {'type_': float},
    DefaultParam.LENGTH_PENALTY.name.lower(): {'type_': float},
    DefaultParam.NO_REPEAT_NGRAM_SIZE.name.lower(): {'type_': int,
                                                     'lower_bound': 0}
}


# Used to generate the warning messages
WARNING = ValidationWarning()


def validate_params(params: dict) -> Tuple[dict, dict]:
    """Validate T5 model parameters.

    If a parameter contains an invalid value, it will be replaced by a default value.
    If a parameter does not exist, it is removed.

    Args:
        params (:obj:`dict`):
            The parameters to validate.

    Returns:
        :obj:`Tuple[dict, dict, dict]: A tuple containing three dictionaries; the
        first with the correct parameters; the second with the invalid, discarded
        parameters); the third with the warning messages.
    """

    supported_params = [param.name.lower() for param in DefaultParam]
    invalid_params = {}
    warning_messages = {}

    for key in params:
        if key not in supported_params:
            invalid_params[key] = params[key]
            warning_messages[key] = [WARNING(WarningMessage.UNSUPPORTED)]
        else:
            reqs = PARAMS_VALIDATION_REQUISITES[key].copy()
            type_ = reqs.pop('type_')

            is_valid, warnings = _validate_value(params[key], type_, **reqs)

            if not is_valid:
                invalid_params[key] = params[key]
            if warnings:
                warning_messages[key] = warnings

    # Ensure that the min length is smaller than the max length
    min_ = DefaultParam.RELATIVE_MIN_LENGTH.name.lower()
    max_ = DefaultParam.RELATIVE_MAX_LENGTH.name.lower()
    # If any of them is invalid, we first add the default value
    if min_ in invalid_params:
        params[min_] = DefaultParam[min_.upper()].value
    if max_ in invalid_params:
        params[max_] = DefaultParam[max_.upper()].value
    # Checks
    if (min_ in params and max_ in params and params[min_] >= params[max_]):
        invalid_params[min_] = params[min_]
        invalid_params[max_] = params[max_]
        if min_ not in warning_messages:
            warning_messages[min_] = [WARNING(WarningMessage.MIN_LENGTH)]
        if max_ not in warning_messages:
            warning_messages[max_] = [WARNING(WarningMessage.MAX_LENGTH)]
    elif (min_ in params and max_ not in params and
            params[min_] >= DefaultParam.RELATIVE_MAX_LENGTH.value):
        invalid_params[min_] = params[min_]
        if min_ not in warning_messages:
            warning_messages[min_] = [WARNING(WarningMessage.MIN_LENGTH_DEFAULT)]
    elif (min_ not in params and max_ in params and
            params[max_] <= DefaultParam.RELATIVE_MIN_LENGTH.value):
        invalid_params[max_] = params[max_]
        if max_ not in warning_messages:
            warning_messages[max_] = [WARNING(WarningMessage.MAX_LENGTH_DEFAULT)]

    _ = [params.pop(invalid) for invalid in invalid_params]  # remove invalid params
    for default_param in supported_params:
        if default_param not in params:  # add not included params
            params[default_param] = \
                DefaultParam[default_param.upper()].value

    return params, invalid_params, warning_messages


def _validate_value(
    value: Any,
    type_: Any,
    lower_bound: int = None,
    upper_bound: int = None
) -> Tuple[bool, List]:
    """Validate if a value is an :obj:`int`.

    The number can be constrained by a lower and/or an upper bound (inclusive).

    Args:
        value (:obj:`Any`):
            The value to check.
        type (:obj:`Any`):
            The type the value must be.
        lower_bound (:obj:`int`, `optional`, defaults to :obj:`None`):
            The lower bound of the constraint. Values smaller than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).
        upper_bound (:obj:`int`, `optional`, defaults to :obj:`None`):
            The upper bound of the constraint. Values greater than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).

    Returns:
        :obj:`Tuple[bool, List]`: A tuple containing a :obj:`bool` indicating whether
        the value is valid, and a :obj:`List` with warning messages (if there are not
        any warning messages, the list will be empty).
    """

    warning_messages = []

    # Don't confuse type_, i.e. the type the value must have,
    # with type(value), i.e. the actual type of the value.
    if type_ is int:
        if type(value) is not int:
            warning_messages.append(WARNING(WarningMessage.INT))
        elif not _validate_bounds(value, lower_bound, upper_bound):
            warning_messages.append(WARNING(WarningMessage.LOWER_BOUNDED,
                                            lower_bound=lower_bound))
    elif type_ is float:
        if type(value) is not float:
            warning_messages.append(WARNING(WarningMessage.FLOAT))
        elif not _validate_bounds(value, lower_bound, upper_bound):
            warning_messages.append(WARNING(WarningMessage.BOUNDED,
                                    lower_bound=lower_bound,
                                    upper_bound=upper_bound))
    elif type_ is bool and type(value) is not bool:
            warning_messages.append(WARNING(WarningMessage.BOOL))

    return len(warning_messages) == 0, warning_messages


def _validate_bounds(
    value: Union[int, float],
    lower_bound: Union[int, float] = None,
    upper_bound: Union[int, float] = None,
) -> bool:
    """Check whether a number is contained within the defined bounds.
    Args:
        value (:obj:`int` or :obj:`float`):
            The value to check.
        lower_bound (:obj:`float`, `optional`, defaults to :obj:`None`):
            The lower bound of the constraint. Values smaller than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).
        upper_bound (:obj:`float`, `optional`, defaults to :obj:`None`):
            The upper bound of the constraint. Values greater than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).
    Returns:
        :obj:`bool`: :obj:`True` if :obj:`value` is contained within the bounds
        :obj:`False` otherwise.
    """

    return ((lower_bound is None or lower_bound <= value)
             and (upper_bound is None or upper_bound >= value))
