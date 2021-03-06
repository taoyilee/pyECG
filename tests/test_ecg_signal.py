import numpy as np
import pytest
from scipy.misc import electrocardiogram

from pyecg import Signal


@pytest.mark.parametrize("signal", ["a"])
def test_bad_type(signal):
    with pytest.raises(TypeError):
        Signal(signal, "II")


def test_length():
    signal = Signal(electrocardiogram(), "II")
    assert len(signal) == 5 * 60 * 360


@pytest.mark.parametrize("lead_name", ["MLII", "I", "II"])
def test_repr(lead_name):
    signal = Signal(electrocardiogram(), lead_name)
    assert signal.__repr__() == f"Lead {lead_name}"


@pytest.mark.parametrize("signal", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_equality(signal):
    ecg_signal = Signal(signal, "MLII")
    assert ecg_signal == signal
    assert np.array_equal(np.array(ecg_signal), np.array(signal))


@pytest.mark.parametrize("signal", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_slicing(signal):
    ecg_signal = Signal(signal, "MLII")
    assert ecg_signal[0:1] == signal[0:1]


@pytest.mark.parametrize("signal", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_slicing_single_element(signal):
    ecg_signal = Signal(signal, "MLII")
    assert ecg_signal[0] == signal[0]


@pytest.mark.parametrize("signal", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_iter(signal):
    ecg_signal = Signal(signal, "MLII")
    for e, i in zip(ecg_signal, signal):
        assert e == i
    for i, e in enumerate(ecg_signal):
        assert e == signal[i]
