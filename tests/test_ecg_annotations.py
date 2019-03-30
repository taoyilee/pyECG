from pyecg.annotations import ECGAnnotation, ECGAnnotationSample


def test_length():
    annotation = ECGAnnotation([ECGAnnotationSample("N", 1),
                                ECGAnnotationSample("N", 5),
                                ECGAnnotationSample("N", 4),
                                ECGAnnotationSample("N", 6)])
    assert len(annotation) == 4


def test_concat():
    annotation1 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    annotation2 = ECGAnnotation([ECGAnnotationSample("A", 10),
                                 ECGAnnotationSample("X", 3),
                                 ECGAnnotationSample("C", 62),
                                 ECGAnnotationSample("D", 84)])
    annotation3 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6),
                                 ECGAnnotationSample("A", 10),
                                 ECGAnnotationSample("X", 3),
                                 ECGAnnotationSample("C", 62),
                                 ECGAnnotationSample("D", 84)])
    assert annotation1 + annotation2 == annotation3


def test_equality():
    annotation1 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    annotation2 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    assert annotation1 == annotation2


def test_inequality_0():
    annotation1 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    annotation2 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 8),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    assert annotation1 != annotation2


def test_inequality_1():
    annotation1 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 5),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    annotation2 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    assert annotation1 != annotation2


def test_inequality_2():
    annotation1 = ECGAnnotation([])
    annotation2 = ECGAnnotation([ECGAnnotationSample("N", 1),
                                 ECGAnnotationSample("N", 4),
                                 ECGAnnotationSample("N", 6)])
    assert annotation1 != annotation2
