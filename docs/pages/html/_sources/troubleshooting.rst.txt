.. _troubleshooting:

===============
Troubleshooting
===============

This page covers the most common errors and how to fix them.

.. contents:: On this page
   :local:
   :depth: 2


Perl not found after initialisation
-------------------------------------

**Symptom**

.. code-block:: text

   WARNING  pyperl:pyperl.py  Perl executable path not found.

**Cause**

Perl is not on the system ``PATH`` and was not found in any of the standard locations.

**Fix**

Tell pyperl where your Perl lives, or let it install a portable copy:

.. code-block:: python

   # Option A — supply the directory containing your perl binary
   perl = pyperl(perl_search_dirs=["/my/custom/perl/bin"])

   # Option B — let pyperl download and install a portable Perl
   perl = pyperl(installation_dir="/opt/my_perl")

   # Option C — force a fresh portable install
   perl = pyperl(force_install=True)


Portable Perl extraction failed
---------------------------------

**Symptom**

.. code-block:: text

   RuntimeError: Portable Perl extraction failed.

**Cause**

The archive was downloaded but the extracted ``perl`` / ``perl.exe`` binary could not be
located afterwards. This usually means the archive is corrupt or partially downloaded.

**Fix**

Force a clean reinstall — this deletes the installation directory and re-extracts:

.. code-block:: python

   perl = pyperl(force_install=True)

If the problem persists, delete the archive manually from the ``installation_dir``
(default: ``%TEMP%\perl_packages`` on Windows or ``/tmp/perl_packages`` elsewhere)
and run again so a fresh copy is downloaded.


Perl script not found
----------------------

**Symptom**

.. code-block:: text

   WARNING  pyperl:pyperl.py  Perl script not found: /path/to/my_script.pl

**Cause**

The ``script`` path passed to ``pyperl()`` does not exist relative to the package root.

**Fix**

Use an absolute path, or verify the relative path is correct:

.. code-block:: python

   import os

   perl = pyperl(script=os.path.abspath("perl_scripts/my_script.pl"))


RuntimeError: Perl script failed with return code N
-----------------------------------------------------

**Symptom**

.. code-block:: python

   RuntimeError: Perl script failed with return code 1

**Cause**

The Perl script itself exited with a non-zero status. The error details are in ``stderr``.

**Fix**

Catch the exception and log ``stderr`` before re-raising, or run with ``verbose="debug"``
to see the full error output:

.. code-block:: python

   perl = pyperl(script="my_script.pl", verbose="debug")

   try:
       result = perl.run("input.wav", "output.mp3")
   except RuntimeError as e:
       print("Script failed:", e)


RuntimeError: Perl script timed out
-------------------------------------

**Symptom**

.. code-block:: python

   RuntimeError: Perl script timed out

**Cause**

The script ran for longer than the ``timeout`` value (default: 300 seconds).

**Fix**

Increase the timeout or investigate why the script is slow:

.. code-block:: python

   result = perl.run("large_file.wav", "output.mp3", timeout=600)


PermissionError during extraction (Linux/macOS)
-------------------------------------------------

**Symptom**

.. code-block:: text

   PermissionError: [Errno 13] Permission denied: '/opt/my_perl/...'

**Cause**

The current user does not have write permission to ``installation_dir``.

**Fix**

Use a directory you own (e.g. a subdirectory of your home folder):

.. code-block:: python

   perl = pyperl(installation_dir="/home/myuser/.local/share/perl_packages")


No internet access / download fails
-------------------------------------

**Symptom**

.. code-block:: text

   WARNING  pyperl:pyperl.py  Portable perl zip not found: /tmp/perl_packages/strawberry-perl-...zip

**Cause**

pyperl cannot download the portable Perl archive because there is no internet access.

**Fix**

Download the archive manually on a machine with internet access and place it in
the ``perl_packages/`` directory inside the pyperl package root (or in your chosen
``installation_dir``):

- **Windows**: ``strawberry-perl-5.42.0.1-64bit-portable.zip``
- **Linux/macOS**: ``perl-5.42.1.tar.gz``

pyperl checks this location before attempting any download.


Enabling debug logging
-----------------------

For any issue not covered above, enable full debug logging to see every step:

.. code-block:: python

   from pyperl import pyperl

   perl = pyperl(script="my_script.pl", verbose="debug")
   result = perl.run()

This prints detailed information including the resolved Perl path, the exact
command built, and subprocess output.


Still stuck?
------------

Open an issue on `GitHub <https://github.com/erdogant/pyperl/issues>`_ and include:

- Your operating system and Python version
- The full traceback
- The output of ``perl = pyperl(verbose="debug")``


.. include:: add_bottom.add