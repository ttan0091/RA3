"""diag.py - Lightweight diagnostic ticker"""
from . import _transport

def tick(event, **kwargs):
    _transport.emit({"event": event, **kwargs})
