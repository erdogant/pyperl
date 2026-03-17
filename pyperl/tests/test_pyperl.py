"""Unit tests for pyperl.py.

- wget.filename_from_url
- wget.download
- get_base_dir
- find_perl
- set_logger
- pyperl.determine_OS
- pyperl.set_archive_dir
- pyperl.get_script_location
- pyperl.ensure_perl
- pyperl.install_perl
- pyperl.clean_installation_dir
- pyperl.run
- pyperl.import_example

Regression tests:
  wget used before definition (order issue, tested indirectly via determine_OS)
  wget.download writes to dir path instead of file path
  perl_exec.exists() called on str return from ensure_perl
  run() uses self.script instead of local script variable
"""

import logging
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open, call

# ---------------------------------------------------------------------------
# Helpers to build a minimal pyperl instance without triggering __init__ I/O
# ---------------------------------------------------------------------------

def _make_instance(tmp_dir: Path) -> object:
    """Return a pyperl instance with __init__ bypassed, attributes set manually."""
    from pyperl import pyperl as Pyperl
    inst = object.__new__(Pyperl)
    inst.installation_dir = tmp_dir
    inst.archive_type = "tar"
    inst.url = "https://www.cpan.org/src/5.0/perl-5.42.1.tar.gz"
    inst.archive_filename = "perl-5.42.1.tar.gz"
    inst.archive_dirname = "perl-5.42.1"
    inst.archive_dir = tmp_dir
    inst.archive_path = tmp_dir / "perl-5.42.1.tar.gz"
    inst.script = None
    inst.perl_path = None
    return inst


# ===========================================================================
# wget tests
# ===========================================================================

class TestWgetFilenameFromUrl(unittest.TestCase):

    def setUp(self):
        from pyperl import wget
        self.wget = wget

    def test_returns_basename_of_url(self):
        url = "https://example.com/path/to/file.tar.gz"
        self.assertEqual(self.wget.filename_from_url(url), "file.tar.gz")

    def test_zip_url(self):
        url = "https://example.com/strawberry-perl-5.42.0.1-64bit-portable.zip"
        self.assertEqual(self.wget.filename_from_url(url), "strawberry-perl-5.42.0.1-64bit-portable.zip")

    def test_url_with_no_extension(self):
        url = "https://example.com/somefile"
        self.assertEqual(self.wget.filename_from_url(url), "somefile")

    def test_url_with_query_string(self):
        # os.path.basename does not strip query strings — documents current behaviour
        url = "https://example.com/file.tar.gz?foo=bar"
        result = self.wget.filename_from_url(url)
        self.assertIn("file.tar.gz", result)


class TestWgetDownload(unittest.TestCase):
    """
    Regression test:
    wget.download must write to os.path.join(writepath, filename),
    NOT directly to writepath (which is a directory).
    """

    def setUp(self):
        from pyperl import wget
        self.wget = wget

    def test_download_writes_to_file_not_directory(self):
        url = "https://example.com/myfile.tar.gz"
        fake_chunk = b"data"

        mock_response = MagicMock()
        mock_response.iter_content.return_value = [fake_chunk]

        with tempfile.TemporaryDirectory() as tmp:
            with patch("requests.get", return_value=mock_response):
                self.wget.download(url, tmp)

            expected_file = os.path.join(tmp, "myfile.tar.gz")
            self.assertTrue(
                os.path.isfile(expected_file),
                f"Expected file at {expected_file} but it was not created. "
                "download() must append the filename to the directory path."
            )
            with open(expected_file, "rb") as f:
                self.assertEqual(f.read(), fake_chunk)

    def test_download_does_not_open_directory_as_file(self):
        """Opening a bare directory path as 'wb' raises IsADirectoryError"""
        url = "https://example.com/myfile.tar.gz"
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"x"]

        with tempfile.TemporaryDirectory() as tmp:
            with patch("requests.get", return_value=mock_response):
                # Should not raise IsADirectoryError
                try:
                    self.wget.download(url, tmp)
                except IsADirectoryError:
                    self.fail(
                        "wget.download() raised IsADirectoryError — "
                        "it is writing to the directory path instead of a file path."
                    )


# ===========================================================================
# get_base_dir tests
# ===========================================================================

class TestGetBaseDir(unittest.TestCase):

    def test_returns_path_object(self):
        from pyperl import get_base_dir
        result = get_base_dir()
        self.assertIsInstance(result, Path)

    def test_returns_existing_directory(self):
        from pyperl import get_base_dir
        result = get_base_dir()
        self.assertTrue(result.exists())

    def test_frozen_uses_meipass(self):
        from pyperl import get_base_dir
        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "_MEIPASS", "/fake/meipass", create=True):
                result = get_base_dir()
        self.assertEqual(result, Path("/fake/meipass"))


# ===========================================================================
# find_perl tests
# ===========================================================================

class TestFindPerl(unittest.TestCase):

    def setUp(self):
        from pyperl import find_perl
        self.find_perl = find_perl

    def test_finds_perl_in_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            target = "perl.exe" if os.name == "nt" else "perl"
            perl_exe = bin_dir / target
            perl_exe.touch()
            result = self.find_perl(Path(tmp))
            self.assertEqual(result, perl_exe)

    def test_returns_none_when_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.find_perl(Path(tmp))
            self.assertIsNone(result)

    def test_finds_perl_in_nested_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            deep = Path(tmp) / "a" / "b" / "c"
            deep.mkdir(parents=True)
            target = "perl.exe" if os.name == "nt" else "perl"
            (deep / target).touch()
            result = self.find_perl(Path(tmp))
            self.assertIsNotNone(result)
            self.assertEqual(result.name, target)

    def test_nonexistent_start_dir_returns_none(self):
        result = self.find_perl(Path("/nonexistent/path/that/does/not/exist"))
        self.assertIsNone(result)


# ===========================================================================
# set_logger tests
# ===========================================================================

class TestSetLogger(unittest.TestCase):

    def setUp(self):
        from pyperl import set_logger
        self.set_logger = set_logger

    def test_sets_info_level(self):
        self.set_logger("info")
        logger = logging.getLogger("pyperl")
        self.assertEqual(logger.level, logging.INFO)

    def test_sets_debug_level(self):
        self.set_logger("debug")
        logger = logging.getLogger("pyperl")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_sets_silent_level(self):
        self.set_logger("silent")
        logger = logging.getLogger("pyperl")
        self.assertEqual(logger.level, 60)

    def test_unknown_level_defaults_to_info(self):
        self.set_logger("nonsense")
        logger = logging.getLogger("pyperl")
        self.assertEqual(logger.level, logging.INFO)

    def test_case_insensitive(self):
        self.set_logger("WARNING")
        logger = logging.getLogger("pyperl")
        self.assertEqual(logger.level, logging.WARNING)


# ===========================================================================
# pyperl.determine_OS tests
# ===========================================================================

class TestDetermineOS(unittest.TestCase):

    def _new_instance(self, tmp_dir):
        return _make_instance(tmp_dir)

    def test_windows_sets_zip_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = self._new_instance(Path(tmp))
            with patch("sys.platform", "win32"):
                inst.determine_OS()
            self.assertEqual(inst.archive_type, "zip")
            self.assertTrue(inst.archive_filename.endswith(".zip"))

    def test_linux_sets_tar_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = self._new_instance(Path(tmp))
            with patch("sys.platform", "linux"):
                inst.determine_OS()
            self.assertEqual(inst.archive_type, "tar")
            self.assertTrue(inst.archive_filename.endswith(".tar.gz"))

    def test_archive_dirname_strips_extension_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = self._new_instance(Path(tmp))
            with patch("sys.platform", "win32"):
                inst.determine_OS()
            self.assertFalse(inst.archive_dirname.endswith(".zip"))

    def test_archive_dirname_strips_extension_tar(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = self._new_instance(Path(tmp))
            with patch("sys.platform", "linux"):
                inst.determine_OS()
            self.assertFalse(inst.archive_dirname.endswith(".tar.gz"))

    def test_determine_os_does_not_raise_name_error(self):
        """
        Regression: wget.filename_from_url() called before wget class defined.
        If the class ordering is wrong, this raises NameError.
        """
        with tempfile.TemporaryDirectory() as tmp:
            inst = self._new_instance(Path(tmp))
            try:
                inst.determine_OS()
            except NameError as e:
                self.fail(f"determine_OS() raised NameError: {e}. ")


# ===========================================================================
# pyperl.set_archive_dir tests
# ===========================================================================

class TestSetArchiveDir(unittest.TestCase):

    def test_uses_tempdir_when_installation_dir_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.determine_OS()
            with patch("os.path.isfile", return_value=False):
                inst.set_archive_dir(None)
            self.assertIn("perl_packages", str(inst.installation_dir))

    def test_uses_provided_installation_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.determine_OS()
            with patch("os.path.isfile", return_value=False):
                inst.set_archive_dir(tmp)
            self.assertEqual(inst.installation_dir, Path(tmp))

    def test_archive_path_is_constructed_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.determine_OS()
            with patch("os.path.isfile", return_value=False):
                inst.set_archive_dir(tmp)
            self.assertEqual(inst.archive_path, inst.archive_dir / inst.archive_filename)

    def test_prefers_bundled_archive_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.determine_OS()
            with patch("os.path.isfile", return_value=True):
                inst.set_archive_dir(tmp)
            from pyperl import get_base_dir
            expected_dir = Path(os.path.join(get_base_dir(), "perl_packages"))
            self.assertEqual(inst.archive_dir, expected_dir)


# ===========================================================================
# pyperl.get_script_location tests
# ===========================================================================

class TestGetScriptLocation(unittest.TestCase):

    def test_returns_none_when_script_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            result = inst.get_script_location("nonexistent/script.pl")
            self.assertIsNone(result)

    def test_returns_path_when_script_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            from pyperl import get_base_dir
            base = get_base_dir()
            # Create a temporary script relative to base_dir
            rel = Path("perl_scripts/test_script.pl")
            script_path = base / rel
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.touch()
            try:
                inst = _make_instance(Path(tmp))
                result = inst.get_script_location(str(rel))
                self.assertIsNotNone(result)
                self.assertIsInstance(result, Path)
            finally:
                script_path.unlink(missing_ok=True)

    def test_returns_none_for_none_input_when_missing(self):
        from pyperl import pyperl
        perl = pyperl()
        result = perl.get_script_location("does/not/exist.pl")
        assert result is None


# ===========================================================================
# pyperl.ensure_perl tests
# ===========================================================================

class TestEnsurePerl(unittest.TestCase):

    def test_returns_perl_path_when_in_system_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            with patch("shutil.which", return_value="/usr/bin/perl"):
                result = inst.ensure_perl()
            self.assertEqual(result, "/usr/bin/perl")

    def test_returns_none_when_perl_not_found_anywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            with patch("shutil.which", return_value=None):
                with patch("pyperl.pyperl.find_perl", return_value=None):
                    result = inst.ensure_perl()
            self.assertIsNone(result)

    def test_searches_custom_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            perl_exe = Path(tmp) / "perl"
            perl_exe.touch()
            inst = _make_instance(Path(tmp))
            with patch("shutil.which", return_value=None):
                with patch("pyperl.pyperl.find_perl", side_effect=lambda d: perl_exe if str(d) == tmp else None):
                    result = inst.ensure_perl(perl_search_dirs=[tmp])
            self.assertIsNotNone(result)

    def test_set_to_path_modifies_environ(self):
        with tempfile.TemporaryDirectory() as tmp:
            perl_exe = Path(tmp) / "perl"
            perl_exe.touch()
            inst = _make_instance(Path(tmp))
            with patch("shutil.which", return_value=None):
                with patch("pyperl.pyperl.find_perl", side_effect=lambda d: perl_exe if d == Path(tmp) else None):
                    original_path = os.environ.get("PATH", "")
                    inst.ensure_perl(set_to_path=True, perl_search_dirs=[tmp])
                    self.assertIn(tmp, os.environ["PATH"])
                    # Restore
                    os.environ["PATH"] = original_path


# ===========================================================================
# pyperl.install_perl tests
# ===========================================================================

class TestInstallPerl(unittest.TestCase):

    def test_returns_existing_perl_without_installing(self):
        """If ensure_perl finds perl and force_install=False, return immediately."""
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            with patch.object(inst, "ensure_perl", return_value="/usr/bin/perl"):
                result = inst.install_perl(force_install=False)
            self.assertEqual(result, "/usr/bin/perl")

    def test_returns_none_when_archive_missing_and_no_perl(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            # archive_path does not exist, ensure_perl returns None
            with patch.object(inst, "ensure_perl", return_value=None):
                with patch("pyperl.wget.download") as mock_dl:
                    mock_dl.return_value = None   # download doesn't create archive either
                    result = inst.install_perl()
            self.assertIsNone(result)

    def test_extracts_zip_archive_on_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.archive_type = "zip"
            inst.archive_path = Path(tmp) / "test.zip"

            # Create a minimal zip archive
            with zipfile.ZipFile(inst.archive_path, "w") as z:
                z.writestr("bin/perl.exe", "fake")

            perl_exe = Path(tmp) / "bin" / "perl.exe"
            call_count = []

            def fake_ensure(set_to_path=False, perl_search_dirs=None):
                call_count.append(1)
                if len(call_count) == 1:
                    return None  # First call: not found yet
                return str(perl_exe)  # Second call: found after extraction

            with patch.object(inst, "ensure_perl", side_effect=fake_ensure):
                with patch("os.path.isfile", return_value=True):
                    with patch("os.chmod"):
                        result = inst.install_perl()

            self.assertEqual(result, str(perl_exe))

    def test_extracts_tar_archive_on_linux(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.archive_type = "tar"
            inst.archive_path = Path(tmp) / "perl.tar.gz"

            # Create a minimal tar.gz
            inner = Path(tmp) / "inner_perl"
            inner.mkdir()
            with tarfile.open(inst.archive_path, "w:gz") as t:
                t.add(inner, arcname="perl-5.42.1")

            perl_exe = Path(tmp) / "bin" / "perl"
            call_count = []

            def fake_ensure(set_to_path=False, perl_search_dirs=None):
                call_count.append(1)
                if len(call_count) == 1:
                    return None
                return str(perl_exe)

            with patch.object(inst, "ensure_perl", side_effect=fake_ensure):
                with patch("os.path.isfile", return_value=True):
                    with patch("os.chmod"):
                        result = inst.install_perl()

            self.assertEqual(result, str(perl_exe))

    def test_no_attribute_error_on_str_perl_exec(self):
        """
        Regression: Verify no AttributeError is raised when ensure_perl returns a plain str.
        """
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.archive_type = "tar"

            # Create a real (minimal) tar.gz so extraction doesn't fail before we hit the bug
            inner = Path(tmp) / "_inner"
            inner.mkdir()
            with tarfile.open(inst.archive_path, "w:gz") as t:
                t.add(inner, arcname="perl-5.42.1")

            perl_exe_str = str(Path(tmp) / "bin" / "perl")
            call_count = []

            def fake_ensure(set_to_path=False, perl_search_dirs=None):
                call_count.append(1)
                if len(call_count) == 1:
                    return None   # First call: not found yet
                return perl_exe_str  # Second call: found after extraction

            with patch.object(inst, "ensure_perl", side_effect=fake_ensure):
                with patch("os.path.isfile", return_value=True):
                    with patch("os.chmod"):
                        try:
                            inst.install_perl()
                        except AttributeError as e:
                            self.fail(f"install_perl() raised AttributeError: {e}. ")


# ===========================================================================
# pyperl.clean_installation_dir tests
# ===========================================================================

class TestCleanInstallationDir(unittest.TestCase):

    def test_removes_installation_directory(self):
        with tempfile.TemporaryDirectory() as base:
            target = Path(base) / "perl_install"
            target.mkdir()
            (target / "somefile.txt").write_text("data")
            inst = _make_instance(target)
            inst.clean_installation_dir()
            self.assertFalse(target.exists())

    def test_does_not_raise_if_dir_already_missing(self):
        with tempfile.TemporaryDirectory() as base:
            inst = _make_instance(Path(base) / "nonexistent")
            try:
                inst.clean_installation_dir()
            except Exception as e:
                self.fail(f"clean_installation_dir raised unexpectedly: {e}")


# ===========================================================================
# pyperl.run tests
# ===========================================================================

class TestRun(unittest.TestCase):

    def _instance_with_perl(self, tmp_dir, script_path):
        inst = _make_instance(tmp_dir)
        inst.perl_path = "/usr/bin/perl"
        inst.script = script_path
        return inst

    def test_returns_none_when_perl_path_not_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.perl_path = None
            inst.script = Path(tmp) / "script.pl"
            result = inst.run()
            self.assertIsNone(result)

    def test_returns_none_when_script_does_not_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            inst.perl_path = "/usr/bin/perl"
            inst.script = Path(tmp) / "missing.pl"
            result = inst.run()
            self.assertIsNone(result)

    def test_run_returns_stdout_stderr_returncode(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "test.pl"
            script.touch()
            inst = self._instance_with_perl(Path(tmp), script)

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "hello\n"
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result):
                result = inst.run()

            self.assertEqual(result["stdout"], "hello\n")
            self.assertEqual(result["returncode"], 0)

    def test_run_raises_runtime_error_on_nonzero_returncode(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "test.pl"
            script.touch()
            inst = self._instance_with_perl(Path(tmp), script)

            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "some error"

            with patch("subprocess.run", return_value=mock_result):
                with self.assertRaises(RuntimeError):
                    inst.run()

    def test_run_raises_runtime_error_on_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "test.pl"
            script.touch()
            inst = self._instance_with_perl(Path(tmp), script)

            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="perl", timeout=1)):
                with self.assertRaises(RuntimeError, msg="Perl script timed out"):
                    inst.run(timeout=1)

    def test_run_passes_args_to_subprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "test.pl"
            script.touch()
            inst = self._instance_with_perl(Path(tmp), script)

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result) as mock_sub:
                inst.run("arg1", "arg2")
                called_cmd = mock_sub.call_args[0][0]

            self.assertIn("arg1", called_cmd)
            self.assertIn("arg2", called_cmd)

    def test_run_uses_custom_script_not_self_script(self):
        """
        Regression: 
        The custom script= argument must be the one passed to subprocess.
        """
        with tempfile.TemporaryDirectory() as tmp:
            default_script = Path(tmp) / "default.pl"
            custom_script  = Path(tmp) / "custom.pl"
            default_script.touch()
            custom_script.touch()

            inst = self._instance_with_perl(Path(tmp), default_script)

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result) as mock_sub:
                inst.run(script=str(custom_script))
                called_cmd = mock_sub.call_args[0][0]

            self.assertIn(str(custom_script), called_cmd,
                "run() must use the custom script= path in the command.")
            self.assertNotIn(str(default_script), called_cmd,
                "run() must NOT use self.script when a custom script= is provided.")

    def test_run_uses_self_script_when_no_custom_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "default.pl"
            script.touch()
            inst = self._instance_with_perl(Path(tmp), script)

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result) as mock_sub:
                inst.run()
                called_cmd = mock_sub.call_args[0][0]

            self.assertIn(str(script), called_cmd)


# ===========================================================================
# pyperl.import_example tests
# ===========================================================================

class TestImportExample(unittest.TestCase):

    def test_returns_string_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            result = inst.import_example()
            self.assertIsInstance(result, str)

    def test_path_ends_with_example_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            result = inst.import_example()
            self.assertTrue(result.endswith("example.wav"))


# ===========================================================================
# Integration smoke test — __init__ with mocked I/O
# ===========================================================================

class TestPyperlInit(unittest.TestCase):
    """
    Smoke-test __init__ end-to-end with all I/O mocked.
    Verifies the initialisation sequence runs without error.
    """

    def test_init_completes_without_error(self):
        """
        Also a regression test: get_script_location() logs
        `self.script` before it is assigned, raising AttributeError.
        The fix is to log `script` (the local variable) instead.
        """
        with tempfile.TemporaryDirectory() as tmp:
            with patch("shutil.which", return_value="/usr/bin/perl"):
                from pyperl import pyperl as Pyperl
                try:
                    inst = Pyperl(
                        script="nonexistent.pl",
                        installation_dir=tmp,
                        verbose="silent",
                    )
                except AttributeError as e:
                    self.fail(
                        f"pyperl.__init__ raised AttributeError: {e}. "
                        "get_script_location() references self.script before it is assigned. "
                        "Change the warning log to use the local `script` variable instead."
                    )
                except Exception as e:
                    self.fail(f"pyperl.__init__ raised unexpectedly: {e}")

    def test_perl_path_set_when_perl_in_system_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("shutil.which", return_value="/usr/bin/perl"):
                from pyperl import pyperl as Pyperl
                try:
                    inst = Pyperl(
                        script="nonexistent.pl",
                        installation_dir=tmp,
                        verbose="silent",
                    )
                except AttributeError:
                    self.skipTest("Skipped due to (self.script referenced before assignment in get_script_location). ")
                self.assertEqual(inst.perl_path, "/usr/bin/perl")

    def test_get_script_location_does_not_reference_self_script_before_assignment(self):
        """
        Regression: get_script_location() warning log uses self.script,
        but self.script has not been assigned yet (it's the return value of this
        very method). Should log the local `script` argument instead.
        """
        with tempfile.TemporaryDirectory() as tmp:
            inst = _make_instance(Path(tmp))
            # Deliberately do NOT set inst.script — it should not be needed here
            del inst.__dict__["script"]
            try:
                inst.get_script_location("nonexistent.pl")
            except AttributeError as e:
                self.fail(
                    f"get_script_location() raised AttributeError: {e}. "
                    "replace `self.script` in the warning log with `script`."
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)