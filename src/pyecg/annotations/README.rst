============================
Annotation Module
============================


iShine annotation specifications
======================================

Original documentation of ishine annotation format can be found `here <http://thew-project.org/papers/ishneAnn.pdf>`_.

The annotation file will have a header, exactly the same as the ISHNE header, in this way the two files:

1. ISHNE binary waveforms file
2. binary annotation segment file

will always be linked.

Also, using the ISHNE header will facilitate analyses requiring *only* the annotation file (for example HRV), as the user will be able to
obtain information related to the original ECG ( nb leads, sample freq..).

Following the header and the first annotation position, each annotation segment will consist of a 4-bytes binary data structure organized as
follows:

1. Label 1 [char]: beat annotation
2. Label 2 [char]: internal use (for example for further beat description)
3. toc (delta Sample): digital samples from last beat annotation [unsigned int]

+--------+------------+
|Label 1 | Label 2    |
+--------+------------+
|Toc                  |
+--------+------------+

Label 1: generic beat label short list

+--------+--------------------------------------------+
| N      |  Normal beat                               |
+--------+--------------------------------------------+
| V      |  Premature ventricular contraction         |
+--------+--------------------------------------------+
| S      | Supraventricular premature or ectopic beat |
+--------+--------------------------------------------+
| C      |     Calibration Pulse                      |
+--------+--------------------------------------------+
| B      | Bundle branch block beat                   |
+--------+--------------------------------------------+
| P      | Pace                                       |
+--------+--------------------------------------------+
| X      |  Artefact                                  |
+--------+--------------------------------------------+
| !      |  Timeout                                   |
+--------+--------------------------------------------+
| U      |  Unknown                                   |
+--------+--------------------------------------------+

The Timeout label is only used when the sample from last annotation is higher than the maximum number that can be expressed by an unsigned int, i.e. when it is larger
than 65535.
In this scenario the following annotation will be present in the file :

+--------+------------+
|   !    | ...\.\.    |
+--------+------------+
| 65535               |
+--------+------------+