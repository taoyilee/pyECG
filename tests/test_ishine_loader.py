import pytest

from pyecg import ECGRecord


@pytest.mark.parametrize("ecg_path", ["tests/wfdb/nonexistent", "tests/wfdb/nonexistent.hea"])
def test_file_notfound(ecg_path):
    with pytest.raises(FileNotFoundError):
        ECGRecord.from_ishine(ecg_path)


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_length(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert len(record) == 95573


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_signal(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.n_sig == 12


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_record_name(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.record_name == "ECG_P28.01"


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_signal_name(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.lead_names == ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


@pytest.mark.parametrize("ecg_path,lead_name,signal", [("tests/ishine/ECG_P28.01.ecg",
                                                        "II",
                                                        [0.04, 0.035, 0.04, 0.045, 0.065, 0.05, 0.045, 0.04, 0.03,
                                                         0.035]),
                                                       ("tests/ishine/ECG_P28.01.ecg",
                                                        "V5",
                                                        [0.08, 0.08, 0.08, 0.08, 0.085, 0.08, 0.08, 0.08, 0.075,
                                                         0.075])])
def test_signal_content(ecg_path, lead_name, signal):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.get_lead(lead_name)[:10] == signal


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_annotation(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert len(record.annotations) == 97


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_select_annotation(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert len(record.annotations.select_label("N")) == 87


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_unique_labels(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.annotations.unique_labels == ["N", "X"]


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01.ecg"])
def test_subject_info(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.info.race == 0
