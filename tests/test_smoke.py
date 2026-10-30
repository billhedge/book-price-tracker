import subprocess
import sys

import booktracker


def test_package_imports() -> None:
    assert booktracker.__version__


def test_module_entry_point_prints_help():
    result = subprocess.run(
        [sys.executable, "-m", "booktracker", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
