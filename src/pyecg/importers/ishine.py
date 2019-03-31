import os

import numpy as np
from ishneholterlib import Holter

from pyecg import ECGRecord, Time, Signal, SubjectInfo
from pyecg.annotations import ECGAnnotation, ECGAnnotationSample
from . import Importer


class ISHINELoader(Importer):

    def load(self, ecg_file) -> ECGRecord:
        if not os.path.isfile(ecg_file):
            raise FileNotFoundError(f"{ecg_file} is not found")
        record = Holter(ecg_file, check_valid=False)
        record.load_data()

        def load_ann(ann_file, annheader):
            filesize = os.path.getsize(ann_file)
            headersize = 522 + annheader.var_block_size + 4
            record.beat_anns = []
            with open(ann_file, 'rb') as f:
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
                    record.beat_anns.append({'ann': ann, 'internal': internal, 'toc': toc})
                    if not timeout:
                        record.beat_anns[-1]['samp_num'] = current_sample

        ann_file = os.path.splitext(ecg_file)[0] + '.ann'
        ann_header = Holter(ann_file, check_valid=False, annfile=True)
        load_ann(ann_file, ann_header)

        time = Time.from_fs_samples(record.sr, len(record.lead[0].data))
        record_name = os.path.split(ecg_file)[1]
        record_name = ".".join(record_name.split(".")[:-1])
        new_record = ECGRecord(name=record_name, time=time)

        for lead in record.lead:
            lead_name = str(lead)
            if self.selected_leads is None or lead_name in self.selected_leads:
                new_record.add_signal(Signal(lead.data, lead_name))

        ecg_annotation = ECGAnnotation([ECGAnnotationSample(i["samp_num"], i["ann"]) for i in record.beat_anns])
        new_record.annotations = ecg_annotation

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
