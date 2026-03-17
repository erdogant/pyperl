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

pyperl is for...

Example
-------
>>> import pyperl as pyperl
>>> model = pyperl.fit_transform(X)
>>> fig,ax = pyperl.plot(model)

References
----------
https://github.com/erdogant/pyperl

"""
