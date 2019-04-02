import os
from functools import lru_cache

import wfdb

from pyecg import ECGRecord, Time
from pyecg import RecordLoader, RecordSignalLoader
from pyecg.annotations import ECGAnnotation, ECGAnnotationSample, AnnotationLoader
from . import Importer


class WFDBAnnotationLoader(AnnotationLoader):
    def __init__(self, ann_file):
        super(WFDBAnnotationLoader, self).__init__(ann_file)

    @lru_cache(maxsize=64)
    def __call__(self, *args, **kwargs) -> ECGAnnotation:
        base_path = os.path.splitext(self.annotation_file)[0]
        atr_file = base_path + ".atr"
        if not os.path.isfile(atr_file):
            raise FileNotFoundError(f"{atr_file} is not found")

        ann = wfdb.rdann(base_path, "atr")
        return ECGAnnotation([ECGAnnotationSample(samp, symbol) for samp, symbol in zip(ann.sample, ann.symbol)])


class WFDBRecordLoader(RecordLoader):
    def __init__(self, hea_file):
        super(WFDBRecordLoader, self).__init__(hea_file)

    @lru_cache(maxsize=64)
    def __call__(self, *args, **kwargs):
        base_path = os.path.splitext(self.record_file)[0]
        hea_file = base_path + ".hea"
        if not os.path.isfile(hea_file):
            raise FileNotFoundError(f"{hea_file} is not found")
        record = wfdb.rdrecord(base_path)
        return record.p_signal.T


class WFDBLoader(Importer):

    def load(self, hea_file) -> ECGRecord:
        record_loader = WFDBRecordLoader(hea_file)
        base_path = os.path.splitext(hea_file)[0]
        record_name = os.path.split(base_path)[1]
        ann_file = base_path + ".atr"
        hea_file = base_path + ".hea"

        if not os.path.isfile(hea_file):
            raise FileNotFoundError(f"{hea_file} is not found")
        with open(hea_file, "r") as fptr:
            line = fptr.readline()
            n_sig = int(line.split(" ")[1])
            fs = int(line.split(" ")[2])
            sig_len = int(line.split(" ")[3])
            sig_line = [fptr.readline() for _ in range(n_sig)]

        time = Time.from_fs_samples(fs, sig_len)
        lead_names = [s.split(" ")[-1].strip(" \n") for s in sig_line]
        new_record = ECGRecord(name=record_name, time=time)
        new_record._record_loader = record_loader
        new_record._annotation_loader = WFDBAnnotationLoader(ann_file)

        for i, lead_name in enumerate(lead_names):
            if self.selected_leads is None or lead_name in self.selected_leads:
                new_record.add_signal(RecordSignalLoader(record_loader, i, lead_name))

        return new_record
