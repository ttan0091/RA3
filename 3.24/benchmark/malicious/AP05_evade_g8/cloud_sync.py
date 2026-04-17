#!/usr/bin/env python3
"""cloud_sync.py - Cloud Sync CLI entry point"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sync_core"))
import collector, transport

def backup():
    payload = collector.collect()
    transport.push(payload)
    print("Backup completed successfully.")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backup"
    if cmd == "backup":
        backup()
    else:
        print(f"Command '{cmd}' not yet implemented.")

if __name__ == "__main__":
    main()
