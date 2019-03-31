import abc

from pyecg import ECGRecord


class Importer:
    def __init__(self, selected_leads=None):
        self.selected_leads = selected_leads

    @abc.abstractmethod
    def load(self, ecg_raw_file) -> ECGRecord:
        pass
