import difflib
import os
import shutil
import time

import pytest

from pyecg import ECGDataset
from pyecg import ECGRecord


@pytest.mark.parametrize("dataset_dir", ["tests/empty_dataset"])
def test_empty(dataset_dir):
    with pytest.raises(FileNotFoundError):
        ECGDataset.from_dir(dataset_dir=dataset_dir)


@pytest.mark.parametrize("dataset_dir", ["tests/nonexistent"])
def test_not_exist(dataset_dir):
    with pytest.raises(FileNotFoundError):
        ECGDataset.from_dir(dataset_dir=dataset_dir)


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_dataset_name(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    assert dataset.dataset_name == dataset_name


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_dataset_dir(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    assert dataset.dataset_dir == dataset_dir


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_dataset_dir_overwrite_notfound(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    with pytest.raises(FileNotFoundError):
        dataset.dataset_dir = "test/nonexistent"


@pytest.mark.parametrize("dataset_dir,dataset_name,new_dir", [("tests/dataset_1",
                                                               "dataset_1",
                                                               "tests/wfdb_dataset_0"),
                                                              ("tests/wfdb_dataset_0",
                                                               "wfdb_dataset_0",
                                                               "tests/dataset_1")])
def test_dataset_dir_overwrite(dataset_dir, dataset_name, new_dir):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    dataset.dataset_dir = new_dir
    assert dataset.dataset_dir == new_dir


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_split_ratio_greater_than_one(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    with pytest.raises(ValueError):
        dataset.split_dataset(["train", "dev", "test"], 0.8, 0.3)


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_split_ratio_valid(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    dataset.split_dataset(["train", "dev", "test"], 0.8, 0.1)
    dataset.split_dataset(["train", "dev", "test"], 0.8, 0.2)


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_split_name(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    train_set, dev_set, test_set = dataset.split_dataset(["train", "dev", "test"], 0.8, 0.1)
    assert train_set.dataset_name == "train"
    assert dev_set.dataset_name == "dev"
    assert test_set.dataset_name == "test"


@pytest.mark.parametrize("dataset_dir,dataset_name", [("tests/dataset_1", "dataset_1"),
                                                      ("tests/wfdb_dataset_0", "wfdb_dataset_0")])
def test_split_name_mismatch(dataset_dir, dataset_name):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    with pytest.raises(ValueError):
        dataset.split_dataset(["train", "dev"], 0.8, 0.1)
    with pytest.raises(ValueError):
        dataset.split_dataset(["train", "dev", "dev-test", "test"], 0.8, 0.1)


@pytest.mark.parametrize("dataset_dir,length", [("tests/dataset_1", 3),
                                                ("tests/wfdb_dataset_0", 2)])
def test_length(dataset_dir, length):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    assert len(dataset) == length


@pytest.mark.parametrize("dataset_dir,length", [("tests/dataset_1", 3),
                                                ("tests/wfdb_dataset_0", 2)])
def test_length_record(dataset_dir, length):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    assert len(dataset.records) == length


@pytest.mark.parametrize("dataset_dir,repr_str",
                         [("tests/dataset_1", "Dataset with records\n100.hea\n101.hea\nECG_P28.01.ecg"),
                          ("tests/wfdb_dataset_0", "Dataset with records\n100.hea\n101.hea")])
def test_repr(dataset_dir, repr_str):
    dataset = ECGDataset.from_dir(dataset_dir=dataset_dir)
    assert str(dataset) == repr_str


def test_split_1():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    train_set, dev_set, test_set = dataset.split_dataset(["train", "dev", "test"], 0.8, 0.1)
    assert str(dataset) == "Dataset with records\n100.hea\n101.hea\nECG_P28.01.ecg"
    assert str(train_set) == "Dataset with records\n100.hea\n101.hea"
    assert str(dev_set) == "Dataset with records\n"
    assert str(test_set) == "Dataset with records\nECG_P28.01.ecg"


def test_save_csv():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    dataset.save_csv("tests/output/transient/dataset_1.csv")
    assert os.path.isfile("tests/output/transient/dataset_1.csv")
    shutil.rmtree("tests/output/transient")


def test_save_csv_autoname():
    dataset = ECGDataset.from_dir(dataset_dir="tests/wfdb_dataset_0")
    dataset.save_csv("tests/output/transient")
    import time
    time.sleep(1)
    assert os.path.isfile("tests/output/transient/wfdb_dataset_0_records.csv")
    shutil.rmtree("tests/output/transient")


def test_csv_content():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    dataset.save_csv("tests/output/dataset_1.csv")
    with open("tests/output/dataset_1.csv", "r") as fptr:
        candidate_csv_text = fptr.read()
    with open("tests/dataset_1.csv", "r") as fptr:
        golden_csv_text = fptr.read()
    diffInstance = difflib.Differ()
    diffList = diffInstance.compare(candidate_csv_text, golden_csv_text)
    assert all([d[0] == " " for d in diffList])


def test_bad_pickle():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    with pytest.raises(ValueError):
        dataset.to_pickle("tests/output/transient/dataset_1.pickle1")


def test_save_pickle():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    dataset.to_pickle("tests/output/transient/dataset_1.pickle")
    assert os.path.isfile("tests/output/transient/dataset_1.pickle")
    shutil.rmtree("tests/output/transient")


def test_save_pickle_no_extension():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    dataset.to_pickle("tests/output/transient")
    assert os.path.isfile("tests/output/transient/dataset_1.pickle")
    shutil.rmtree("tests/output/transient")


def test_load_pickle():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    dataset.to_pickle("tests/output/transient/dataset_1.pickle")
    dataset_loaded = dataset.from_pickle("tests/output/transient/dataset_1.pickle")
    assert dataset_loaded == dataset
    shutil.rmtree("tests/output/transient")


def test_slicing():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    assert dataset[0:1] == [ECGRecord.from_wfdb("tests/wfdb/100.hea")]


def test_slicing_single_element():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    assert dataset[1] == ECGRecord.from_wfdb("tests/dataset_1/101.hea")


def test_select_lead():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1", selected_leads=["MLII", "II"])
    for record in dataset.records:
        assert record.n_sig == 1


def test_record_content():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    for i in range(10):
        start = time.time()
        record_100 = dataset[0]
        record_101 = dataset[1]
        record_ecg_p28 = dataset[2]
        assert record_100.record_name == "100"
        assert record_101.record_name == "101"
        assert record_ecg_p28.record_name == "ECG_P28.01"
        end = time.time()
        print(end - start)


def test_record_length():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    record_length = dataset.sig_len
    assert record_length == [650000, 650000, 95573]


def test_record_duration():
    dataset = ECGDataset.from_dir(dataset_dir="tests/dataset_1")
    record_duration = dataset.duration
    assert record_duration == [1805.5527777777777, 1805.5527777777777, 95.572]
