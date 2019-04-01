===============
Changelog
===============

Version 0.0.1
===============
- Definition of basic destructures
- Read / Write physiobank datasets (\*.hea/\*.dat)

Version 0.0.2
===============
- Read / Write physiobank datasets (\*.hea/\*.dat)


Version 0.0.3
===============
- Read / Write ishine datasets (\*.ecg/\*.ann)


Version 0.0.4
===============
- Add support of annotation files for WFDB/iShine

Version 0.0.5
===============
- Add a new class ECGDataset to support full dataset manipulation

Version 0.0.6
===============
- Add support for lead selection on dataset loading

Version 0.0.7
===============
- Disable import validation for iShine DB. Use metadata to retrieve record length

Version 0.0.8
===============
- Add multithread support to speed up loading

Version 0.0.8.1
===============
- Add duration and fs properties to RecordTicket and allows Dataset to query durations directly


Version 0.0.8.2
===============
- Add record_name property to RecordTicket
- Return output file name in to_csv() and to_pickle() methods



Version 0.0.8.2
===============
- Use metadata to speed up dataset processing

