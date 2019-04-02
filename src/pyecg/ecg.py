import abc
import copy
from typing import List

import numpy as np

from .annotations import ECGAnnotation
from .sequence_data import Time
from .subject_info import SubjectInfo


class RecordSignalLoader:
    def __init__(self, record_loader, signal_index, lead_name):
        self.record_loader = record_loader
        self.signal_index = signal_index
        self.lead_name = lead_name
        self._slice = None

    def slice(self, slice_):
        new_instance = copy.copy(self)
        new_instance._slice = slice_
        return new_instance

    def __key(self):
        return self.record_loader.record_file, self.signal_index, self.lead_name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def __call__(self, *args, **kwargs):
        p_signal = self.record_loader()
        if self._slice is None:
            return p_signal[self.signal_index, :].tolist()
        else:
            return p_signal[self.signal_index, self._slice].tolist()


class RecordLoader:
    def __init__(self, record_file):
        self.record_file = record_file

    def __key(self):
        return self.record_file

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class FixedRecordLoader(RecordLoader):
    def __init__(self, p_signal):
        super(FixedRecordLoader, self).__init__(None)
        self.p_signal = p_signal

    def __call__(self, *args, **kwargs):
        return self.p_signal


class ECGRecord:
    time: Time = None
    record_name: str = None
    _signal_loaders: List[RecordSignalLoader] = []
    _annotations: ECGAnnotation = None
    _annotation_loader = None
    _record_loader = None
    info: SubjectInfo = None

    @property
    def signals(self):
        return [sl() for sl in self._signal_loaders]

    @property
    def annotations(self):
        if self._annotations is None and self._annotation_loader is not None:
            self._annotations = self._annotation_loader()
            self._annotations.max_index = len(self)
        return self._annotations

    @annotations.setter
    def annotations(self, value):
        self._annotations = value
        self._annotations.max_index = len(self)

    def __key(self):
        return tuple([self.record_name, self.n_sig, self.annotations] + self.signals)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def __init__(self, name, time):
        self.record_name = name
        if not isinstance(time, Time):
            raise TypeError("time should be ECGTime")
        self.time = time
        self._signal_loaders = []

    @property
    def duration(self):
        return max(self.time)

    @property
    def n_sig(self):
        return len(self._signal_loaders)

    @property
    def p_signal(self):
        return np.array([s() for s in self._signal_loaders])

    @property
    def lead_names(self):
        if self._signal_loaders:
            return [s.lead_name for s in self._signal_loaders]
        else:
            return [s.lead_name for s in self._signal_loaders]

    def get_lead(self, lead_name):
        try:
            return list(filter(lambda s: s.lead_name == lead_name, self._signal_loaders))[0]()
        except IndexError:
            return None

    def add_signal(self, signal):
        if not isinstance(signal, RecordSignalLoader):
            raise TypeError("signal should be RecordSignalLoader")
        self._signal_loaders.append(signal)

    def __len__(self):
        return len(self.time)

    def __repr__(self):
        return f"Record {self.record_name}: {self.lead_names}"

    def __getitem__(self, item):
        new_instance = copy.copy(self)
        new_instance.time = new_instance.time.slice(item)
        if new_instance.annotations is not None:
            if isinstance(item, slice):
                new_instance.annotations = new_instance.annotations.shift(0 if item.start is None else -item.start)
                new_instance.annotations.max_index = len(new_instance)
            else:
                new_instance.annotations = new_instance.annotations.shift(-item)
                new_instance.annotations.max_index = 1
        new_instance._signal_loaders = [s.slice(item) for s in new_instance._signal_loaders]
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
        record_loader = FixedRecordLoader(signal_array)
        for i, name in enumerate(signal_names):
            new_instance.add_signal(RecordSignalLoader(record_loader, i, name))
        return new_instance
