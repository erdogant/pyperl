.. _examples:

========
Examples
========


Basic usage
-----------

Auto-detect or install Perl, then run a script.

.. code:: python    
    
    """Basic initialization and script execution."""
    from pyperl import pyperl
     
    # Initialize — auto-detects or installs Perl
    perl = pyperl(script="my_script.pl")
     
    # Run the default Perl script
    result = perl.run()
     
    print(result["stdout"])
    print(result["returncode"])  # 0 = success


Run with arguments
------------------

Forward positional arguments directly to the Perl script.

.. code:: python    

    """Run a Perl script with positional arguments."""
    from pyperl import pyperl
     
    perl = pyperl(script="perl_scripts/convert_audio.pl")
     
    # Pass positional arguments directly to the Perl script
    result = perl.run("input.wav", "output.mp3")
     
    print(result["stdout"])
    print(result["returncode"])  # 0 = success


Inspect the result dictionary
------------------------------

``run()`` returns a plain ``dict`` — inspect all three output fields.

.. code:: python    

    from pyperl import pyperl
     
    perl = pyperl(script="my_script.pl")
    result = perl.run("--input", "data.csv")
     
    print("STDOUT   :", result["stdout"])
    print("STDERR   :", result["stderr"])
    print("Exit code:", result["returncode"])
     
    if result["returncode"] == 0:
        print("Script completed successfully.")


Override the script at run-time
--------------------------------

Change the Perl script for a single call without re-initialising.

 .. code:: python    

    """Search additional directories for an existing Perl installation."""
    from pyperl import pyperl
     
    perl = pyperl(
        script="my_script.pl",
        perl_search_dirs=[
            "/home/myuser/perl5/bin",
            "/custom/tools/perl/bin",
        ],
    )
     
    result = perl.run("--verbose")
    print(result["stdout"])
        



Custom installation directory
------------------------------

Install portable Perl to a persistent path and add it to the system ``PATH``.

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


Search additional directories
------------------------------

Point pyperl at a non-standard Perl location before falling back to a portable install.

 .. code:: python    

    """Override the default script at run-time without re-initializing."""
    from pyperl import pyperl
     
    perl = pyperl()
     
    # Run a completely different script on the same Perl installation
    result = perl.run("arg1", "arg2", script="other_script.pl")
    print(result["stdout"])
     


Force reinstall
---------------

Wipe any existing portable Perl installation and re-extract from the archive.

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
     


Timeout handling
----------------

Cap execution time and handle a ``RuntimeError`` if the script runs too long.

 .. code:: python    

    """Handle a long-running script with a custom timeout."""
    from pyperl import pyperl
 
    perl = pyperl(script="long_running.pl")
 
    try:
        result = perl.run(timeout=60)   # raises RuntimeError after 60 s
        print(result["stdout"])
    except RuntimeError as e:
        print(f"Script timed out or failed: {e}")
    


Verbosity / logging control
-----------------------------

Switch between silent, informational, and debug log levels.

 .. code:: python

    """Control log output with the verbose parameter."""
    from pyperl import pyperl
     
    # Silent — no log output at all
    perl_silent = pyperl(script="my_script.pl", verbose="silent")
     
    # Debug — full internal logging to stdout
    perl_debug = pyperl(script="my_script.pl", verbose="debug")
     
    result = perl_debug.run()
    print(result["stdout"])



Full audio conversion workflow
-------------------------------

End-to-end example using the bundled ``convert_audio.pl`` script and the
example ``example.wav`` audio file.

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

.. include:: add_bottom.add