from pyecg.annotations import ECGAnnotationSample


def test_equality():
    annotation1 = ECGAnnotationSample("N", 1)
    annotation2 = ECGAnnotationSample("N", 1)
    assert annotation1 == annotation2


def test_inequality_0():
    annotation1 = ECGAnnotationSample("A", 1)
    annotation2 = ECGAnnotationSample("N", 1)
    assert annotation1 != annotation2


def test_inequality_1():
    annotation1 = ECGAnnotationSample("N", 1)
    annotation2 = ECGAnnotationSample("N", 2)
    assert annotation1 != annotation2


def test_inequality_2():
    annotation1 = ECGAnnotationSample("A", 1)
    annotation2 = ECGAnnotationSample("N", 2)
    assert annotation1 != annotation2
