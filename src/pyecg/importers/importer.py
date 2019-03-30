import abc

from pyecg import ECGRecord


class Importer:
    @abc.abstractmethod
    def load(self, ecg_raw_file) -> ECGRecord:
        pass
