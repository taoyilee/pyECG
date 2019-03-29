import numpy as np


def is_monotonic_increasing(x):
    return np.all(np.diff(x) > 0)


class ECGRecord:
    time = None

    def __init__(self):
        pass


class ECGTime:
    _timestamps = None
    fs = None
    samples = None

    @property
    def time(self):
        if self._timestamps is not None:
            return self._timestamps
        else:
            self._timestamps = (1 / self.fs) * np.arange(0, self.samples)
            return self._timestamps

    def __init__(self, fs=None, samples=None, time_stamps=None):
        self.fs = fs
        self.samples = samples
        self._timestamps = time_stamps

    @classmethod
    def from_fs_samples(cls, fs, samples):
        return cls(fs=fs, samples=samples)

    @classmethod
    def from_timestamps(cls, time_stamps):
        if not is_monotonic_increasing(time_stamps):
            raise ValueError("Timestamps are not monotonically increasing")
        return cls(time_stamps=time_stamps)


class ECGAnnotation:
    def __init__(self):
        pass


class ECGSignal:
    lead_name = None
    signal = None

    def __init__(self):
        pass


class SubjectInfo:
    def __init__(self):
        pass
