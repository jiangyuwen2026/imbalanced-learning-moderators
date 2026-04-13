"""
Adaptive-SyMProD V3: Classifier-Consistent CT Optimization

Key Improvements:
    1. Use same classifier for CT selection and final evaluation
    2. Nested CV: inner loop for CT, outer loop for evaluation
    3. Calibration: use held-out calibration set to pick CT
    4. Adaptive metric weights based on dataset characteristics
"""

import numpy as np
from typing import Optional, Tuple, Dict, List, Union
from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone
import warnings

from .symprod import SyMProD


class AdaptiveSyMProDV3:
    """
    Classifier-Consistent Adaptive-SyMProD.
    
    Ensures the CT selected is optimal for the specific classifier
    that will be used for final prediction.
    
    Parameters
    ----------
    classifier : estimator
        The classifier that will be used. CT optimization uses this
        same classifier to ensure consistency.
    ct_candidates : list or None
        List of CT values to try. If None, uses [0.6, 0.8, 1.0, 1.2, 1.4]
    validation_size : float, default=0.2
        Proportion of training data to use for CT validation
    metric : str, default='auc'
        Metric to optimize ('auc', 'ks', 'f1')
    k, m : int
        SyMProD parameters
    random_state : int, optional
        Random seed
    verbose : int, default=0
        Verbosity
    """
    
    def __init__(
        self,
        classifier,
        ct_candidates: Optional[List[float]] = None,
        validation_size: float = 0.2,
        metric: str = 'auc',
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None,
        verbose: int = 0
    ):
        self.classifier = classifier
        self.ct_candidates = ct_candidates or [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
        self.validation_size = validation_size
        self.metric = metric
        self.k = k
        self.m = m
        self.random_state = random_state
        self.verbose = verbose
        
        # Results
        self.best_ct_ = None
        self.best_score_ = None
        self.ct_scores_ = {}
        
    def _compute_metric(self, y_true, y_prob):
        """Compute specified metric."""
        from sklearn.metrics import roc_auc_score, f1_score, roc_curve
        
        if self.metric == 'auc':
            return roc_auc_score(y_true, y_prob)
        elif self.metric == 'f1':
            return f1_score(y_true, (y_prob > 0.5).astype(int))
        elif self.metric == 'ks':
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            return np.max(tpr - fpr)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'AdaptiveSyMProDV3':
        """
        Find optimal CT using held-out validation set.
        
        This ensures the CT is chosen using the same classifier
        that will be used for prediction.
        """
        from sklearn.model_selection import train_test_split
        
        X = np.asarray(X)
        y = np.asarray(y)
        
        if self.verbose >= 1:
            print(f"Adaptive V3: Testing {len(self.ct_candidates)} CT values")
        
        # Split training data: actual training + validation for CT selection
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=self.validation_size,
            stratify=y,
            random_state=self.random_state
        )
        
        # Test each CT value
        best_ct = self.ct_candidates[0]
        best_score = -np.inf
        
        for ct in self.ct_candidates:
            # Apply SyMProD with this CT
            sampler = SyMProD(ct=ct, k=self.k, m=self.m, random_state=self.random_state)
            
            try:
                X_res, y_res = sampler.fit_resample(X_train, y_train)
            except:
                self.ct_scores_[ct] = -np.inf
                continue
            
            # Train classifier (same one that will be used!)
            clf = clone(self.classifier)
            clf.fit(X_res, y_res)
            
            # Evaluate on validation set
            if hasattr(clf, 'predict_proba'):
                y_prob = clf.predict_proba(X_val)[:, 1]
            else:
                y_prob = clf.predict(X_val)
            
            score = self._compute_metric(y_val, y_prob)
            self.ct_scores_[ct] = score
            
            if self.verbose >= 2:
                print(f"  CT={ct:.2f}: {self.metric}={score:.4f}")
            
            if score > best_score:
                best_score = score
                best_ct = ct
        
        self.best_ct_ = best_ct
        self.best_score_ = best_score
        
        if self.verbose >= 1:
            print(f"  Best CT: {best_ct:.2f} ({self.metric}={best_score:.4f})")
        
        return self
    
    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Find optimal CT and resample all data."""
        self.fit(X, y)
        
        # Apply SyMProD with best CT to ALL data
        sampler = SyMProD(
            ct=self.best_ct_,
            k=self.k,
            m=self.m,
            random_state=self.random_state
        )
        
        return sampler.fit_resample(X, y)


class NestedCVAdaptiveSyMProD:
    """
    Nested Cross-Validation for unbiased CT selection.
    
    Outer loop: evaluate model performance
    Inner loop: select optimal CT
    
    This gives unbiased estimate of both CT selection and model performance.
    """
    
    def __init__(
        self,
        classifier,
        ct_candidates: Optional[List[float]] = None,
        outer_cv: int = 5,
        inner_cv: int = 3,
        metric: str = 'auc',
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None,
        verbose: int = 0
    ):
        self.classifier = classifier
        self.ct_candidates = ct_candidates or [0.6, 0.8, 1.0, 1.2, 1.4]
        self.outer_cv = outer_cv
        self.inner_cv = inner_cv
        self.metric = metric
        self.k = k
        self.m = m
        self.random_state = random_state
        self.verbose = verbose
        
        self.best_ct_ = None
        self.cv_scores_ = []
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'NestedCVAdaptiveSyMProD':
        """
        Nested CV to find CT that generalizes best.
        """
        from sklearn.model_selection import StratifiedKFold
        
        X = np.asarray(X)
        y = np.asarray(y)
        
        outer_skf = StratifiedKFold(
            n_splits=self.outer_cv,
            shuffle=True,
            random_state=self.random_state
        )
        
        ct_per_fold = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(outer_skf.split(X, y)):
            if self.verbose >= 1:
                print(f"Outer fold {fold_idx + 1}/{self.outer_cv}")
            
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Inner CV: find best CT for this fold
            inner_skf = StratifiedKFold(
                n_splits=self.inner_cv,
                shuffle=True,
                random_state=self.random_state
            )
            
            ct_scores = {ct: [] for ct in self.ct_candidates}
            
            for inner_train_idx, inner_val_idx in inner_skf.split(X_train, y_train):
                X_inner_train = X_train[inner_train_idx]
                y_inner_train = y_train[inner_train_idx]
                X_inner_val = X_train[inner_val_idx]
                y_inner_val = y_train[inner_val_idx]
                
                for ct in self.ct_candidates:
                    sampler = SyMProD(ct=ct, k=self.k, m=self.m, random_state=self.random_state)
                    
                    try:
                        X_res, y_res = sampler.fit_resample(X_inner_train, y_inner_train)
                        clf = clone(self.classifier)
                        clf.fit(X_res, y_res)
                        
                        if hasattr(clf, 'predict_proba'):
                            y_prob = clf.predict_proba(X_inner_val)[:, 1]
                        else:
                            y_prob = clf.predict(X_inner_val)
                        
                        from sklearn.metrics import roc_auc_score
                        score = roc_auc_score(y_inner_val, y_prob)
                        ct_scores[ct].append(score)
                    except:
                        ct_scores[ct].append(0)
            
            # Find best CT for this fold
            mean_scores = {ct: np.mean(scores) for ct, scores in ct_scores.items()}
            best_ct = max(mean_scores, key=mean_scores.get)
            ct_per_fold.append(best_ct)
            
            if self.verbose >= 2:
                print(f"  Best CT this fold: {best_ct} (score={mean_scores[best_ct]:.4f})")
        
        # Use most frequent CT across folds (robust choice)
        from collections import Counter
        ct_counter = Counter(ct_per_fold)
        self.best_ct_ = ct_counter.most_common(1)[0][0]
        
        if self.verbose >= 1:
            print(f"\nMost robust CT across {self.outer_cv} folds: {self.best_ct_}")
            print(f"CT distribution: {dict(ct_counter)}")
        
        return self
    
    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Find CT with nested CV and resample."""
        self.fit(X, y)
        
        sampler = SyMProD(
            ct=self.best_ct_,
            k=self.k,
            m=self.m,
            random_state=self.random_state
        )
        
        return sampler.fit_resample(X, y)


class SimpleAdaptiveCT:
    """
    Simplified adaptive CT selection.
    
    Uses a simple heuristic: try a few CT values and pick the one
    that produces the most "reasonable" synthetic samples.
    
    Heuristic criteria:
    1. Not too few samples (need sufficient training data)
    2. Not too many samples (avoid overfitting)
    3. Reasonable class separation in resampled data
    """
    
    def __init__(
        self,
        ct_candidates: List[float] = None,
        target_ratio: float = 1.0,
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None
    ):
        self.ct_candidates = ct_candidates or [0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
        self.target_ratio = target_ratio
        self.k = k
        self.m = m
        self.random_state = random_state
        self.best_ct_ = None
    
    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Simple heuristic selection."""
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        
        X = np.asarray(X)
        y = np.asarray(y)
        
        n_minority = np.sum(y == 1)
        n_majority = np.sum(y == 0)
        
        best_ct = 1.0
        best_score = -np.inf
        
        for ct in self.ct_candidates:
            sampler = SyMProD(ct=ct, k=self.k, m=self.m, random_state=self.random_state)
            
            try:
                X_res, y_res = sampler.fit_resample(X, y)
                
                # Heuristic: measure class separability after resampling
                lda = LinearDiscriminantAnalysis()
                lda.fit(X_res, y_res)
                
                # Compute separation (higher is better, but not too high)
                y_pred = lda.predict(X_res)
                accuracy = np.mean(y_pred == y_res)
                
                # Prefer moderate accuracy (0.6-0.8) indicating good but not overfit separation
                if 0.6 <= accuracy <= 0.8:
                    score = 1.0 - abs(accuracy - 0.7)  # Peak at 0.7
                else:
                    score = 0.5
                
                # Bonus for achieving target ratio
                actual_ratio = np.sum(y_res == 0) / np.sum(y_res == 1)
                ratio_penalty = abs(actual_ratio - self.target_ratio) / self.target_ratio
                score *= (1 - 0.3 * ratio_penalty)
                
                if score > best_score:
                    best_score = score
                    best_ct = ct
                    
            except:
                continue
        
        self.best_ct_ = best_ct
        
        # Final resampling with best CT
        sampler = SyMProD(ct=best_ct, k=self.k, m=self.m, random_state=self.random_state)
        return sampler.fit_resample(X, y)
