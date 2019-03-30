import numpy as np
import pytest

from pyecg import ECGTime


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_len(fs, samples):
    time = ECGTime.from_fs_samples(fs, samples)
    assert len(time) == samples


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_from_fs_samples(fs, samples):
    time = ECGTime.from_fs_samples(fs, samples)
    time_expected = (1 / fs) * np.arange(0, samples)
    assert np.array_equal(time.time, time_expected)


@pytest.mark.parametrize("time_stamps", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_slicing(time_stamps):
    time = ECGTime.from_timestamps(time_stamps)
    assert np.array_equal(time[0:1].time, time_stamps[0:1])


@pytest.mark.parametrize("time_stamps", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_slicing_single_element(time_stamps):
    time = ECGTime.from_timestamps(time_stamps)
    assert np.array_equal(time[0].time, [time_stamps[0]])


@pytest.mark.parametrize("time_stamps", [[0, 1, 2, 3], [1, 2, 3, 4]])
def test_from_time_stamp(time_stamps):
    time = ECGTime.from_timestamps(time_stamps)
    assert np.array_equal(time.time, time_stamps)


@pytest.mark.parametrize("time_stamps", [[2, 1, 3, 3], [5, 2, 3, 4]])
def test_from_time_stamp_not_monotonic(time_stamps):
    with pytest.raises(ValueError):
        ECGTime.from_timestamps(time_stamps)


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_length(fs, samples):
    time = ECGTime.from_fs_samples(fs, samples)
    assert len(time.time) == samples
