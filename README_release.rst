==========================
Releasing Procedures
==========================


.. code-block:: bash

    python setup.py sdist bdist_wheel
    twine check dist/*
    twine upload dist/*