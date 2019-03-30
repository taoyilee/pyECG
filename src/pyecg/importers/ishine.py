import os

from ishneholterlib import Holter

from pyecg import ECGRecord, ECGTime, ECGSignal
from . import Importer


class ISHINELoader(Importer):

    def load(self, ecg_file) -> ECGRecord:
        if not os.path.isfile(ecg_file):
            raise FileNotFoundError(f"{ecg_file} is not found")
        record = Holter(ecg_file)
        record.load_data()
        time = ECGTime.from_fs_samples(record.sr, len(record.lead[0].data))
        record_name = os.path.split(ecg_file)[1]
        record_name = ".".join(record_name.split(".")[:-1])
        new_record = ECGRecord(name=record_name, time=time)

        for leadi in record.lead:
            new_record._add_signal(ECGSignal(leadi.data, str(leadi)))

        return new_record
