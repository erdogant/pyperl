.. _usage:

====================
Cross-Platform Usage
====================

pyperl handles the platform-specific differences in Perl installation transparently.
This page explains what happens on each platform and how to configure pyperl for
advanced scenarios.


Platform behaviour at a glance
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Platform
     - Portable archive used
     - Default install location
   * - **Windows**
     - ``strawberry-perl-5.42.0.1-64bit-portable.zip``
     - ``%TEMP%\perl_packages``
   * - **Linux**
     - ``perl-5.42.1.tar.gz`` (CPAN source)
     - ``/tmp/perl_packages``
   * - **macOS**
     - ``perl-5.42.1.tar.gz`` (CPAN source)
     - ``/tmp/perl_packages``


Windows
-------

On Windows, pyperl uses `Strawberry Perl <https://strawberryperl.com/>`_ — a
self-contained portable ZIP that includes Perl, CPAN modules, and a C compiler.
No admin rights are required.

.. code-block:: python

   from pyperl import pyperl

   # Windows — Strawberry Perl is extracted to %TEMP%\perl_packages by default
   perl = pyperl(script="my_script.pl")
   result = perl.run("input.wav", "output.mp3")
   print(result["stdout"])

Common Windows Perl installation locations that pyperl searches automatically:

- ``C:\Strawberry\perl\bin``
- ``C:\Perl\bin``
- ``%TEMP%\perl_packages`` (pyperl portable install)


Linux & macOS
-------------

On Linux and macOS, pyperl first checks whether system Perl is already available
(most distributions ship with Perl pre-installed). If not found, it downloads the
Perl 5 source tarball from CPAN and extracts it.

.. code-block:: python

   from pyperl import pyperl

   perl = pyperl(script="my_script.pl")
   result = perl.run()
   print(result["stdout"])

System paths checked automatically:

- ``/usr/bin/perl``
- ``/usr/local/bin/perl``
- ``/opt/homebrew/bin/perl`` (macOS Homebrew)


Custom installation dir
------------------------------

To install portable Perl to a persistent location (instead of the temp directory),
pass ``installation_dir``. Combine with ``set_to_path=True`` to make Perl available
globally in the current process environment.

 .. code:: python    

    """Install portable Perl to a custom directory and expose it on PATH."""
    from pyperl import pyperl
     
    perl = pyperl(
        script="my_script.pl",
        installation_dir="/opt/my_perl",
        set_to_path=True,    # adds Perl bin dir to os.environ["PATH"]
        verbose="info",
    )
     
    result = perl.run()
    print(result["stdout"])


Searching additional directories
----------------------------------

If you have Perl installed in a non-standard location, tell pyperl where to look:

 .. code:: python    

    """Override the default script at run-time without re-initializing."""
    from pyperl import pyperl
     
    perl = pyperl()
     
    # Run a completely different script on the same Perl installation
    result = perl.run("arg1", "arg2", script="other_script.pl")
    print(result["stdout"])
     


Force re-install
-----------------

If your portable Perl installation becomes corrupt, use ``force_install=True`` to
wipe it and start fresh:

 .. code:: python    

    """Force a clean reinstall of portable Perl."""
    from pyperl import pyperl
     
    # Wipes any existing portable install and re-extracts from the archive
    perl = pyperl(
        script="my_script.pl",
        force_install=True,
    )
     
    result = perl.run()
    print(result["stdout"])


Bundled / offline environments
--------------------------------

pyperl checks for the archive file in the ``perl_packages/`` directory next to the
library *before* attempting a download. To prepare an offline bundle:

1. Download the appropriate archive manually.
2. Place it in ``<pyperl_package_root>/perl_packages/``.
3. Run normally — no internet connection is required.


PyInstaller / cx_Freeze support
---------------------------------

pyperl uses ``sys._MEIPASS`` to resolve its base directory when running inside a
frozen executable (PyInstaller or cx_Freeze). No additional configuration is needed —
the library path resolution is handled automatically via ``get_base_dir()``.

.. seealso::

   - :ref:`api_reference` — full parameter documentation
   - :ref:`troubleshooting` — common errors and fixes


.. include:: add_bottom.add