import numpy as np
import pytest

from pyecg import ECGRecord, Time
from pyecg.annotations import ECGAnnotation, ECGAnnotationSample


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_duration(fs, samples):
    record = ECGRecord("record_100", time=Time.from_fs_samples(fs, samples))
    assert record.duration == (samples - 1) / fs


@pytest.mark.parametrize("fs, samples", [(360, 10), (250, 20), (360.0, 30)])
def test_length(fs, samples):
    record = ECGRecord("record_100", time=Time.from_fs_samples(fs, samples))
    assert len(record) == samples


@pytest.mark.parametrize("time", [[1, 2, 3, 4]])
def test_bad_time(time):
    with pytest.raises(TypeError):
        ECGRecord("record_100", time=time)


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
    assert record_sliced.time == time[0:1]
    for i, s in enumerate(signal):
        assert record_sliced.signals[i] == s[0:1]


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_slicing_not_touching_original(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_sliced = record[0:1]
    assert len(record) == 6
    record_sliced = record[0:2]
    assert len(record) == 6
    record_sliced = record[1:3]
    assert len(record) == 6
    record_sliced = record[1]
    assert len(record) == 6


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_slicing_single_element(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_sliced = record[0]
    assert record_sliced.time == time[0]
    for i, s in enumerate(signal):
        assert record_sliced.signals[i] == s[0]


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_p_signal(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    assert np.array_equal(record.p_signal, signal)


@pytest.mark.parametrize("time, signal", [([0, 1, 2, 3, 4, 5], np.array([[1, 2, 3, 4, 5, 6],
                                                                         [5, 6, 7, 8, 9, 10],
                                                                         [10, 20, 30, 40, 50, 60]]))])
def test_p_signal_shape(time, signal):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    assert np.array_equal(record.p_signal.shape, (3, 6))


@pytest.mark.parametrize("time, signal,slice_", [([0, 1, 2, 3, 4, 5],
                                                  np.array([[1, 2, 3, 4, 5, 6],
                                                            [5, 6, 7, 8, 9, 10],
                                                            [10, 20, 30, 40, 50, 60]]),
                                                  slice(0, 4)),
                                                 ([0, 1, 2, 3, 4, 5],
                                                  np.array([[1, 2, 3, 4, 5, 6],
                                                            [5, 6, 7, 8, 9, 10],
                                                            [10, 20, 30, 40, 50, 60]]),
                                                  slice(1, 4)),
                                                 ([0, 1, 2, 3, 4, 5],
                                                  np.array([[1, 2, 3, 4, 5, 6],
                                                            [5, 6, 7, 8, 9, 10],
                                                            [10, 20, 30, 40, 50, 60]]),
                                                  slice(None, 4)),
                                                 ([0, 1, 2, 3, 4, 5],
                                                  np.array([[1, 2, 3, 4, 5, 6],
                                                            [5, 6, 7, 8, 9, 10],
                                                            [10, 20, 30, 40, 50, 60]]),
                                                  slice(3, None))
                                                 ])
def test_p_signal_slice(time, signal, slice_):
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record_slice = record[slice_]
    assert np.array_equal(record_slice.p_signal, signal[:, slice_])


@pytest.mark.parametrize("slice_,annotation_sliced", [(slice(1, 4), ECGAnnotation([ECGAnnotationSample(0, "N"),
                                                                                   ECGAnnotationSample(1, "N"),
                                                                                   ECGAnnotationSample(2, "N"),
                                                                                   ECGAnnotationSample(4, "N")])),
                                                      (slice(None, 4), ECGAnnotation([ECGAnnotationSample(1, "N"),
                                                                                      ECGAnnotationSample(2, "N"),
                                                                                      ECGAnnotationSample(3, "N"),
                                                                                      ECGAnnotationSample(5, "N")])),
                                                      (0, ECGAnnotation([ECGAnnotationSample(1, "N"),
                                                                         ECGAnnotationSample(2, "N"),
                                                                         ECGAnnotationSample(3, "N"),
                                                                         ECGAnnotationSample(5, "N")])),
                                                      (2, ECGAnnotation([ECGAnnotationSample(-1, "N"),
                                                                         ECGAnnotationSample(0, "N"),
                                                                         ECGAnnotationSample(1, "N"),
                                                                         ECGAnnotationSample(3, "N")]))
                                                      ])
def test_slice_annotation(slice_, annotation_sliced):
    time = [0, 1, 2, 3, 4, 5, 6]
    signal = np.array([[1, 2, 3, 4, 5, 6, 8.2],
                       [5, 6, 7, 8, 9, 10, 9.2],
                       [10, 20, 30, 40, 50, 60, 3.8]])

    annotation1 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(2, "N"),
                                 ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(5, "N")])
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record.annotations = annotation1
    record_slice = record[slice_]

    assert record_slice.annotations == annotation_sliced


@pytest.mark.parametrize("slice_,annotation_sliced", [(slice(1, 4), ECGAnnotation([ECGAnnotationSample(0, "N"),
                                                                                   ECGAnnotationSample(1, "N"),
                                                                                   ECGAnnotationSample(2, "N"),
                                                                                   ECGAnnotationSample(4, "N")])),
                                                      (slice(None, 4), ECGAnnotation([ECGAnnotationSample(1, "N"),
                                                                                      ECGAnnotationSample(2, "N"),
                                                                                      ECGAnnotationSample(3, "N"),
                                                                                      ECGAnnotationSample(5, "N")])),
                                                      (0, ECGAnnotation([ECGAnnotationSample(1, "N"),
                                                                         ECGAnnotationSample(2, "N"),
                                                                         ECGAnnotationSample(3, "N"),
                                                                         ECGAnnotationSample(5, "N")])),
                                                      (2, ECGAnnotation([ECGAnnotationSample(-1, "N"),
                                                                         ECGAnnotationSample(0, "N"),
                                                                         ECGAnnotationSample(1, "N"),
                                                                         ECGAnnotationSample(3, "N")]))
                                                      ])
def test_annotation_sliced_max_index(slice_, annotation_sliced):
    time = [0, 1, 2, 3, 4, 5, 6]
    signal = np.array([[1, 2, 3, 4, 5, 6, 8.2],
                       [5, 6, 7, 8, 9, 10, 9.2],
                       [10, 20, 30, 40, 50, 60, 3.8]])

    annotation1 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(2, "N"),
                                 ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(5, "N")])
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record.annotations = annotation1
    record_slice = record[slice_]
    if isinstance(slice_, slice):
        start = 0 if slice_.start is None else slice_.start
        stop = len(record) if slice_.stop is None else slice_.stop
        assert record_slice.annotations.max_index == stop - start
    else:
        assert record_slice.annotations.max_index == 1


def test_annotation_max_index():
    time = [0, 1, 2, 3, 4, 5, 6]
    signal = np.array([[1, 2, 3, 4, 5, 6, 8.2],
                       [5, 6, 7, 8, 9, 10, 9.2],
                       [10, 20, 30, 40, 50, 60, 3.8]])

    annotation1 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(2, "N"),
                                 ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(5, "N"),
                                 ECGAnnotationSample(6, "A"),
                                 ECGAnnotationSample(250, "X"),
                                 ECGAnnotationSample(300, "N")])
    record = ECGRecord.from_np_array("100", time, signal, ["I", "II", "III"])
    record.annotations = annotation1
    assert record.annotations.max_index == len(record)
    assert len(record.annotations.stem_label("N")) == len(record)
    assert len(record.annotations.stem_label("X")) == len(record)
    assert len(record.annotations.stem_label("A")) == len(record)
    assert len(record.annotations.stem_label("~")) == len(record)
