import numpy as np
import pytest
from scipy.misc import electrocardiogram

from pyecg import ECGRecord, ECGTime, ECGSignal


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_length(fs, samples):
    record = ECGRecord("record_100", time=ECGTime.from_fs_samples(fs, samples))
    assert len(record) == samples


@pytest.mark.parametrize("time", [[1, 2, 3, 4]])
def test_bad_time(time):
    with pytest.raises(TypeError):
        ECGRecord("record_100", time=time)


def test_inconsistent_signal_len():
    record = ECGRecord("record_100", time=ECGTime.from_fs_samples(360, 10))
    with pytest.raises(ValueError):
        record._add_signal(ECGSignal(electrocardiogram(), "MLII"))


def test_inconsistent_signal_type():
    record = ECGRecord("record_100", time=ECGTime.from_fs_samples(360, 10))
    with pytest.raises(TypeError):
        record._add_signal(electrocardiogram())


@pytest.mark.parametrize("time, signal", [(np.arange(100), np.random.rand(100)),
                                          (np.arange(100), np.random.rand(100, 3, 4))])
def test_from_numpy_array_bad_signal_shape(time, signal):
    with pytest.raises(ValueError):
        ECGRecord.from_np_array("record_100", time, signal, ["II"])


@pytest.mark.parametrize("time, signal", [(np.arange(100), np.random.rand(3, 100))])
def test_from_numpy_array(time, signal):
    record = ECGRecord.from_np_array("record_100", time, signal, ["I", "II", "III"])
    assert len(record) == len(time)


@pytest.mark.parametrize("time, signal", [(np.arange(100), np.random.rand(3, 100))])
def test_from_numpy_array_inconsistent_signal_name(time, signal):
    with pytest.raises(ValueError):
        ECGRecord.from_np_array("record_100", time, signal, ["II"])


@pytest.mark.parametrize("time, signal", [(np.arange(100), np.random.rand(3, 100))])
def test_repr(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    assert record.__repr__() == f"Record 100: ['I', 'II', 'III']"


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_get_lead(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    assert np.array_equal(record.get_lead("I")[:], [1, 2, 3, 4, 5, 6])
    assert np.array_equal(record.get_lead("II")[:], [5, 6, 7, 8, 9, 10])
    assert np.array_equal(record.get_lead("III")[:], [10, 20, 30, 40, 50, 60])


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_get_lead_notfound(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    assert record.get_lead("MLII") is None


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_slicing(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_sliced = record[0:1]
    assert np.array_equal(record_sliced.time.time, time[0:1])
    for i, s in enumerate(signal):
        print(record_sliced._signals[i].signal)
        assert record_sliced._signals[i] == s[0:1]


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_slicing_not_touching_original(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_sliced = record[0:1]
    assert not np.array_equal(record.time.time, time[0:1])
    for i, s in enumerate(signal):
        assert not record._signals[i] == s[0:1].tolist()
    record_sliced = record[1]
    assert not np.array_equal(record.time.time, time[1])
    for i, s in enumerate(signal):
        assert not record._signals[i] == [s[1]]


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_slicing_single_element(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_sliced = record[0]
    assert np.array_equal(record_sliced.time.time, [time[0]])
    for i, s in enumerate(signal):
        assert record_sliced._signals[i] == [s[0]]
