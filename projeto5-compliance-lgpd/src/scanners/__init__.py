"""Módulo de scanners de dados sensíveis."""
from .pii_scanner import PIIScanner, ScanResult

__all__ = ["PIIScanner", "ScanResult"]
