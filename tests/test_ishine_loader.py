import pytest

from pyecg import ECGRecord


@pytest.mark.parametrize("ecg_path", ["tests/wfdb/nonexistent", "tests/wfdb/nonexistent.hea"])
def test_file_notfound(ecg_path):
    with pytest.raises(FileNotFoundError):
        ECGRecord.from_ishine(ecg_path)


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01", "tests/ishine/ECG_P28.01.ecg"])
def test_length(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert len(record) == 650000


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01", "tests/ishine/ECG_P28.01.ecg"])
def test_signal(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.n_sig == 2


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01", "tests/ishine/ECG_P28.01.ecg"])
def test_record_name(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.name == "100"


@pytest.mark.parametrize("ecg_path", ["tests/ishine/ECG_P28.01", "tests/ishine/ECG_P28.01.ecg"])
def test_signal_name(ecg_path):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.lead_names == ['MLII', 'V5']


@pytest.mark.parametrize("ecg_path,lead_name,signal", [("tests/ishine/ECG_P28.01",
                                                        "MLII",
                                                        [-0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145,
                                                         -0.12, -0.135]),
                                                       ("tests/ishine/ECG_P28.01.ecg",
                                                        "V5",
                                                        [-0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065,
                                                         -0.08, -0.08])])
def test_signal_content(ecg_path, lead_name, signal):
    record = ECGRecord.from_ishine(ecg_path)
    assert record.get_lead(lead_name)[:10] == signal
