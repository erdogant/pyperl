.. _quickstart:

=============
Quick Start
=============

This page shows the most common pyperl usage patterns. All code snippets below
are sourced directly from the :ref:`examples section <examples>` of ``pyperl.py``.


1 — Basic usage
---------------

The simplest way to use pyperl is to initialize it with the path to your Perl script.
pyperl will automatically detect or install Perl for you.

.. code:: python    
    
    """Basic initialization and script execution."""
    from pyperl import pyperl
     
    # Initialize — auto-detects or installs Perl
    perl = pyperl(script="my_script.pl")
     
    # Run the default Perl script
    result = perl.run()
     
    print(result["stdout"])
    print(result["returncode"])  # 0 = success

2 — Run a script with arguments
---------------------------------

Pass any number of positional arguments to your Perl script. They are forwarded
verbatim as command-line arguments.

.. code:: python    

    """Run a Perl script with positional arguments."""
    from pyperl import pyperl
     
    perl = pyperl(script="perl_scripts/convert_audio.pl")
     
    # Pass positional arguments directly to the Perl script
    result = perl.run("input.wav", "output.mp3")
     
    print(result["stdout"])
    print(result["returncode"])  # 0 = success


3 — Inspect the result
------------------------

``run()`` always returns a plain dictionary — convenient for downstream processing,
logging, or serialisation.

.. code:: python    

    from pyperl import pyperl
     
    perl = pyperl(script="my_script.pl")
    result = perl.run("--input", "data.csv")
     
    print("STDOUT   :", result["stdout"])
    print("STDERR   :", result["stderr"])
    print("Exit code:", result["returncode"])
     
    if result["returncode"] == 0:
        print("Script completed successfully.")

.. list-table:: Result dictionary keys
   :header-rows: 1
   :widths: 20 15 65

   * - Key
     - Type
     - Description
   * - ``"stdout"``
     - ``str``
     - Everything the Perl script printed to standard output.
   * - ``"stderr"``
     - ``str``
     - Everything printed to standard error (warnings, diagnostics).
   * - ``"returncode"``
     - ``int``
     - Exit code. ``0`` means success; anything else indicates an error.


4 — Audio conversion (full example)
--------------------------------------

This example shows the complete workflow for converting an audio file using
the bundled ``convert_audio.pl`` script.

 .. code:: python

    """Full end-to-end audio conversion workflow."""
    from pyperl import pyperl
     
    # 1. Initialize — Perl is found or installed automatically
    perl = pyperl(
        script="perl_scripts/convert_audio.pl",
        verbose="info",
    )
     
    # 2. Use the bundled example audio file
    audio_file = perl.import_example()   # returns path to data/example.wav
     
    # 3. Convert to MP3
    result = perl.run(audio_file, "output.mp3")
     
    if result["returncode"] == 0:
        print("Conversion successful!")
        print(result["stdout"])
    else:
        print("Conversion failed:", result["stderr"])


What happens on first run?
--------------------------

When you call ``pyperl()``, the library follows this resolution order:

1. **System PATH** — checks whether ``perl`` is already available globally.
2. **Common directories** — scans ``/usr/bin``, ``/usr/local/bin``, ``/opt/homebrew/bin``, and common Windows paths.
3. **Portable install** — if no Perl is found, downloads and extracts a portable Perl package into the system temp directory (or your custom ``installation_dir``).

On subsequent runs the previously installed Perl is reused automatically — no repeated downloads.

.. seealso::

   - :ref:`usage` — cross-platform details and advanced configuration
   - :ref:`api_reference` — complete API reference
   - :ref:`examples` — full gallery of runnable examples


.. include:: add_bottom.add