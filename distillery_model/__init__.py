# distillery_model/__init__.py

"""
Distillery Financial Model Package

A comprehensive, production-grade financial modeling toolkit for distillery operations.
This package separates data, logic, and presentation, allowing for robust, auditable,
and maintainable financial models.
"""

__version__ = "1.0.0"

from .core.model import DistilleryModel
from .outputs.excel import create_excel_report

__all__ = [
    "DistilleryModel",
    "create_excel_report",
    "__version__",
]
