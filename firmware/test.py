#!/usr/bin/env python3
"""Run protocol and actual-sketch tests against simulated hardware, plus host tests."""
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='epaper-tests-') as tmp:
    for name in ['test_core','test_application']:
        out=str(Path(tmp)/name)
        subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',
          '-Wno-misleading-indentation','-fsanitize=address,undefined',
          '-I',str(ROOT/'tests/fakes'),str(ROOT/'tests'/f'{name}.cpp'),'-o',out],check=True)
        subprocess.run([out],check=True)
subprocess.run(['python','-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],check=True)
