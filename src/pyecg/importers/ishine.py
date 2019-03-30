import os

import wfdb

from pyecg import ECGRecord, ECGTime, ECGSignal
from . import Importer


class ISHINELoader(Importer):

    def load(self, hea_file) -> ECGRecord:
        def load_annotation(ann_ext):
            return wfdb.rdann(hea_file, ann_ext)

        base_path = os.path.splitext(hea_file)[0]
        hea_file = base_path + ".hea"
        if not os.path.isfile(hea_file):
            raise FileNotFoundError(f"{hea_file} is not found")

        record = wfdb.rdrecord(base_path)
        time = ECGTime.from_fs_samples(record.fs, record.sig_len)
        new_record = ECGRecord(name=record.record_name, time=time)

        for signal, lead_name in zip(record.p_signal.T, record.sig_name):
            new_record._add_signal(ECGSignal(signal, lead_name))
        return new_record
