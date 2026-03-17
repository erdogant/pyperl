# pyperl

**pyperl** is a Python library that automatically installs and manages Perl, and provides a clean interface for running Perl scripts from Python — with zero manual Perl setup required.

---

### Key Features

| Feature | Description |
|--------|-------------|
| **Auto Perl Install** | Detects system Perl or installs a portable version automatically (Strawberry Perl on Windows, CPAN source on Linux/Mac). |
| **Cross-Platform** | Works on Windows, Linux, and macOS — handles the platform differences for you. |
| **Run Perl Scripts** | Execute any `.pl` script with arbitrary arguments directly from Python. |
| **Portable & Bundled** | Ships with bundled Perl archives so it works in offline or restricted environments. |
| **Logging Control** | Configurable verbosity from `"silent"` to `"debug"`. |

---

### Installation

##### Install from PyPI
```bash
pip install pyperl
```

##### Install from GitHub source
```bash
pip install git+https://github.com/erdogant/pyperl
```

---

### Quick Start

```python
from pyperl import pyperl

# Initialize — auto-detects or installs Perl
perl = pyperl()

# Run a Perl script
result = perl.run("my_script.pl")
print(result["stdout"])
```

##### Run a script with arguments
```python
perl = pyperl(perl_script="perl_scripts/convert_audio.pl")

result = perl.run("input.wav", "output.mp3")
print(result["stdout"])
print(result["returncode"])  # 0 = success
```

##### Use a custom installation directory
```python
perl = pyperl(installation_dir="/opt/my_perl", set_to_path=True)
```

##### Force reinstall portable Perl
```python
perl = pyperl(force_install=True)
```

---

### How It Works

On initialization, `pyperl` follows this resolution order:

1. **Check system PATH** — if `perl` is already available, use it.
2. **Search common directories** — checks `/usr/bin`, `/usr/local/bin`, `/opt/homebrew/bin`, and common Windows paths.
3. **Install portable Perl** — if no Perl is found, downloads and extracts a portable Perl package:
   - **Windows**: [Strawberry Perl](https://strawberryperl.com/) portable ZIP
   - **Linux/Mac**: Perl source from CPAN (tar.gz)

---

### API Reference

#### `pyperl(perl_script, installation_dir, set_to_path, perl_search_dirs, force_install, verbose)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `perl_script` | `str` | `"perl_scripts/convert_audio.pl"` | Path to the default Perl script. |
| `installation_dir` | `str` | system temp dir | Directory to install portable Perl. |
| `set_to_path` | `bool` | `False` | Add Perl to the system `PATH`. |
| `perl_search_dirs` | `list` | `None` | Extra directories to search for Perl. |
| `force_install` | `bool` | `False` | Force reinstall portable Perl. |
| `verbose` | `str` | `"info"` | Log level: `"silent"`, `"debug"`, `"info"`, `"warning"`, `"error"`, `"critical"`. |

#### `pyperl.run(*args, script=None, timeout=300)`

Executes a Perl script and returns a result dict.

| Key | Type | Description |
|-----|------|-------------|
| `"stdout"` | `str` | Standard output from the script. |
| `"stderr"` | `str` | Error output from the script. |
| `"returncode"` | `int` | Exit code (`0` = success). |

Raises `RuntimeError` on non-zero exit, timeout, or missing Perl executable.

---

### Maintainer

* erdogant — [GitHub](https://github.com/erdogant)
* Contributions are welcome.

### License

MIT License — see [LICENSE](LICENSE) for details.
