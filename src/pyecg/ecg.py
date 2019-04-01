import copy
from typing import List

import numpy as np

from .annotations import ECGAnnotation
from .sequence_data import Time, Signal
from .subject_info import SubjectInfo


class ECGRecord:
    time: Time = None
    record_name: str = None
    _signals: List[Signal] = []
    annotations: ECGAnnotation = None
    info: SubjectInfo = None

    def __eq__(self, other):
        if self.n_sig != other.n_sig:
            return False
        if self.record_name != other.record_name:
            return False
        if self._signals != other._signals:
            return False
        if self.annotations != other.annotations:
            return False
        if self.info != other.info:
            return False
        return True

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
    def from_wfdb(cls, hea_file, selected_leads=None):
        from pyecg.importers import WFDBLoader
        loader = WFDBLoader(selected_leads=selected_leads)
        return loader.load(hea_file)

    @classmethod
    def from_ishine(cls, ecg_file, selected_leads=None):
        from pyecg.importers import ISHINELoader
        loader = ISHINELoader(selected_leads=selected_leads)
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
