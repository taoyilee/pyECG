import pytest

from pyecg import RecordTicket


@pytest.mark.parametrize("hea_path", ["tests/wfdb/nonexistent", "tests/wfdb/nonexistent.hea"])
def test_file_notfound(hea_path):
    with pytest.raises(FileNotFoundError):
        ticket = RecordTicket(hea_path)
        ticket()


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_length(hea_path):
    record = RecordTicket(hea_path)
    assert len(record()) == 650000


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_signal(hea_path):
    record = RecordTicket(hea_path)
    assert record().n_sig == 2


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_record_name(hea_path):
    record = RecordTicket(hea_path)
    assert record().record_name == "100"


@pytest.mark.parametrize("hea_path", ["tests/wfdb/100", "tests/wfdb/100.hea"])
def test_signal_name(hea_path):
    record = RecordTicket(hea_path)
    assert record().lead_names == ['MLII', 'V5']


@pytest.mark.parametrize("hea_path,lead_name,signal", [("tests/wfdb/100",
                                                        "MLII",
                                                        [-0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145, -0.145,
                                                         -0.12, -0.135]),
                                                       ("tests/wfdb/100",
                                                        "V5",
                                                        [-0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065, -0.065,
                                                         -0.08, -0.08])])
def test_signal_content(hea_path, lead_name, signal):
    record = RecordTicket(hea_path)
    assert record().get_lead(lead_name)[:10] == signal
