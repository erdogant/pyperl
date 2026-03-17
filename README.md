[![Python](https://img.shields.io/pypi/pyversions/pyperl)](https://img.shields.io/pypi/pyversions/pyperl)
[![PyPI Version](https://img.shields.io/pypi/v/pyperl)](https://pypi.org/project/pyperl/)
![GitHub Repo stars](https://img.shields.io/github/stars/erdogant/pyperl)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/erdogant/pyperl/blob/master/LICENSE)
[![Forks](https://img.shields.io/github/forks/erdogant/pyperl.svg)](https://github.com/erdogant/pyperl/network)
[![Open Issues](https://img.shields.io/github/issues/erdogant/pyperl.svg)](https://github.com/erdogant/pyperl/issues)
[![Project Status](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
[![Downloads](https://pepy.tech/badge/pyperl/month)](https://pepy.tech/project/pyperl/)
[![Downloads](https://pepy.tech/badge/pyperl)](https://pepy.tech/project/pyperl)
[![Docs](https://img.shields.io/badge/Sphinx-Docs-Green)](https://erdogant.github.io/pyperl/)
[![Medium](https://img.shields.io/badge/Medium-Blog-black)](https://erdogant.github.io/pyperl/pages/html/Documentation.html#medium-blog)
![GitHub repo size](https://img.shields.io/github/repo-size/erdogant/pyperl)
[![Donate](https://img.shields.io/badge/Support%20this%20project-grey.svg?logo=github%20sponsors)](https://erdogant.github.io/pyperl/pages/html/Documentation.html#)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://erdogant.github.io/pyperl/pages/html/Documentation.html#colab-notebook)


### 

<div>

<a href="https://erdogant.github.io/pyperl/"><img src="https://github.com/erdogant/pyperl/blob/master/docs/figs/logo.png" width="175" align="left" /></a>
**pyperl** is a Python library that automatically installs and manages Perl, and provides a clean interface for running Perl scripts from Python — with zero manual Perl setup required.
 Navigate to [API documentations](https://erdogant.github.io/pyperl/) for more detailed information. **⭐️ Star it if you like it ⭐️**
</div>

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

### Maintainer
* Erdogan Taskesen, github: [erdogant](https://github.com/erdogant)
* Contributions are welcome.
* Yes! This library is entirely **free** but it runs on coffee! :) Feel free to support with a <a href="https://erdogant.github.io/donate/?currency=USD&amount=5">Coffee</a>.

[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy+me+a+coffee&emoji=&slug=erdogant&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/erdogant)
