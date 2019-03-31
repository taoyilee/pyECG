import pytest

from pyecg import ECGRecord


@pytest.mark.parametrize("hea_path", ["tests/wfdb/nonexistent", "tests/wfdb/nonexistent.hea"])
def test_file_notfound(hea_path):
    with pytest.raises(FileNotFoundError):
        ECGRecord.from_wfdb(hea_path)


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_length(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert len(record) == 650000


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_signal(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert record.n_sig == 2


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_record_name(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert record.record_name == "100"


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_signal_name(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert record.lead_names == ['MLII', 'V5']


@pytest.mark.parametrize("hea_path,lead_name,signal", [("tests/wfdb/100",
                                                        "MLII",
                                                        [-0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145,
                                                         -0.12, -0.135]),
                                                       ("tests/wfdb/100",
                                                        "V5",
                                                        [-0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065,
                                                         -0.08, -0.08])])
def test_signal_content(hea_path, lead_name, signal):
    record = ECGRecord.from_wfdb(hea_path)
    assert record.get_lead(lead_name)[:10] == signal


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100"])
def test_annotation(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert len(record.annotations) == 2274


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100"])
def test_select_annotation(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert len(record.annotations.select_label("N")) == 2239


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100"])
def test_unique_labels(hea_path):
    record = ECGRecord.from_wfdb(hea_path)
    assert record.annotations.unique_labels == ['+', 'A', 'N', 'V']


@pytest.mark.parametrize("hea_path, lead_names, n_lead",
                         [("tests/wfdb/100.hea", ["MLII"], 1),
                          ("tests/wfdb/100.hea", ["V5"], 1),
                          ("tests/wfdb/100.hea", ["MLII", "V5"], 2)])
def test_record_select_lead(hea_path, lead_names, n_lead):
    record = ECGRecord.from_wfdb(hea_path, selected_leads=lead_names)
    assert record.n_sig == n_lead
