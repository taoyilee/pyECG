import copy
import glob
import os
import pickle
import random
from functools import lru_cache
from multiprocessing import Pool
from typing import List

import numpy as np
import pandas as pd
from ishneholterlib import Holter

from pyecg import ECGRecord


class RelocatableDataset:
    _dataset_dir = None

    @property
    def dataset_dir(self):
        return self._dataset_dir

    @dataset_dir.setter
    def dataset_dir(self, value):
        if os.path.isdir(value):
            self._dataset_dir = value
        else:
            raise FileNotFoundError(f"{value} is not a valid directory")


class RecordTicket(RelocatableDataset):
    _sig_len = None
    _fs = None

    def __init__(self, record_file, selected_leads=None):
        """

        :param record_file: .hea / .ecg
        :param selected_leads: if this kwarg is specified, lead names outside this list will not be loaded
        """
        self._record_file = record_file
        self._dataset_dir = os.path.dirname(record_file)
        self.selected_leads = selected_leads

    @property
    def fs(self):
        if self._fs is not None:
            return self._fs
        if self.is_ishine:
            record = Holter(self.record_file, check_valid=False)
            self._fs = record.sr
        if self.is_wfdb:
            with open(self.record_file, "r") as fptr:
                line = fptr.readline()
            self._fs = int(line.split(" ")[2])
        return self._fs

    @property
    def duration(self):
        return (self.sig_len - 1) / self.fs

    @property
    def sig_len(self):
        if self._sig_len is not None:
            return self._sig_len
        if self.is_ishine:
            record = Holter(self.record_file, check_valid=False)
            self._sig_len = record.ecg_size
        if self.is_wfdb:
            with open(self.record_file, "r") as fptr:
                line = fptr.readline()
            self._sig_len = int(line.split(" ")[3])
        return self._sig_len

    @property
    def extension(self):
        return os.path.splitext(self.record_file)[1].lower()

    @property
    def is_wfdb(self):
        if self.extension == ".hea":
            return True
        if self.extension == "":
            file_candidates = glob.glob(self.record_file + "*.hea")
            file_candidates += glob.glob(self.record_file + "*.ecg")
            if len(file_candidates) == 0:
                raise FileNotFoundError(f"No hea/ecg file found with basename {self.record_file}")
            if len(file_candidates) > 1:
                raise ValueError(f"Too many files ({len(file_candidates)}) starts with {self.record_file}")
            if os.path.splitext(file_candidates[0])[1].lower() == ".hea":
                return True
        return False

    @property
    def is_ishine(self):
        extension = self.extension
        if extension == "":
            file_candidates = glob.glob(self.record_file + "*.hea")
            file_candidates += glob.glob(self.record_file + "*.ecg")
            if len(file_candidates) == 0:
                raise FileNotFoundError(f"No hea/ecg file found with basename {self.record_file}")
            if len(file_candidates) > 1:
                raise ValueError(f"Too many files ({len(file_candidates)}) starts with {self.record_file}")
            extension = os.path.splitext(file_candidates[0])[1].lower()
        if extension == ".ecg":
            return True
        return False

    @property
    def record_name(self):
        return os.path.splitext(self.record_base)[0]

    @property
    def record_base(self):
        return os.path.split(self.record_file)[1]

    @property
    def record_file(self):
        return os.path.join(self.dataset_dir, os.path.split(self._record_file)[1])

    @lru_cache(maxsize=64)
    def __call__(self, *args, **kwargs):
        """
        Call means load from disk
        :param args:
        :param kwargs:
        :return:
        """
        if self.is_wfdb:
            return ECGRecord.from_wfdb(self.record_file, self.selected_leads)
        elif self.is_ishine:
            return ECGRecord.from_ishine(self.record_file, self.selected_leads)
        else:
            raise ValueError(f"Unknown extension")

    def __repr__(self):
        return os.path.split(self._record_file)[1]

    def __key(self):
        if self.selected_leads is None:
            return self.record_base, self.selected_leads
        else:
            return tuple([self.record_file] + self.selected_leads)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()


class RecordGetAttrCallable:
    def __init__(self, attr):
        self.attr = attr

    def __call__(self, x):
        return getattr(x, self.attr)


class RecordThawingCallable:
    def __call__(self, x):
        return x()


RECORD_LOAD_THREADS = 2


class ECGDataset(RelocatableDataset):
    record_tickets: List[RecordTicket] = []
    dataset_name = None
    _df = None

    @property
    def duration(self):
        if self._df is not None:
            return self._df["duration"].tolist()
        with Pool(RECORD_LOAD_THREADS) as p:
            return p.map(RecordGetAttrCallable("duration"), self.record_tickets)

    @property
    def sig_len(self):
        if self._df is not None:
            return self._df["sig_len"].tolist()
        with Pool(RECORD_LOAD_THREADS) as p:
            return p.map(RecordGetAttrCallable("sig_len"), self.record_tickets)

    def __init__(self, dataset_name=None, dataset_dir=None, record_tickets: List[RecordTicket] = []):
        if not os.path.isdir(dataset_dir):
            raise FileNotFoundError(f"{dataset_dir} is not a directory")

        if dataset_name is not None:
            self.dataset_name = dataset_name
        else:
            self.dataset_name = os.path.split(dataset_dir)[1]

        self._dataset_dir = dataset_dir
        self.record_tickets = record_tickets

    @property
    def records(self):
        return [rt() for rt in self.record_tickets]

    def __iter__(self):
        return iter(self.records)

    def __getitem__(self, item):
        if isinstance(item, slice):
            with Pool(4) as p:
                return p.map(RecordThawingCallable(), self.record_tickets[item])
        else:
            return self.record_tickets[item]()

    def shuffle(self):
        random.shuffle(self.record_tickets)

    def slice(self, item):
        new_instance = copy.copy(self)
        new_instance.record_tickets = new_instance.record_tickets[item]
        return new_instance

    @classmethod
    def from_dir(cls, dataset_dir, selected_leads=None):
        if not os.path.isdir(dataset_dir):
            raise FileNotFoundError(f"{dataset_dir} does not exist")

        hea_files = glob.glob(os.path.join(dataset_dir, "*.hea"))
        ecg_files = glob.glob(os.path.join(dataset_dir, "*.ecg"))
        record_tickets = [RecordTicket(f, selected_leads) for f in hea_files + ecg_files]
        if len(record_tickets) == 0:
            raise FileNotFoundError(f"{dataset_dir} does not contain any valid ECG record")
        return cls(dataset_dir=dataset_dir, record_tickets=record_tickets)

    def split_dataset(self, dataset_names=None, *ratios):
        """

        :param dataset_names: ["train", "dev", "test"]
        :param ratios: 0.8, 0.1
        :return:
        """
        if sum(ratios) > 1:
            raise ValueError("Sum of ratios should be less than or equal to 1")
        if len(dataset_names) != len(ratios) + 1:
            raise ValueError("len(dataset_names) must == len(ratios) + 1")
        record_numbers = (len(self) * np.array(ratios)).astype(int).tolist()  # type:list
        record_numbers.append(len(self) - sum(record_numbers))
        output_dataset = []
        starting_index = 0
        for name, number in zip(dataset_names, record_numbers):
            ending_index = starting_index + number
            new_dataset = self.slice(slice(starting_index, ending_index))
            new_dataset.dataset_name = name
            output_dataset.append(new_dataset)
            starting_index = ending_index
        return tuple(output_dataset)

    def save_csv(self, output_file_name):
        """

        :param output_file_name: if extension is .csv, create directory and write into the file, if not assume this is directory and write into dataset_name_records.csv
        :return:
        """
        extension = os.path.splitext(output_file_name)[1].lower()
        if extension != ".csv":
            output_file_name = os.path.join(output_file_name, self.dataset_name + "_records.csv")
        try:
            os.makedirs(os.path.dirname(output_file_name))
        except OSError:
            pass
        data = {"Dataset_Directory": [], "Base_Name": []}
        for r in self.record_tickets:
            data["Dataset_Directory"].append(r.dataset_dir)
            data["Base_Name"].append(r.record_base)
        data["sig_len"] = self.sig_len
        data["duration"] = self.duration
        self._df = pd.DataFrame(data)
        self._df.to_csv(output_file_name)
        return output_file_name

    def to_pickle(self, output_file_name):
        extension = os.path.splitext(output_file_name)[1].lower()
        if extension != "" and extension != ".pickle":
            raise ValueError("Extension must be .pickle")
        if extension == "":  # output_file_name is a directory
            output_csv_name = output_file_name
            output_file_name = os.path.join(output_file_name, self.dataset_name + ".pickle")
        else:
            output_csv_name = os.path.splitext(output_file_name)[0] + ".csv"

        self.save_csv(output_csv_name)
        with open(output_file_name, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        return output_file_name

    @classmethod
    def from_pickle(cls, pickle_file):
        if not os.path.isfile(pickle_file):
            raise FileNotFoundError(f"{pickle_file} is not found")
        with open(pickle_file, 'rb') as f:
            return pickle.load(f)

    def __len__(self):
        return len(self.record_tickets)

    def __add__(self, other):
        new_instance = copy.copy(self)
        new_instance.record_tickets += other.record_tickets
        return new_instance

    def __repr__(self):
        record_str = '\n'.join([str(r) for r in self.record_tickets])
        return f"Dataset with records\n{record_str}"

    def __eq__(self, other):
        for s, o in zip(self.record_tickets, other.record_tickets):
            if s != o:
                return False
        return True
