import os

import wfdb

from pyecg import ECGRecord, Time, Signal
from pyecg.annotations import ECGAnnotation, ECGAnnotationSample
from . import Importer


class WFDBLoader(Importer):

    def load(self, hea_file) -> ECGRecord:
        base_path = os.path.splitext(hea_file)[0]

        def load_annotation(ann_ext):
            return wfdb.rdann(base_path, ann_ext)

        hea_file = base_path + ".hea"
        if not os.path.isfile(hea_file):
            raise FileNotFoundError(f"{hea_file} is not found")

        record = wfdb.rdrecord(base_path)
        time = Time.from_fs_samples(record.fs, record.sig_len)
        new_record = ECGRecord(name=record.record_name, time=time)

        for signal, lead_name in zip(record.p_signal.T, record.sig_name):
            new_record.add_signal(Signal(signal, lead_name))
        ann = load_annotation("atr")

        ecg_annotation = ECGAnnotation([ECGAnnotationSample(samp, symbol) for samp, symbol in zip(ann.sample, ann.symbol)])
        new_record.annotations = ecg_annotation
        return new_record
