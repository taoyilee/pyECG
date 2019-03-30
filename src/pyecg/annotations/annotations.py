from .constants import *


class ECGAnnotationSample:
    def __init__(self, index, label=NORMAL_BEAT):
        self.index = index
        self.label = label

    def __eq__(self, other):
        if self.index == other.index and self.label == other.label:
            return True
        return False


class ECGAnnotation:
    _annotation_samples = []

    def __iter__(self):
        return iter(self._annotation_samples)

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for s, o in zip(self, other):
            if s != o:
                return False
        return True

    def __len__(self):
        return len(self._annotation_samples)

    def __init__(self, annotations=[]):
        self._annotation_samples = annotations

    @property
    def unique_labels(self):
        unique_labels = list(set([i.label for i in self._annotation_samples]))
        unique_labels.sort()
        return unique_labels

    def select_label(self, label):
        return ECGAnnotation(list(filter(lambda x: x.label == label, self._annotation_samples)))

    def __add__(self, other):
        return ECGAnnotation(self._annotation_samples + other._annotation_samples)
