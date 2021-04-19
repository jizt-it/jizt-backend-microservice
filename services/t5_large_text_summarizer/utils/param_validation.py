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

__version__ = '0.1.0'

from default_params import DefaultParam
from typing import Union, Any, Tuple
from warning_messages import WarningMessage

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


def validate_params(params: dict) -> Tuple[dict, dict]:
    """Validate T5 model parameters.

    If a parameter contains an invalid value, it will be replaced by a default value.
    If a parameter does not exist, it is removed.

    Args:
        params (:obj:`dict`):
            The parameters to validate.

    Returns:
        :obj:`Tuple[dict, dict]: A tuple containing two dictionaries, the first
        with the correct parameters, and the second with the invalid, discarded
        parameters.
    """

    supported_params = [param.name.lower() for param in DefaultParam]
    invalid_params = {}

    for key in params:
        if key not in supported_params:
            invalid_params[key] = params[key]
        else:
            reqs = PARAMS_VALIDATION_REQUISITES[key].copy()
            type_ = reqs.pop('type_')

            # validate ints
            if (type_ is int
                    and not _validate_int(value=params[key], **reqs)
                    # validate floats
                    or type_ is float
                    and not _validate_float(value=params[key], **reqs)
                    # validate bools
                    or type_ is bool
                    and not _validate_bool(params[key])):
                invalid_params[key] = params[key]

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
    elif (min_ in params and max_ not in params and
            params[min_] >= DefaultParam.RELATIVE_MAX_LENGTH.value):
        invalid_params[min_] = params[min_]
    elif (min_ not in params and max_ in params and
            params[max_] <= DefaultParam.RELATIVE_MIN_LENGTH.value):
        invalid_params[max_] = params[max_]

    _ = [params.pop(invalid) for invalid in invalid_params]  # remove invalid params
    for default_param in supported_params:
        if default_param not in params:  # add not included params
            params[default_param] = \
                DefaultParam[default_param.upper()].value

    return params, invalid_params


def _validate_int(
    value: Any,
    lower_bound: int = None,
    upper_bound: int = None
) -> bool:
    """Validate if a value is an :obj:`int`.

    The number can be constrained by a lower and/or an upper bound (inclusive).

    Args:
        value (:obj:`Any`):
            The value to check.
        lower_bound (:obj:`int`, `optional`, defaults to :obj:`None`):
            The lower bound of the constraint. Values smaller than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).
        upper_bound (:obj:`int`, `optional`, defaults to :obj:`None`):
            The upper bound of the constraint. Values greater than this number are
            invalid. If set to :obj:`None`, the bound is not checked (i.e., the value
            is unbounded).

    Returns:
        :obj:`bool`: :obj:`True` if :obj:`value` is valid (i.e., it's an :obj:`int`)
        between :obj:`lower_bound` and :obj:`upper_bound`, inclusive), :obj:`False`
        otherwise.
    """

    return type(value) is int and _validate_bounds(value, lower_bound, upper_bound)


def _validate_float(
    value: Any,
    lower_bound: float = None,
    upper_bound: float = None
) -> bool:
    """Validate if a value is an :obj:`float`.

    The number can be constrained by a lower and/or an upper bound (inclusive).

    Args:
        value (:obj:`Any`):
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
        :obj:`bool`: :obj:`True` if :obj:`value` is valid (i.e., it's an :obj:`float`)
        between :obj:`lower_bound` and :obj:`upper_bound`, inclusive), :obj:`False`
        otherwise.
    """

    return type(value) is float and _validate_bounds(value, lower_bound, upper_bound)


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


def _validate_bool(value: Any) -> bool:
    """Determine whether a value is a :obj:`bool` or not.

    Args:
        value (:obj:`Any`):
            The value to check.

    Returns:
        :obj:`bool`: :obj:`True` if :obj:`value` is a :obj:`bool`, :obj:`False`
        otherwise.
    """

    return type(value) is bool
