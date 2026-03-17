.. _contributing:

============
Contributing
============

Contributions are very welcome! Whether it's a bug fix, a new feature, improved
documentation, or a new example — all pull requests are appreciated.


Getting started
---------------

1. Fork the repository on `GitHub <https://github.com/erdogant/pyperl>`_.
2. Clone your fork and create a feature branch:

   .. code-block:: console

      git clone https://github.com/<your-username>/pyperl.git
      cd pyperl
      git checkout -b my-feature

3. Install the package in editable mode with development dependencies:

   .. code-block:: console

      pip install -e ".[dev]"

4. Make your changes, add tests, and update documentation as needed.
5. Push and open a pull request against the ``main`` branch.


Running the tests
-----------------

.. code-block:: console

   pytest tests/

Please ensure all tests pass before submitting a pull request.


Adding examples
---------------

Examples in ``pyperl.py`` follow the ``# [example_name]`` / ``# [/example_name]``
marker convention so they can be included directly in the RST documentation via
``literalinclude``. When adding a new example function:

1. Add a named function at the bottom of ``pyperl.py`` wrapped in the marker comments.
2. Add a corresponding ``.. literalinclude::`` block in ``docs/examples.rst``.
3. Reference the example from ``quickstart.rst`` or ``usage.rst`` if relevant.


Code style
----------

- Follow `PEP 8 <https://peps.python.org/pep-0008/>`_.
- Use NumPy-style docstrings for all public functions and methods.
- Keep functions small and focused.


Reporting bugs
--------------

Open an issue on `GitHub <https://github.com/erdogant/pyperl/issues>`_ with:

- A minimal reproducible example
- Your OS and Python version
- The full traceback
- Output of ``pyperl(verbose="debug")``


.. include:: add_bottom.add