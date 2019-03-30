import copy

import numpy as np


def is_monotonic_increasing(x):
    return np.all(np.diff(x) > 0)


class ECGRecord:
    time = None
    name = None
    _signals = []
    _annotations = []
    _subject_info = None

    def __init__(self, name, time):
        self.name = name
        if not isinstance(time, ECGTime):
            raise TypeError("time should be ECGTime")
        self.time = time
        self._signals = []

    @property
    def n_sig(self):
        return len(self._signals)

    @property
    def lead_names(self):
        return [s.lead_name for s in self._signals]

    def get_lead(self, lead_name):
        try:
            return list(filter(lambda s: s.lead_name == lead_name, self._signals))[0]
        except IndexError:
            return None

    def __len__(self):
        return len(self.time)

    def _add_signal(self, signal):
        if not isinstance(signal, ECGSignal):
            raise TypeError("signal should be ECGSignal")
        if len(signal) != len(self):
            raise ValueError(f"len(signal) has {len(signal)} samples != len(timestamps) = {len(self.time)}")
        self._signals.append(signal)

    @classmethod
    def from_np_array(cls, name, time, signal_array, signal_names):
        new_instance = cls(name, ECGTime.from_timestamps(time))
        if len(signal_array.shape) != 2:
            raise ValueError(f"Signal should be 2D array e.g. (3, 1000) got {signal_array.shape}")
        if signal_array.shape[0] != len(signal_names):
            raise ValueError(f"signal_array.shape[0] should match len(signal_names)")

        for signal, name in zip(signal_array, signal_names):
            new_instance._add_signal(ECGSignal(signal=signal, lead_name=name))
        return new_instance

    def __repr__(self):
        return f"Record {self.name}: {self.lead_names}"

    def __getitem__(self, item):
        new_instance = copy.copy(self)
        new_instance.time = new_instance.time[item]
        new_instance._signals = new_instance._signals.copy()
        for i, s in enumerate(new_instance._signals):
            new_instance._signals[i] = ECGSignal(s[item], s.lead_name)
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


class ECGTime:
    _timestamps = None
    fs = None
    samples = None

    def __len__(self):
        return len(self.time)

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
        if time_stamps is not None and not isinstance(time_stamps, list) and not isinstance(time_stamps, np.ndarray):
            raise TypeError(f"time_stamps should be a np.ndarray or a list: {type(time_stamps)}")
        self._timestamps = time_stamps

    def __getitem__(self, item):
        new_instance = copy.copy(self)
        if isinstance(item, slice):
            new_instance._timestamps = new_instance.time[item]
        else:
            new_instance._timestamps = [new_instance.time[item]]
        return new_instance

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

    def __iter__(self):
        return iter(self.signal)

    def __eq__(self, other):
        return self.signal == other

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.signal[item]
        else:
            return [self.signal[item]]

    def __repr__(self):
        return f"Lead {self.lead_name}"

    def __init__(self, signal, lead_name):
        if not isinstance(signal, list) and not isinstance(signal, np.ndarray):
            raise TypeError(f"signal should be a np.ndarray or a list: {type(signal)}")
        if isinstance(signal, np.ndarray):
            self.signal = signal.tolist()
        else:
            self.signal = signal
        self.lead_name = lead_name

    def __len__(self):
        return len(self.signal)


class SubjectInfo:
    def __init__(self):
        pass
