"""pyperl.

Name        : pyperl.py
Author      : erdogant
Contact     : erdogant@gmail.com
github      : https://github.com/erdogant/pyperl

"""
import os
import shutil
import subprocess
import logging
import sys
import zipfile
import tarfile
import requests
import tempfile
from pathlib import Path


logger = logging.getLogger(__name__)


# %% Retrieve files files.
class wget:
    """Retrieve file from url."""

    def filename_from_url(url, ext=True):
        """Return filename."""
        urlname = os.path.basename(url)
        if not ext: _, ext = os.path.splitext(urlname)
        return urlname

    def download(url, writepath):
        """Download.

        Parameters
        ----------
        url : str.
            Internet source.
        writepath : str.
            Directory to write the file.

        Returns
        -------
        None.

        """
        writepath = str(writepath)
        logger.info(f'Downloading {wget.filename_from_url(url)}')
        r = requests.get(url, stream=True)
        filepath = os.path.join(writepath, wget.filename_from_url(url))
        with open(filepath, "wb") as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

# %% Main class
class pyperl:
    """Convert audio files to WAV using a Perl script."""

    def __init__(self,
                 script="perl_scripts/convert_audio.pl",
                 installation_dir=None,
                 set_to_path=False,
                 perl_search_dirs=None,
                 force_install=False,
                 verbose="info",
                 ):
        """
        Initialize the pyperl class for converting audio files using a Perl script.

        Parameters
        ----------
        script : str, optional
            Path to the Perl script used for audio conversion. Default is "perl_scripts/convert_audio.pl".
        installation_dir : string, optional
            if None, the system temp directory is taken.
        set_to_path : bool, optional
            If True, add the Perl executable to the system PATH. Default is False.
        perl_search_dirs : list or None, optional
            Additional directories to search for a Perl installation. Default is None.
        force_install : bool, optional
            If True, force reinstallation of portable Perl even if Perl is already found. Default is False.
        verbose : str, optional
            Logging verbosity level. Options: "silent", "debug", "info", "warning", "error", "critical". Default is "info".

        Returns
        -------
        None
        """
        # Set logger
        set_logger(verbose)
        # Determine system OS
        self.determine_OS()

        # Set archive and installation dir
        self.set_archive_dir(installation_dir)
        # Set the location of the perl script
        self.script = self.get_script_location(script)
        # Install perl
        self.perl_path = self.install_perl(set_to_path=set_to_path, perl_search_dirs=perl_search_dirs, force_install=force_install)


    def set_archive_dir(self, installation_dir):
        if installation_dir is None:
            installation_dir = os.path.join(tempfile.gettempdir(), "perl_packages")
        # Convert to path
        if isinstance(installation_dir, str):
            self.installation_dir = Path(installation_dir)

        # Check whether perl archive file exists in dir
        if os.path.isfile(os.path.join(get_base_dir(), "perl_packages", self.archive_filename)):
            self.archive_dir = Path(os.path.join(get_base_dir(), "perl_packages"))
        else:
            # Set archive dir to tempdir where it needs to download the files
            self.archive_dir = self.installation_dir
        # Set path
        self.archive_path = self.archive_dir / self.archive_filename

    def determine_OS(self):
        # Determine system OS
        if sys.platform.startswith("win"):
            self.archive_type = "zip"
            self.url = 'https://github.com/StrawberryPerl/Perl-Dist-Strawberry/releases/download/SP_54201_64bit/strawberry-perl-5.42.0.1-64bit-portable.zip'
            self.archive_filename = wget.filename_from_url(self.url)
            self.archive_dirname = self.archive_filename.replace('.zip','')
        else:
            self.archive_type = "tar"
            self.url = 'https://www.cpan.org/src/5.0/perl-5.42.1.tar.gz'
            self.archive_filename = wget.filename_from_url(self.url)
            self.archive_dirname = self.archive_filename.replace('.tar.gz','')

    def get_script_location(self, script):
        """
        Resolve and validate the location of the Perl script.

        Parameters
        ----------
        script : str or Path
            Path to the Perl script to be used for audio conversion.

        Returns
        -------
        script : Path or None
            Path object pointing to the Perl script if found, otherwise None.
        """
        # Determine package directory
        base_dir = get_base_dir()

        # Set path in a modular manner
        if script is not None:
            script = Path(os.path.join(base_dir, script))

        # Check existense of path
        if not script.exists():
            logger.warning(f"Perl script not found: {script}")
            return None
        else:
            logger.info("Perl script is successfully set.")

        # Return
        return script

    # Install perl from portable location
    def install_perl(self, set_to_path=False, perl_search_dirs=None, force_install = False):
        """Install and configure Perl on the system.

        This method installs Perl from a portable package if it's not already available
        in the system or if force_install is True. It supports both Windows and Unix-like
        systems with appropriate archive formats (ZIP for Windows, TAR.GZ for Linux/Mac).

        Parameters
        ----------
        set_to_path : bool, optional
            If True, sets the installation directory to the portable_perl path.
            Default is False.
        perl_search_dirs : list[str] | None, optional
            List of directories to search for existing Perl installations.
            If None, default system paths are used. Default is None.
        force_install : bool, optional
            If True, forces reinstallation even if Perl is partially installed.
            Default is False.

        Returns
        -------
        str
            Path to the installed Perl executable if successful, None otherwise.

        Raises
        ------
        RuntimeError
            If Perl cannot be installed or extracted properly.
        FileNotFoundError
            If required archive files are missing.
        PermissionError
            If permission is denied during extraction or permission changes.

        Notes
        -----
        1. On Windows, requires a valid "strawberry-perl" zip package.
        2. On Unix-like systems, expects a "perl-5.42.1.tar.gz" archive.
        3. The portable directory is set to `portable_perl` under the project root.
        4. Executable permissions are set to 755 for Perl binaries.

        References
        ----------
        - Perl installation guide: https://www.perl.org/get.html#unix_like
        - Python's ensure_perl docs: https://github.com/pyperl/pyperl/blob/main/pyperl/pyperl.py#L200

        """
        # base_dir = get_base_dir()

        # 1. Check system perl
        perl_exec = self.ensure_perl(set_to_path=set_to_path, perl_search_dirs=perl_search_dirs)
        if perl_exec and not force_install:
            return perl_exec

        logger.info('Installing perl from portable location.')

        # Force delete for new fresh installations
        if force_install:
            self.clean_installation_dir()

        # Create directory
        self.installation_dir.mkdir(parents=True, exist_ok=True)

        # Perl path
        # perl_exec = (
        #     self.installation_dir
        #     / self.archive_dirname
        #     / ("bin/perl.exe" if self.archive_type == "zip" else "bin/perl"))


        # Check whether archive already exists, if not, then download
        if not self.archive_path.exists():
            logger.warning(f"Portable perl {self.archive_type} not found: {self.archive_path}")
            # Download to archive dir
            wget.download(self.url, str(self.installation_dir))

        if self.archive_path.exists():
            logger.info('Partable perl package detected.')
        else:
            logger.error('Partable perl package not found. <return>')
            return None


        if perl_exec is None or not perl_exec.exists() and self.archive_path.exists():
            logger.info("Extracting portable Perl...")
            # Extract
            if self.archive_type == "zip":
                with zipfile.ZipFile(self.archive_path, "r") as z:
                    z.extractall(self.installation_dir)
            else:
                with tarfile.open(self.archive_path, "r") as tar:
                    tar.extractall(path=self.installation_dir)


        # Set the perl path
        perl_exec = self.ensure_perl(set_to_path=set_to_path, perl_search_dirs=perl_search_dirs)

        if not os.path.isfile(perl_exec):
            logger.warning("Portable Perl extraction failed.")
            raise RuntimeError("Portable Perl extraction failed.")
        
        # ensure executable permissions
        os.chmod(perl_exec, 0o755)

        logger.info(f"Using portable perl: {perl_exec}")

        # Return
        return str(perl_exec)


    # Ensure Perl
    def ensure_perl(self, set_to_path=False, perl_search_dirs=None):
        """Ensure Perl is available in the system path.

        This method checks for Perl installation in standard locations and optional
        custom directories. If found, it ensures Perl is accessible either through
        PATH modification or by setting the environment variable directly.

        Parameters
        ----------
        set_to_path : bool, optional
            If True, modifies the system PATH to include the portable Perl directory.
            Default is False.
        perl_search_dirs : list[str] | None, optional
            Additional directories to search for Perl executables. If None, uses
            default system paths. Default is None.

        Returns
        -------
        str
            Path to the found Perl executable if successful, None otherwise.

        Notes
        -----
        1. Checks standard system paths first (Linux/Mac: /usr/bin, /opt/homebrew/bin)
        2. For Windows systems, checks common Perl installation locations
        3. If set_to_path is True, modifies PATH environment variable
        4. Returns None if Perl cannot be found

        References
        ----------
        - Perl installation guide: https://www.perl.org/get.html#unix_like
        - Python's shutil.which documentation: https://docs.python.org/3/library/shutil.html#module-shutil

        """
        # Check wether perl is in path
        perl_path = shutil.which("perl")

        if perl_path:
            logger.info(f"Perl found in PATH: {perl_path}")
            return perl_path

        # Search whether perl is installed at other locations
        search_dirs = [str(self.installation_dir)]

        if perl_search_dirs:
            search_dirs.extend(perl_search_dirs)

        search_dirs.extend([
            "/usr/bin",
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "C:\\Strawberry\\perl\\bin",
            "C:\\Perl\\bin",
        ])

        for d in search_dirs:
            # perl_candidate_path = Path(d) / ("perl.exe" if os.name == "nt" else "perl")
            perl_candidate_path = find_perl(Path(d))
            if perl_candidate_path is not None and perl_candidate_path.exists():
                logger.info(f"Perl found at: {perl_candidate_path}")
                if set_to_path:
                    os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]
                return str(perl_candidate_path)

        logger.warning("Perl executable path not found.")
        return None

    def clean_installation_dir(self):
        logger.info('Removing previous installations of the portable perl package..')
        shutil.rmtree(self.installation_dir, ignore_errors=True)

    def run(self, *args, script=None, timeout=300):
        """Execute a Perl script with arbitrary arguments and manage execution parameters.

           This method runs Perl scripts with support for custom arguments, timeout control,
           and detailed output collection. It handles error conditions and provides
           comprehensive logging of execution details.

           Parameters
           ----------
           *args : str
               Variable length argument list to pass to the Perl script.
               If None, uses the script's embedded default arguments.
           script : str, optional
               Path to Perl script to execute. If None, uses the instance's default script.
               Default is None.
           timeout : int, optional
               Maximum execution time in seconds. Default is 300 seconds (5 minutes).
               Raise RuntimeError if exceeded.

           Returns
           -------
           dict
               Dictionary containing:
               - "stdout": str: Standard output from Perl script
               - "stderr": str: Error output from Perl script
               - "returncode": int: Exit status code of Perl process

           Raises
           ------
           RuntimeError
               If Perl executable not found
               - If script execution fails with non-zero exit code
               - If script execution times out
               - If required dependencies are missing

           Notes
           -----
           1. Logs detailed execution information including command construction
           2. Validates script existence before execution
           3. Handles subprocess timeouts gracefully
           4. Preserves original Perl script arguments when not overridden
           5. Returns structured output for easy programmatic handling

           Examples
           --------
           Basic execution:
               result = pyperl.run(script="my_script.pl")

           With custom arguments:
               result = pyperl.run("--input", "data.txt")

           Timeout example:
               try:
                   result = pyperl.run(script="long_script.pl", timeout=60)
               except RuntimeError as e:
                   print(f"Execution timed out: {e}")

           """
        if self.perl_path is None:
            logger.error("Perl executable path not set")
            return None

        # Get script
        script = Path(script) if script is not None else self.script
        if not script.exists():
            logger.error("No Perl script specified")
            return None

        # Build command
        cmd = [
            str(self.perl_path),
            str(script),
            *map(str, args),
        ]

        logger.info(f"Running Perl script: {script.name}")
        logger.info(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

        except subprocess.TimeoutExpired as e:
            logger.error("Perl script timed out")
            raise RuntimeError("Perl script timed out") from e

        # Handle errors
        if result.returncode != 0:
            logger.error(result.stderr.strip())
            raise RuntimeError(
                f"Perl script failed with return code {result.returncode}"
            )

        # Debug logging
        if result.stdout:
            logger.debug(result.stdout.strip())

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def import_example(self):
        return os.path.join(get_base_dir(), 'data', 'example.wav')


# %%
def get_base_dir():
    """

    Returns
    -------
    base_dir : TYPE
        DESCRIPTION.

    """
    # Path of this file. This manner is important because it solves issues with pyinstaller/cxfreeze installations etc
    # Ensures the script is found inside the bundled executable environment.
    if getattr(sys, "frozen", False):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).resolve().parent
    return base_dir

def find_perl(start_dir: Path):
    """
    Recursively search for a Perl executable starting from the given directory.

    Parameters
    ----------
    start_dir : Path
        The directory from which to begin searching for the Perl executable.

    Returns
    -------
    Path or None
        The full path to the Perl executable if found, otherwise None.

    """
    target = "perl.exe" if os.name == "nt" else "perl"

    for root, dirs, files in os.walk(start_dir):
        if target in files:
            return Path(root) / target

    return None



# %%
def set_logger(verbose="info"):
    _logger = logging.getLogger("pyperl")

    levels = {
        "silent": 60,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    level = levels.get(str(verbose).lower(), logging.INFO)
    _logger.setLevel(level)

    for h in _logger.handlers:
        h.setLevel(level)


# %% Example usage
if __name__ == "__main__":

    # Initialize
    perl = pyperl(verbose='info')
    # Get example audio file
    audio_file = perl.import_example()
    # Run perl script for audio conversion using ffmpeg
    perl.run(audio_file, "output.mp3")
