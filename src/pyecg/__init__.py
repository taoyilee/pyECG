# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

from .annotations import ECGAnnotation
from .ecg import ECGRecord,RecordLoader,RecordSignalLoader
from pyecg.dataset import RecordTicket, ECGDataset
from .sequence_data import Time, Signal
from .subject_info import SubjectInfo

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'pyECG'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound
