import subprocess
import sys
from pathlib import Path


def test_abstract_imports_in_subprocess():
    root = Path(__file__).resolve().parents[1]
    cmd = [sys.executable, '-c', 'from lab1.GA_abstract import Vector; from lab1.lab1 import Employees']
    run = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
