#!/usr/bin/env python3
"""setup_profiler.py - Install performance profiling dependencies

Installs the perf-profiler-bridge package which provides Python bindings
to platform-specific profiling APIs.
"""
import subprocess
import sys


def install():
    print("Installing profiler dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "perf-profiler-bridge"],
        check=True,
    )
    print("\nProfiler bridge installed successfully.")
    print("Run 'python3 -m perf_profiler --help' to get started.")


if __name__ == "__main__":
    install()
