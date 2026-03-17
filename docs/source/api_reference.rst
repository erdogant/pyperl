.. _api_reference:

=============
API Reference
=============

This page documents every public class and function in pyperl.

.. contents:: On this page
   :local:
   :depth: 2


pyperl class
============

.. autoclass:: pyperl.pyperl
   :members:
   :undoc-members:
   :show-inheritance:


Constructor
-----------

.. code-block:: python

   pyperl(
       script="perl_scripts/convert_audio.pl",
       installation_dir=None,
       set_to_path=False,
       perl_search_dirs=None,
       force_install=False,
       verbose="info",
   )

.. list-table::
   :header-rows: 1
   :widths: 22 12 18 48

   * - Parameter
     - Type
     - Default
     - Description
   * - ``script``
     - ``str``
     - ``"perl_scripts/convert_audio.pl"``
     - Path to the Perl script (relative to the package root or absolute).
       Set to ``None`` to skip script validation at initialisation time.
   * - ``installation_dir``
     - ``str`` or ``None``
     - ``None``
     - Directory where portable Perl will be installed. When ``None`` the
       system temporary directory (``%TEMP%`` / ``/tmp``) is used.
   * - ``set_to_path``
     - ``bool``
     - ``False``
     - When ``True``, the directory containing the Perl executable is
       prepended to ``os.environ["PATH"]`` so that Perl is available
       process-wide for the rest of the session.
   * - ``perl_search_dirs``
     - ``list`` or ``None``
     - ``None``
     - Extra directories to search for an existing Perl executable before
       falling back to a portable install. Searched in order, after the
       system PATH but before the default system locations.
   * - ``force_install``
     - ``bool``
     - ``False``
     - When ``True``, any previously installed portable Perl is deleted and
       re-extracted from the archive. Useful for repairing a broken install.
   * - ``verbose``
     - ``str``
     - ``"info"``
     - Controls log verbosity. Accepted values:
       ``"silent"``, ``"debug"``, ``"info"``, ``"warning"``,
       ``"error"``, ``"critical"``.


pyperl.run()
------------

Execute a Perl script and return its output.

.. code-block:: python

   result = perl.run(*args, script=None, timeout=300)

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 20 12 15 53

   * - Parameter
     - Type
     - Default
     - Description
   * - ``*args``
     - ``str``
     - —
     - Zero or more positional arguments forwarded to the Perl script on
       the command line (e.g. input path, output path, flags).
   * - ``script``
     - ``str`` or ``None``
     - ``None``
     - Override the script to run for this call only. If ``None``, the
       script set during initialisation is used.
   * - ``timeout``
     - ``int``
     - ``300``
     - Maximum allowed runtime in seconds. A ``RuntimeError`` is raised
       if the script exceeds this limit.

**Returns**

A ``dict`` with the following keys:

.. list-table::
   :header-rows: 1
   :widths: 20 12 68

   * - Key
     - Type
     - Description
   * - ``"stdout"``
     - ``str``
     - Everything the Perl script wrote to standard output.
   * - ``"stderr"``
     - ``str``
     - Everything written to standard error (warnings, diagnostics).
   * - ``"returncode"``
     - ``int``
     - Exit code. ``0`` = success. Non-zero values indicate an error.

**Raises**

- ``RuntimeError`` — Perl executable not found.
- ``RuntimeError`` — Script exits with a non-zero return code.
- ``RuntimeError`` — Script execution exceeds ``timeout`` seconds.


pyperl.install_perl()
----------------------

.. automethod:: pyperl.pyperl.install_perl


pyperl.ensure_perl()
---------------------

.. automethod:: pyperl.pyperl.ensure_perl


pyperl.get_script_location()
-----------------------------

.. automethod:: pyperl.pyperl.get_script_location


pyperl.clean_installation_dir()
--------------------------------

Delete the portable Perl installation directory. Useful for automated cleanup
or before a forced reinstall.

.. code-block:: python

   perl.clean_installation_dir()


pyperl.import_example()
------------------------

Return the path to the bundled example ``.wav`` audio file included with pyperl.

.. code-block:: python

   audio_path = perl.import_example()
   # Returns: "<package_root>/data/example.wav"


Module-level functions
======================

get_base_dir()
--------------

.. autofunction:: pyperl.get_base_dir

Returns the root directory of the pyperl package. Works correctly in both
normal Python environments and frozen executables (PyInstaller, cx_Freeze).


find_perl()
-----------

.. autofunction:: pyperl.find_perl

Recursively walks ``start_dir`` looking for a Perl executable
(``perl`` on Linux/macOS, ``perl.exe`` on Windows).

**Parameters**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``start_dir``
     - ``pathlib.Path``
     - Root directory for the recursive search.

**Returns** ``pathlib.Path`` or ``None``.


set_logger()
------------

.. autofunction:: pyperl.set_logger

Configure the ``"pyperl"`` logger verbosity at any point in your code.

.. code-block:: python

   from pyperl import set_logger

   set_logger("debug")   # enable full debug output
   set_logger("silent")  # suppress all output

Accepted levels: ``"silent"``, ``"debug"``, ``"info"``, ``"warning"``, ``"error"``, ``"critical"``.


wget class
==========

Internal helper used to download portable Perl archives. Not intended for
direct use but documented here for completeness.

.. autoclass:: pyperl.wget
   :members:


Instance attributes
===================

After initialisation, the following attributes are available on a ``pyperl`` instance:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``perl.perl_path``
     - Absolute path to the Perl executable as a string, or ``None`` if Perl
       could not be found or installed.
   * - ``perl.script``
     - ``pathlib.Path`` to the default Perl script, or ``None``.
   * - ``perl.installation_dir``
     - ``pathlib.Path`` to the portable Perl installation directory.
   * - ``perl.archive_path``
     - ``pathlib.Path`` to the portable Perl archive file.
   * - ``perl.archive_filename``
     - Filename of the Perl archive (platform-specific).
   * - ``perl.archive_type``
     - ``"zip"`` (Windows) or ``"tar"`` (Linux/macOS).
   * - ``perl.url``
     - URL from which the portable Perl archive is downloaded if not found locally.


.. include:: add_bottom.add