import os
from functools import lru_cache

import numpy as np
from ishneholterlib import Holter

from pyecg import ECGRecord, Time
from pyecg import RecordLoader
from pyecg import RecordSignalLoader
from pyecg import SubjectInfo
from pyecg.annotations import ECGAnnotation, ECGAnnotationSample, AnnotationLoader
from . import Importer


class ISHINEAnnotationLoader(AnnotationLoader):
    def __init__(self, ann_file):
        super(ISHINEAnnotationLoader, self).__init__(ann_file)

    @lru_cache(maxsize=64)
    def __call__(self, *args, **kwargs) -> ECGAnnotation:
        if not os.path.isfile(self.annotation_file):
            raise FileNotFoundError(f"{self.annotation_file} is not found")
        ann_header = Holter(self.annotation_file, check_valid=False, annfile=True)
        filesize = os.path.getsize(self.annotation_file)
        headersize = 522 + ann_header.var_block_size + 4
        beat_anns = []
        with open(self.annotation_file, 'rb') as f:
            f.seek(headersize - 4, os.SEEK_SET)
            first_sample = np.fromfile(f, dtype=np.uint32, count=1)[0]
            current_sample = first_sample
            timeout = False  # was there a gap in the annotations?
            for beat in range(int((filesize - headersize) / 4)):
                # note, the beat at first_sample isn't annotated.  so the first beat
                # in beat_anns is actually the second beat of the recording.
                ann = chr(np.fromfile(f, dtype=np.uint8, count=1)[0])
                internal = chr(np.fromfile(f, dtype=np.uint8, count=1)[0])
                toc = np.fromfile(f, dtype=np.int16, count=1)[0]
                current_sample += toc
                if ann == '!':
                    timeout = True  # there was a few minutes gap in the anns; don't
                    # know how to line them up to rest of recording
                beat_anns.append({'ann': ann, 'internal': internal, 'toc': toc})
                if not timeout:
                    beat_anns[-1]['samp_num'] = current_sample

        return ECGAnnotation([ECGAnnotationSample(i["samp_num"], i["ann"]) for i in beat_anns])


class ISHINERecordLoader(RecordLoader):
    def __init__(self, ecg_file):
        super(ISHINERecordLoader, self).__init__(ecg_file)

    @lru_cache(maxsize=64)
    def __call__(self, *args, **kwargs):
        if not os.path.isfile(self.record_file):
            raise FileNotFoundError(f"{self.record_file} is not found")
        record = Holter(self.record_file, check_valid=False)
        record.load_data()
        return np.array([lead.data for lead in record.lead])


class ISHINELoader(Importer):

    def load(self, ecg_file) -> ECGRecord:
        if not os.path.isfile(ecg_file):
            raise FileNotFoundError(f"{ecg_file} is not found")

        record = Holter(ecg_file, check_valid=False)
        time = Time.from_fs_samples(record.sr, record.ecg_size)
        record_name = os.path.split(ecg_file)[1]
        record_name = ".".join(record_name.split(".")[:-1])

        new_record = ECGRecord(name=record_name, time=time)
        record_loader = ISHINERecordLoader(ecg_file)
        new_record._record_loader = record_loader

        ann_file = os.path.splitext(ecg_file)[0] + '.ann'
        new_record._annotation_loader = ISHINEAnnotationLoader(ann_file)

        for i, lead in enumerate(record.lead):
            lead_name = str(lead)
            if self.selected_leads is None or lead_name in self.selected_leads:
                new_record.add_signal(RecordSignalLoader(record_loader, i, lead_name))

        # copy over subject basic info
        new_record.info = SubjectInfo()
        new_record.info.race = record.race
        new_record.info.sex = record.sex
        new_record.info.birth_date = record.birth_date
        new_record.info.record_date = record.record_date
        new_record.info.file_date = record.file_date
        new_record.info.start_time = record.start_time
        new_record.info.pm = record.pm

        return new_record
