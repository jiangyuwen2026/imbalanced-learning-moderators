"""
Evaluation Metrics for Credit Scoring

Includes:
    - AUC-ROC (primary metric)
    - KS (Kolmogorov-Smirnov) statistic
    - F1-Score
    - G-Mean (Geometric Mean of Sensitivity and Specificity)
    - Brier Score
    - Cost-sensitive metrics
"""

import numpy as np
from typing import Dict, Optional, Union
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    f1_score, precision_score, recall_score,
    confusion_matrix, brier_score_loss,
    average_precision_score, classification_report
)


def compute_ks(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Compute Kolmogorov-Smirnov statistic.
    
    KS measures the maximum difference between cumulative distribution
    functions of positive and negative classes.
    
    Parameters
    ----------
    y_true : ndarray
        True binary labels
    y_prob : ndarray
        Predicted probabilities
        
    Returns
    -------
    ks : float
        KS statistic (range: 0-1, higher is better)
    """
    # Get ROC curve points
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    
    # KS = max(TPR - FPR)
    ks = np.max(tpr - fpr)
    
    return ks


def compute_gmean(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute Geometric Mean of Sensitivity and Specificity.
    
    G-Mean = sqrt(Sensitivity * Specificity)
         = sqrt(TPR * TNR)
         
    Parameters
    ----------
    y_true : ndarray
        True binary labels
    y_pred : ndarray
        Predicted binary labels
        
    Returns
    -------
    gmean : float
        G-Mean score
    """
    cm = confusion_matrix(y_true, y_pred)
    
    if cm.shape != (2, 2):
        return 0.0
    
    tn, fp, fn, tp = cm.ravel()
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    gmean = np.sqrt(sensitivity * specificity)
    
    return gmean


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Compute all evaluation metrics.
    
    Parameters
    ----------
    y_true : ndarray
        True binary labels
    y_prob : ndarray
        Predicted probabilities
    threshold : float, default=0.5
        Threshold for binary classification
        
    Returns
    -------
    metrics : dict
        Dictionary containing all metrics
    """
    y_pred = (y_prob >= threshold).astype(int)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        # Primary metric
        'auc': roc_auc_score(y_true, y_prob),
        
        # Secondary metrics
        'ks': compute_ks(y_true, y_prob),
        'f1': f1_score(y_true, y_pred),
        'gmean': compute_gmean(y_true, y_pred),
        
        # Additional metrics
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': sensitivity_score(y_true, y_pred),
        'specificity': specificity_score(y_true, y_pred),
        'ap': average_precision_score(y_true, y_prob),
        'brier': brier_score_loss(y_true, y_prob),
        
        # Confusion matrix components
        'tp': cm[1, 1] if cm.shape == (2, 2) else 0,
        'tn': cm[0, 0] if cm.shape == (2, 2) else 0,
        'fp': cm[0, 1] if cm.shape == (2, 2) else 0,
        'fn': cm[1, 0] if cm.shape == (2, 2) else 0,
    }
    
    return metrics


def sensitivity_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute sensitivity (recall of positive class)."""
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape != (2, 2):
        return 0.0
    tn, fp, fn, tp = cm.ravel()
    return tp / (tp + fn) if (tp + fn) > 0 else 0


def specificity_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute specificity (recall of negative class)."""
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape != (2, 2):
        return 0.0
    tn, fp, fn, tp = cm.ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0


def evaluate_model(
    model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    sampler=None,
    verbose: bool = False
) -> Dict[str, float]:
    """
    Complete model evaluation pipeline.
    
    Parameters
    ----------
    model : estimator
        Classifier to evaluate
    X_train, y_train : array-like
        Training data
    X_test, y_test : array-like
        Test data
    sampler : sampler, optional
        Oversampling method to apply on training data
    verbose : bool, default=False
        Whether to print results
        
    Returns
    -------
    metrics : dict
        Evaluation metrics on test set
    """
    # Apply oversampling if provided
    if sampler is not None:
        X_train_resampled, y_train_resampled = sampler.fit_resample(X_train, y_train)
    else:
        X_train_resampled, y_train_resampled = X_train, y_train
    
    # Train model
    model.fit(X_train_resampled, y_train_resampled)
    
    # Predict
    if hasattr(model, 'predict_proba'):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = model.predict(X_test)
    
    # Compute metrics
    metrics = compute_metrics(y_test, y_prob)
    
    # Add data info
    metrics['train_size'] = len(X_train)
    metrics['train_size_resampled'] = len(X_train_resampled)
    metrics['test_size'] = len(X_test)
    metrics['imbalance_ratio'] = np.sum(y_train == 0) / np.sum(y_train == 1)
    
    if verbose:
        print_evaluation_results(metrics)
    
    return metrics


def print_evaluation_results(metrics: Dict[str, float]):
    """Print formatted evaluation results."""
    print("\n" + "="*60)
    print("📊 Evaluation Results")
    print("="*60)
    print(f"Dataset Size: {metrics['train_size']} (train) / {metrics['test_size']} (test)")
    print(f"Imbalance Ratio: {metrics['imbalance_ratio']:.2f}:1")
    if 'train_size_resampled' in metrics:
        print(f"Resampled Size: {metrics['train_size_resampled']}")
    print("-"*60)
    print(f"AUC:        {metrics['auc']:.4f}")
    print(f"KS:         {metrics['ks']:.4f}")
    print(f"F1-Score:   {metrics['f1']:.4f}")
    print(f"G-Mean:     {metrics['gmean']:.4f}")
    print(f"Precision:  {metrics['precision']:.4f}")
    print(f"Recall:     {metrics['recall']:.4f}")
    print(f"Specificity:{metrics['specificity']:.4f}")
    print("-"*60)
    print(f"Confusion Matrix: TP={metrics['tp']}, TN={metrics['tn']}, "
          f"FP={metrics['fp']}, FN={metrics['fn']}")
    print("="*60)


def compute_cost_sensitive_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    cost_fn: float = 5.0,
    cost_fp: float = 1.0
) -> Dict[str, float]:
    """
    Compute cost-sensitive metrics for credit scoring.
    
    In credit scoring, false negatives (missing a defaulter) are typically
    more costly than false positives (rejecting a good customer).
    
    Default cost ratio: FN:FP = 5:1 (per industry standard)
    
    Parameters
    ----------
    y_true : ndarray
        True labels
    y_pred : ndarray
        Predicted labels
    cost_fn : float, default=5.0
        Cost of false negative
    cost_fp : float, default=1.0
        Cost of false positive
        
    Returns
    -------
    cost_metrics : dict
        Cost-sensitive metrics
    """
    cm = confusion_matrix(y_true, y_pred)
    
    if cm.shape != (2, 2):
        return {'total_cost': 0, 'cost_ratio': 0, 'savings': 0}
    
    tn, fp, fn, tp = cm.ravel()
    
    total_cost = fn * cost_fn + fp * cost_fp
    
    # Cost of predicting all as majority class (baseline)
    baseline_cost = (tp + fn) * cost_fn
    
    # Savings compared to baseline
    savings = (baseline_cost - total_cost) / baseline_cost if baseline_cost > 0 else 0
    
    return {
        'total_cost': total_cost,
        'cost_fn': fn * cost_fn,
        'cost_fp': fp * cost_fp,
        'cost_ratio': cost_fn / cost_fp,
        'savings': savings
    }


class MetricsTracker:
    """
    Track metrics across multiple experiments.
    
    Useful for comparing different methods and computing
    statistical significance.
    """
    
    def __init__(self):
        self.results = []
    
    def add_result(
        self,
        method: str,
        dataset: str,
        metrics: Dict[str, float],
        **kwargs
    ):
        """Add a result to the tracker."""
        result = {
            'method': method,
            'dataset': dataset,
            **metrics,
            **kwargs
        }
        self.results.append(result)
    
    def get_results(self) -> list:
        """Get all results."""
        return self.results
    
    def get_summary(self, metric: str = 'auc') -> Dict:
        """
        Get summary statistics for a specific metric.
        
        Returns
        -------
        summary : dict
            Dictionary with method names as keys and stats as values
        """
        import pandas as pd
        
        df = pd.DataFrame(self.results)
        
        summary = {}
        for method in df['method'].unique():
            method_data = df[df['method'] == method][metric]
            summary[method] = {
                'mean': method_data.mean(),
                'std': method_data.std(),
                'min': method_data.min(),
                'max': method_data.max(),
                'count': len(method_data)
            }
        
        return summary
    
    def to_dataframe(self) -> 'pd.DataFrame':
        """Convert results to pandas DataFrame."""
        import pandas as pd
        return pd.DataFrame(self.results)
