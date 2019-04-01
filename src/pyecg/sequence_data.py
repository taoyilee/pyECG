import copy

import numpy as np


def is_monotonic_increasing(x):
    return np.all(np.diff(x) > 0)


class Sequence:
    seq_data = None

    def __eq__(self, other):
        return self.seq_data == other

    def __getitem__(self, item):
        return self.seq_data[item]

    def slice(self, slice_):
        new_instance = copy.copy(self)
        new_instance.seq_data = new_instance[slice_]
        return new_instance

    def __len__(self):
        if isinstance(self.seq_data, int) or isinstance(self.seq_data, float):
            return 1
        return len(self.seq_data)

    def __iter__(self):
        return iter(self.seq_data)


class Time(Sequence):
    fs = None
    samples = None

    @property
    def time(self):
        return self.seq_data

    def __init__(self, fs=None, samples=None, time_stamps=None):
        if fs is not None and samples is not None:
            self.fs = fs
            self.samples = samples
            self.seq_data = (1 / self.fs) * np.arange(0, self.samples)
            return

        if time_stamps is not None and not isinstance(time_stamps, list) and not isinstance(time_stamps, np.ndarray):
            raise TypeError(f"time_stamps should be a np.ndarray or a list: {type(time_stamps)}")
        if time_stamps is not None:
            self.seq_data = time_stamps

    @classmethod
    def from_fs_samples(cls, fs, samples):
        return cls(fs=fs, samples=samples)

    @classmethod
    def from_timestamps(cls, time_stamps):
        if not is_monotonic_increasing(time_stamps):
            raise ValueError("Timestamps are not monotonically increasing")
        return cls(time_stamps=time_stamps)


class Signal(Sequence):
    lead_name = None

    def __repr__(self):
        return f"Lead {self.lead_name}"

    def __init__(self, signal, lead_name):
        if isinstance(signal, str):
            raise TypeError(f"Bad type of signal: {type(signal)}")
        if isinstance(signal, np.ndarray):
            self.seq_data = signal.tolist()
        else:
            self.seq_data = signal
        self.lead_name = lead_name
