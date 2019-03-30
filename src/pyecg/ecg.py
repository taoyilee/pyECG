import copy
from typing import List

import numpy as np

from pyecg.annotations import ECGAnnotation


def is_monotonic_increasing(x):
    return np.all(np.diff(x) > 0)


class SubjectInfo:
    sex = None  # 1=male, 2=female
    race = None  # 1=white, 2=black, 3=oriental
    birth_data = None
    record_data = None
    file_date = None
    start_time = None
    pm = None


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


class ECGRecord:
    time: Time = None
    record_name: str = None
    _signals: List[Signal] = []
    annotations: ECGAnnotation = None
    info: SubjectInfo = None

    def __init__(self, name, time):
        self.record_name = name
        if not isinstance(time, Time):
            raise TypeError("time should be ECGTime")
        self.time = time
        self._signals = []

    @property
    def duration(self):
        return max(self.time)

    @property
    def n_sig(self):
        return len(self._signals)

    @property
    def p_signal(self):
        return np.array([s for s in self._signals])

    @property
    def lead_names(self):
        return [s.lead_name for s in self._signals]

    def get_lead(self, lead_name):
        try:
            return list(filter(lambda s: s.lead_name == lead_name, self._signals))[0]
        except IndexError:
            return None

    def add_signal(self, signal):
        if not isinstance(signal, Signal):
            raise TypeError("signal should be ECGSignal")
        if len(signal) != len(self):
            raise ValueError(f"len(signal) has {len(signal)} samples != len(timestamps) = {len(self.time)}")
        self._signals.append(signal)

    def __len__(self):
        return len(self.time)

    def __repr__(self):
        return f"Record {self.record_name}: {self.lead_names}"

    def __getitem__(self, item):
        new_instance = copy.copy(self)
        new_instance.time = new_instance.time.slice(item)
        new_instance._signals = [s.slice(item) for s in new_instance._signals]
        return new_instance

    @classmethod
    def from_wfdb(cls, hea_file):
        from pyecg.importers import WFDBLoader
        loader = WFDBLoader()
        return loader.load(hea_file)

    @classmethod
    def from_ishine(cls, ecg_file):
        from pyecg.importers import ISHINELoader
        loader = ISHINELoader()
        return loader.load(ecg_file)

    @classmethod
    def from_np_array(cls, name, time, signal_array, signal_names):
        new_instance = cls(name, Time.from_timestamps(time))
        if len(signal_array.shape) != 2:
            raise ValueError(f"Signal should be 2D array e.g. (3, 1000) got {signal_array.shape}")
        if signal_array.shape[0] != len(signal_names):
            raise ValueError(f"signal_array.shape[0] should match len(signal_names)")

        for signal, name in zip(signal_array, signal_names):
            new_instance.add_signal(Signal(signal=signal, lead_name=name))
        return new_instance
