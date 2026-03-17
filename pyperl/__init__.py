import logging

from pyperl.pyperl import pyperl

from pyperl.pyperl import (
    wget,
    get_base_dir,
    find_perl,
    set_logger,
    )


__author__ = 'Erdogan Taskesen'
__email__ = 'erdogant@gmail.com'
__version__ = '0.1.0'

# Setup package-level logger
_logger = logging.getLogger("pyperl")
_log_handler = logging.StreamHandler()
_formatter = logging.Formatter(fmt="[%(asctime)s] [%(name)-12s] [%(levelname)-8s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
_log_handler.setFormatter(_formatter)
_log_handler.setLevel(logging.DEBUG)
if not _logger.handlers: _logger.addHandler(_log_handler)
_logger.setLevel(logging.INFO)
_logger.propagate = False # can result in duplicate messages when True

# module level doc-string
__doc__ = """
pyperl
=====================================================================

pyperl is for runing Perl scripts using Python.

Example
-------
>>> # Import
>>> from pyperl import pyperl
>>>
>>> # Initialize
>>> perl = pyperl()
>>>
>>> # Get example audio file
>>> audio_file = perl.import_example()
>>>
>>> # Run perl script for audio conversion using ffmpeg
>>> out = perl.run(audio_file, "c:/temp/output.mp3")

References
----------
https://github.com/erdogant/pyperl

"""
