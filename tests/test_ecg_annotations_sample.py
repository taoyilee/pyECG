from pyecg.annotations import ECGAnnotationSample


def test_equality():
    annotation1 = ECGAnnotationSample(1, "N")
    annotation2 = ECGAnnotationSample(1, "N")
    assert annotation1 == annotation2


def test_inequality_0():
    annotation1 = ECGAnnotationSample(1, "A")
    annotation2 = ECGAnnotationSample(1, "N")
    assert annotation1 != annotation2


def test_inequality_1():
    annotation1 = ECGAnnotationSample(1, "N")
    annotation2 = ECGAnnotationSample(2, "N")
    assert annotation1 != annotation2


def test_inequality_2():
    annotation1 = ECGAnnotationSample(1, "A")
    annotation2 = ECGAnnotationSample(2, "N")
    assert annotation1 != annotation2
