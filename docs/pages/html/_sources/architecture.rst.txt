.. _architecture:

========================
Architecture & Internals
========================

This page explains how pyperl is structured and what happens under the hood
when you call ``pyperl()`` and ``perl.run()``.


Initialisation flow
-------------------

When you construct a ``pyperl`` instance, the following steps happen in order:

.. code-block:: text

   pyperl.__init__()
   │
   ├── 1. set_logger(verbose)          — configure log level
   ├── 2. determine_OS()               — detect platform, set archive URL / filename
   ├── 3. set_archive_dir(...)         — locate or set the Perl archive directory
   ├── 4. get_script_location(script)  — resolve and validate the Perl script path
   └── 5. install_perl(...)            — find or install Perl
           │
           ├── ensure_perl()           — check PATH and common directories
           │       └── find_perl()     — recursive search within a directory
           │
           └── (if not found)
               ├── Download archive from URL (via wget.download)
               ├── Extract ZIP (Windows) or TAR.GZ (Linux/macOS)
               └── ensure_perl()       — locate the newly extracted executable


Perl resolution order
---------------------

``ensure_perl()`` searches for Perl in this priority order:

1. ``shutil.which("perl")`` — already on the system ``PATH``.
2. ``installation_dir`` — the configured portable install location.
3. ``perl_search_dirs`` — any extra directories you supplied.
4. Standard system paths:

   - ``/usr/bin``
   - ``/usr/local/bin``
   - ``/opt/homebrew/bin`` (macOS Homebrew)
   - ``C:\Strawberry\perl\bin`` (Windows)
   - ``C:\Perl\bin`` (Windows)

If Perl is not found in any of these locations, ``install_perl()`` downloads and
extracts the portable package.


Script execution flow
---------------------

Calling ``perl.run(*args, script, timeout)`` does the following:

.. code-block:: text

   run()
   │
   ├── Validate perl_path is set
   ├── Resolve script path (override or default)
   ├── Build subprocess command:
   │       [perl_path, script_path, *args]
   ├── subprocess.run(..., capture_output=True, timeout=timeout)
   ├── Check returncode — raise RuntimeError on non-zero
   └── Return {"stdout": ..., "stderr": ..., "returncode": ...}


Module structure
----------------

.. code-block:: text

   pyperl/
   ├── pyperl.py          ← main module (all classes and functions)
   ├── perl_packages/     ← optional bundled Perl archives (offline use)
   │   ├── strawberry-perl-*.zip        (Windows)
   │   └── perl-5.x.x.tar.gz           (Linux/macOS)
   ├── perl_scripts/      ← default Perl scripts shipped with the library
   │   └── convert_audio.pl
   └── data/
       └── example.wav    ← bundled example audio file


Key classes and functions
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Name
     - Role
   * - ``pyperl`` (class)
     - Main interface. Manages Perl installation and script execution.
   * - ``wget`` (class)
     - Thin download helper. Uses ``requests`` to stream files to disk.
   * - ``find_perl(start_dir)``
     - Recursive filesystem walker that locates a Perl binary.
   * - ``get_base_dir()``
     - Returns the package root, handling PyInstaller/cx_Freeze frozen paths.
   * - ``set_logger(verbose)``
     - Configures the ``"pyperl"`` logger level.


Platform-specific archive handling
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 15 20 30 35

   * - Platform
     - Archive type
     - Source
     - Extraction
   * - Windows
     - ZIP
     - Strawberry Perl GitHub releases
     - ``zipfile.ZipFile.extractall()``
   * - Linux / macOS
     - TAR.GZ
     - CPAN (perl.org)
     - ``tarfile.open().extractall()``


Frozen executable support
--------------------------

pyperl uses ``sys._MEIPASS`` to locate bundled assets when running inside a
frozen executable created by PyInstaller or cx_Freeze:

.. code-block:: python

   def get_base_dir():
       if getattr(sys, "frozen", False):
           return Path(sys._MEIPASS)
       return Path(__file__).resolve().parent

This ensures that ``perl_packages/``, ``perl_scripts/``, and ``data/`` are
found correctly in both development and packaged deployments.


.. include:: add_bottom.add