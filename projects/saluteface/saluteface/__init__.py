"""Saluteface: transparent, reproducible sequence research utilities."""
from .sequence import normalize_sequence, validate_sequence, gc_like_composition
from .watermark import WatermarkCodec, Verification
__version__ = "0.3.0"
__all__ = ["normalize_sequence", "validate_sequence", "gc_like_composition", "WatermarkCodec", "Verification"]
