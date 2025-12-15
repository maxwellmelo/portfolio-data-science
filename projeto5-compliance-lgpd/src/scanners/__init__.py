"""Módulo de scanners de dados sensíveis."""
from .pii_scanner import PIIScanner, ScanResult, PIIType, RiskLevel

__all__ = ["PIIScanner", "ScanResult", "PIIType", "RiskLevel"]
