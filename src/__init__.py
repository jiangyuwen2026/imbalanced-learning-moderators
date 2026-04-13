"""
Adaptive-SyMProD: Adaptive Synthetically Minority Over-sampling with Probabilistic Distribution

A credit scoring oriented oversampling method with dynamic closeness threshold optimization.

Main Components:
    - SyMProD: Base algorithm (Tum et al., 2020)
    - AdaptiveSyMProD: Dynamic CT optimization variant
    - DataPreprocessor: Data cleaning and preprocessing
    - ExperimentRunner: Complete experimental framework

Author: Research Team
Version: 0.1.0
"""

from .symprod import SyMProD
from .adaptive_symprod import AdaptiveSyMProD
from .preprocessing import DataPreprocessor
from .metrics import evaluate_model, compute_metrics
from .experiments import ExperimentRunner

__version__ = "0.1.0"
__all__ = [
    "SyMProD",
    "AdaptiveSyMProD", 
    "DataPreprocessor",
    "evaluate_model",
    "compute_metrics",
    "ExperimentRunner",
]
