import abc
import copy

import numpy as np

from .constants import *


class AnnotationLoader:
    def __init__(self, annotation_file):
        self.annotation_file = annotation_file

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class ECGAnnotationSample:
    def __init__(self, index: int, label=NORMAL_BEAT):
        if index % 1 != 0:
            raise ValueError(f"Index must be an int {type(index)}")
        self.index = int(index)
        self.label = label

    def __eq__(self, other):
        if self.index == other.index and self.label == other.label:
            return True
        return False

    def shift(self, index_shift: int):
        if not isinstance(index_shift, int):
            raise ValueError("Index shift must be an int")
        new_instance = copy.copy(self)
        new_instance.index += index_shift
        return new_instance

    def __lt__(self, other):
        return self.index < other.index

    def __gt__(self, other):
        return self.index > other.index

    def __repr__(self):
        return f"{self.label} @ {self.index}"


class ECGAnnotation:
    _labels = []
    _max_index = None

    @property
    def max_index(self):
        if self._max_index is not None:
            return self._max_index
        else:
            return max([s.index for s in self._labels]) + 1

    @max_index.setter
    def max_index(self, value):
        if isinstance(value, int):
            self._max_index = value
        else:
            raise ValueError("max_index must be an integer")

    def __iter__(self):
        return iter(self._labels)

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for s, o in zip(self, other):
            if s != o:
                return False
        return True

    def __len__(self):
        return len(self._labels)

    def _sort(self):
        self._labels.sort()

    def __init__(self, labels=[]):
        self._labels = labels
        self._sort()

    @property
    def labels(self):
        return np.array([labeli.label for labeli in self._labels if labeli.index < self.max_index])

    def stem_label(self, label, use_adjacent=True) -> np.ndarray:
        return_array = np.full(self.max_index, False)
        selected_labels = list(filter(lambda x: 0 <= x.index < self.max_index and x.label == label, self._labels))
        indexes = [i.index for i in selected_labels]
        return_array[indexes] = True
        if use_adjacent:
            if self.left_label == label:
                return_array[0] = True
            if self.right_label == label:
                return_array[-1] = True
        return return_array

    @property
    def left_label(self):
        selected_annotations = list(filter(lambda x: x.index <= 0, self._labels))
        if not selected_annotations:
            return None
        else:
            return selected_annotations[-1].label

    @property
    def right_label(self):
        selected_annotations = list(filter(lambda x: x.index >= self.max_index, self._labels))
        if not selected_annotations:
            return None
        else:
            return selected_annotations[0].label

    def shift(self, index_shift):
        if not isinstance(index_shift, int):
            raise ValueError("Index shift must be an int")
        new_instance = copy.copy(self)
        new_instance._labels = [a.shift(index_shift) for a in new_instance._labels]
        return new_instance

    @property
    def unique_labels(self):
        unique_labels = list(set([i.label for i in self._labels]))
        unique_labels.sort()
        return unique_labels

    def __getitem__(self, item):
        new_instance = copy.copy(self)
        new_instance._labels = list(filter(lambda x: x.label == item, self._labels))
        return new_instance

    def __add__(self, other):
        return ECGAnnotation(self._labels + other._labels)
