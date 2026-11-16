#!/usr/bin/env python3
"""Thin wrapper: assemble the system prompt via brain.py.

Kept as a stable entry point so docs and habits don't break if the engine moves.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.exit(subprocess.call([sys.executable, str(HERE / "brain.py"), "build"] + sys.argv[1:]))
