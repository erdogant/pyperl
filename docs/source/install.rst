.. _install:

============
Installation
============

Requirements
------------

- Python **3.12** or higher
- Internet access for the first run (to download portable Perl if not found on the system)

.. note::

   pyperl ships with bundled Perl archives so it can also work in **offline or restricted environments**
   — as long as the archive is present in the ``perl_packages/`` directory alongside the library.


Install from PyPI
-----------------

The recommended way to install pyperl is directly from PyPI:

.. code-block:: console

   pip install pyperl


Install from GitHub source
--------------------------

To get the very latest development version:

.. code-block:: console

   pip install git+https://github.com/erdogant/pyperl


Install in a virtual environment (recommended)
----------------------------------------------

.. code-block:: console

   python -m venv .venv
   source .venv/bin/activate      
   
   # Windows: 
   .venv\Scripts\activate
   

Verify the installation
-----------------------

.. code-block:: python

   import pyperl
   print(pyperl.__version__)



Dependencies
------------

pyperl depends only on the Python standard library plus ``requests`` for downloading
portable Perl archives when required.  All dependencies are declared in ``requirements.txt``
and installed automatically by ``pip``.


Bundled Perl archives (offline use)
------------------------------------
 
If you need pyperl to work without internet access, place the appropriate archive
in the ``perl_packages/`` directory inside the pyperl package root before first use:

- **Windows**: ``strawberry-perl-5.42.0.1-64bit-portable.zip``
- **Linux / macOS**: ``perl-5.42.1.tar.gz``

pyperl checks this directory first before attempting a download.


.. include:: add_bottom.add