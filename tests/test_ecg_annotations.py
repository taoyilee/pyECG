import copy

from pyecg.annotations import ECGAnnotation, ECGAnnotationSample

annotation1 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                             ECGAnnotationSample(4, "N"),
                             ECGAnnotationSample(5, "N"),
                             ECGAnnotationSample(6, "N")])

annotation_random = ECGAnnotation([ECGAnnotationSample(6, "N"),
                                   ECGAnnotationSample(5, "N"),
                                   ECGAnnotationSample(1, "N"),
                                   ECGAnnotationSample(4, "N")])

annotation_label = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                  ECGAnnotationSample(3, "X"),
                                  ECGAnnotationSample(4, "A"),
                                  ECGAnnotationSample(5, "B")])

annotation_label_shuffle = ECGAnnotation([ECGAnnotationSample(4, "A"),
                                          ECGAnnotationSample(5, "B"),
                                          ECGAnnotationSample(0, "N"),
                                          ECGAnnotationSample(3, "X")])


def test_auto_sort():
    assert annotation_random == annotation1


def test_length():
    assert len(annotation1) == 4


def test_concat():
    annotation2 = ECGAnnotation([ECGAnnotationSample(10, "A"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(62, "C"),
                                 ECGAnnotationSample(84, "D")])
    annotation3 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(5, "N"),
                                 ECGAnnotationSample(6, "N"),
                                 ECGAnnotationSample(10, "A"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(62, "C"),
                                 ECGAnnotationSample(84, "D")])
    assert annotation1 + annotation2 == annotation3


def test_max_index():
    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(5, "N")])
    assert annotation2.max_index == 6
    annotation2.max_index = 3
    assert annotation2.max_index == 3


def test_annotation_shape():
    annotation2 = ECGAnnotation([ECGAnnotationSample(-3, "A"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    assert annotation2.stem_label("N").shape == (6,)


def test_stem_labell():
    annotation2 = ECGAnnotation([ECGAnnotationSample(-3, "A"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    assert annotation2.stem_label("N").tolist() == [False, False, False, False, False, False]
    assert annotation2.stem_label("X").tolist() == [False, False, False, True, False, False]
    assert annotation2.stem_label("A").tolist() == [True, False, False, False, True, False]
    assert annotation2.stem_label("B").tolist() == [False, False, False, False, False, True]

    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    assert annotation2.stem_label("N").tolist() == [True, False, False, False, False, False]
    assert annotation2.stem_label("X").tolist() == [False, False, False, True, False, False]
    assert annotation2.stem_label("A").tolist() == [False, False, False, False, True, False]
    assert annotation2.stem_label("B").tolist() == [False, False, False, False, False, True]

    annotation2.max_index = 3
    assert annotation2.stem_label("X").tolist() == [False, False, True]
    assert annotation2.stem_label("N").tolist() == [True, False, False]
    assert annotation2.stem_label("A").tolist() == [False, False, False]
    assert annotation2.stem_label("B").tolist() == [False, False, False]

    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "N"),
                                 ECGAnnotationSample(8, "N"),
                                 ECGAnnotationSample(9, "N"),
                                 ECGAnnotationSample(10, "B")])
    assert annotation2.stem_label("N").tolist() == [True, False, False, False, False, True, False, False, True, True,
                                                    False]
    assert annotation2.stem_label("X").tolist() == [False, False, False, True, False, False, False, False, False, False,
                                                    False]
    assert annotation2.stem_label("A").tolist() == [False, False, False, False, True, False, False, False, False, False,
                                                    False]
    assert annotation2.stem_label("B").tolist() == [False, False, False, False, False, False, False, False, False,
                                                    False,
                                                    True]


def test_get_right_label():
    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    annotation2.max_index = 3
    assert annotation2.right_label == "X"

    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    annotation2.max_index = 4
    assert annotation2.right_label == "A"

    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    annotation2.max_index = 5
    assert annotation2.right_label == "B"


def test_get_left_label():
    annotation2 = ECGAnnotation([ECGAnnotationSample(-3, "A"),
                                 ECGAnnotationSample(3, "X"),
                                 ECGAnnotationSample(4, "A"),
                                 ECGAnnotationSample(5, "B")])
    assert annotation2.left_label == "A"

    annotation_label_1 = copy.copy(annotation_label)
    annotation_label_1 = annotation_label_1.shift(-2)
    assert annotation_label_1.left_label == "N"

    annotation_label_1 = copy.copy(annotation_label)
    annotation_label_1 = annotation_label_1.shift(-3)
    assert annotation_label_1.left_label == "X"

    annotation_label_1 = copy.copy(annotation_label)
    annotation_label_1 = annotation_label_1.shift(-4)
    assert annotation_label_1.left_label == "A"

    annotation_label_1 = copy.copy(annotation_label)
    annotation_label_1 = annotation_label_1.shift(-5)
    assert annotation_label_1.left_label == "B"

    annotation_label_1 = copy.copy(annotation_label_shuffle)
    annotation_label_1 = annotation_label_1.shift(-2)
    assert annotation_label_1.left_label == "N"

    annotation_label_1 = copy.copy(annotation_label_shuffle)
    annotation_label_1 = annotation_label_1.shift(-3)
    assert annotation_label_1.left_label == "X"

    annotation_label_1 = copy.copy(annotation_label_shuffle)
    annotation_label_1 = annotation_label_1.shift(-4)
    assert annotation_label_1.left_label == "A"

    annotation_label_1 = copy.copy(annotation_label_shuffle)
    annotation_label_1 = annotation_label_1.shift(-5)
    assert annotation_label_1.left_label == "B"


def test_shift_neg():
    annotation1_shift = annotation1.shift(-1)
    annotation2 = ECGAnnotation([ECGAnnotationSample(0, "N"),
                                 ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(5, "N")])
    assert annotation1_shift == annotation2


def test_shift_pos():
    annotation1_shift = annotation1.shift(2)
    annotation2 = ECGAnnotation([ECGAnnotationSample(3, "N"),
                                 ECGAnnotationSample(6, "N"),
                                 ECGAnnotationSample(7, "N"),
                                 ECGAnnotationSample(8, "N")])
    assert annotation1_shift == annotation2


def test_equality():
    annotation2 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(5, "N"),
                                 ECGAnnotationSample(6, "N")])
    assert annotation1 == annotation2


def test_inequality_0():
    annotation2 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(8, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(6, "N")])
    assert annotation1 != annotation2


def test_inequality_1():
    annotation2 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(6, "N")])
    assert annotation1 != annotation2


def test_inequality_2():
    annotation1 = ECGAnnotation([])
    annotation2 = ECGAnnotation([ECGAnnotationSample(1, "N"),
                                 ECGAnnotationSample(4, "N"),
                                 ECGAnnotationSample(6, "N")])
    assert annotation1 != annotation2
