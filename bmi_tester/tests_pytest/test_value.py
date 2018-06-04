from __future__ import print_function
import warnings

from distutils.version import StrictVersion
import numpy as np
import pytest

from .utils import strictly_input_names
from . import BMI_VERSION_STRING


BMI_VERSION = StrictVersion(BMI_VERSION_STRING)

BAD_VALUE = {
    'f': np.nan,
    'i': -999,
    'u': 0,
}

def empty_var_buffer(bmi, var_name):
    gid = bmi.get_var_grid(var_name)
    if BMI_VERSION > '1.0':
        loc = bmi.get_var_location(var_name)
    else:
        warnings.warn('get_var_location not implemented (assuming nodes)', FutureWarning)
        loc = 'node'

    if loc == 'node':
        size = bmi.get_grid_size(gid)
    elif loc == 'edge':
        size = bmi.get_grid_number_of_edges(gid)
    else:
        size = 0

    dtype = np.dtype(bmi.get_var_type(var_name))
    values = np.empty(size, dtype=dtype)

    return values


def test_get_var_location(new_bmi, var_name):
    """Test for get_var_location"""
    if BMI_VERSION < '1.1':
        pytest.skip('testing BMIv{ver}: get_var_location was introduced in BMIv1.1'.format(ver=BMI_VERSION))

    assert hasattr(new_bmi, 'get_var_location')

    loc = new_bmi.get_var_location(var_name)

    assert isinstance(loc, str)
    assert loc in ('node', 'edge', 'face')


def test_get_input_values(new_bmi, in_var_name):
    """Input values are numpy arrays."""
    gid = new_bmi.get_var_grid(in_var_name)

    values = empty_var_buffer(new_bmi, in_var_name)
    values.fill(BAD_VALUE[values.dtype.kind])
    rtn = new_bmi.set_value(in_var_name, values)
    if rtn is None:
        warnings.warn('set_value should return the buffer')
    else:
        assert values is rtn
    if np.isnan(BAD_VALUE[values.dtype.kind]):
        assert np.all(np.isnan(values))
    else:
        assert np.all(values == BAD_VALUE[values.dtype.kind])


def test_get_output_values(new_bmi, out_var_name):
    """Output values are numpy arrays."""
    gid = new_bmi.get_var_grid(out_var_name)

    values = empty_var_buffer(new_bmi, out_var_name)
    values.fill(BAD_VALUE[values.dtype.kind])
    initial = values.copy()
    try:
        rtn = new_bmi.get_value(out_var_name, values)
    except TypeError:
        warnings.warn('get_value should take two arguments')
        rtn = new_bmi.get_value(out_var_name)
        values[:] = rtn
    else:
        assert values is rtn

    assert np.any(values != initial)