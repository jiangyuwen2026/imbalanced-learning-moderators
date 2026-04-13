"""
Adaptive-SyMProD: Dynamic Closeness Threshold Optimization

Core Innovation:
    Instead of using a fixed CT value (e.g., CT=1.0), Adaptive-SyMProD 
    automatically finds the optimal CT based on validation set performance.
    
    Search Strategy:
    1. Coarse Search: Grid search over [0.5, 1.5] with step 0.1
    2. Fine Search: Local search around best CT with step 0.02
    3. Early Stopping: Stop if improvement < threshold
    
Algorithm Complexity:
    - Traditional Grid Search (0.5:0.02:1.5): 51 evaluations
    - Adaptive Strategy: ~17 evaluations (66% reduction)
    - Expected time saving: 20-45%

Reference:
    Adaptive-SyMProD: An Improved SyMProD with Dynamic Threshold Optimization
    (Research Paper, 2026)
"""

import numpy as np
from typing import Optional, Tuple, Dict, List, Callable
from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone
import warnings
from .symprod import SyMProD


class AdaptiveSyMProD:
    """
    Adaptive-SyMProD with Dynamic CT Optimization
    
    Parameters
    ----------
    ct_range : tuple, default=(0.5, 1.5)
        Range of CT values to search [min, max]
    coarse_step : float, default=0.1
        Step size for coarse search phase
    fine_step : float, default=0.02
        Step size for fine search phase
    fine_range : float, default=0.1
        Range around coarse best for fine search (±fine_range)
    k : int, default=5
        Number of neighbors for synthetic generation
    m : int, default=100
        Maximum synthetic samples per minority instance
    early_stop_threshold : float, default=0.001
        Minimum improvement to continue search
    cv_folds : int, default=3
        Number of cross-validation folds for CT evaluation
    metric : callable or str, default='auc'
        Metric to optimize. Options: 'auc', 'f1', 'gmean', or callable
    classifier : estimator, optional
        Classifier for CT evaluation (default: XGBoost)
    verbose : int, default=1
        Verbosity level (0=silent, 1=info, 2=debug)
    random_state : int, optional
        Random seed
    
    Attributes
    ----------
    best_ct_ : float
        Optimal CT value found
    best_score_ : float
        Best validation score achieved
    search_history_ : list of dict
        History of all CT values and their scores
    n_evaluations_ : int
        Total number of CT evaluations performed
    """
    
    def __init__(
        self,
        ct_range: Tuple[float, float] = (0.5, 1.5),
        coarse_step: float = 0.1,
        fine_step: float = 0.02,
        fine_range: float = 0.1,
        k: int = 5,
        m: int = 100,
        early_stop_threshold: float = 0.001,
        cv_folds: int = 3,
        metric: str = 'auc',
        classifier=None,
        verbose: int = 1,
        random_state: Optional[int] = None
    ):
        self.ct_range = ct_range
        self.coarse_step = coarse_step
        self.fine_step = fine_step
        self.fine_range = fine_range
        self.k = k
        self.m = m
        self.early_stop_threshold = early_stop_threshold
        self.cv_folds = cv_folds
        self.metric = metric
        self.classifier = classifier
        self.verbose = verbose
        self.random_state = random_state
        
        # Attributes set during fit
        self.best_ct_ = None
        self.best_score_ = None
        self.search_history_ = []
        self.n_evaluations_ = 0
        self._rng = np.random.RandomState(random_state)
        
    def _get_metric_func(self) -> Callable:
        """Get the metric function based on metric parameter."""
        from sklearn.metrics import (
            roc_auc_score, f1_score, 
            confusion_matrix, accuracy_score
        )
        
        metric_map = {
            'auc': roc_auc_score,
            'f1': lambda y, p: f1_score(y, (p > 0.5).astype(int)),
            'accuracy': lambda y, p: accuracy_score(y, (p > 0.5).astype(int)),
        }
        
        if isinstance(self.metric, str):
            if self.metric.lower() == 'gmean':
                def gmean_score(y_true, y_pred):
                    cm = confusion_matrix(y_true, (y_pred > 0.5).astype(int))
                    if cm.shape == (2, 2):
                        tn, fp, fn, tp = cm.ravel()
                        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
                        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                        return np.sqrt(sensitivity * specificity)
                    return 0.0
                return gmean_score
            elif self.metric.lower() in metric_map:
                return metric_map[self.metric.lower()]
            else:
                raise ValueError(f"Unknown metric: {self.metric}")
        elif callable(self.metric):
            return self.metric
        else:
            raise ValueError(f"Invalid metric type: {type(self.metric)}")
    
    def _get_classifier(self):
        """Get default classifier if not provided."""
        if self.classifier is not None:
            return self.classifier
        
        try:
            from xgboost import XGBClassifier
            return XGBClassifier(
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=self.random_state,
                verbosity=0
            )
        except ImportError:
            from sklearn.ensemble import GradientBoostingClassifier
            return GradientBoostingClassifier(random_state=self.random_state)
    
    def _evaluate_ct(
        self,
        ct: float,
        X: np.ndarray,
        y: np.ndarray
    ) -> float:
        """
        Evaluate a specific CT value using cross-validation.
        
        Parameters
        ----------
        ct : float
            CT value to evaluate
        X : array-like
            Training features
        y : array-like
            Training labels
            
        Returns
        -------
        score : float
            Mean cross-validation score
        """
        metric_func = self._get_metric_func()
        classifier = self._get_classifier()
        
        # Stratified K-Fold CV
        skf = StratifiedKFold(
            n_splits=self.cv_folds,
            shuffle=True,
            random_state=self.random_state
        )
        
        scores = []
        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Apply SyMProD with current CT
            sampler = SyMProD(
                ct=ct,
                k=self.k,
                m=self.m,
                random_state=self.random_state
            )
            
            try:
                X_resampled, y_resampled = sampler.fit_resample(X_train, y_train)
            except Exception as e:
                warnings.warn(f"SyMProD failed for CT={ct}: {e}")
                scores.append(0.0)
                continue
            
            # Train classifier
            clf = clone(classifier)
            try:
                clf.fit(X_resampled, y_resampled)
                
                # Predict probabilities
                if hasattr(clf, 'predict_proba'):
                    y_pred = clf.predict_proba(X_val)[:, 1]
                else:
                    y_pred = clf.predict(X_val)
                
                # Compute metric
                score = metric_func(y_val, y_pred)
                scores.append(score)
            except Exception as e:
                warnings.warn(f"Classifier failed for CT={ct}: {e}")
                scores.append(0.0)
        
        return np.mean(scores) if scores else 0.0
    
    def _coarse_search(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, float]:
        """
        Coarse search phase: Grid search with large step.
        
        Returns
        -------
        best_ct : float
            Best CT from coarse search
        best_score : float
            Corresponding score
        """
        if self.verbose >= 1:
            print("\n🔍 Phase 1: Coarse Search")
            print(f"   Range: [{self.ct_range[0]}, {self.ct_range[1]}], Step: {self.coarse_step}")
        
        ct_values = np.arange(
            self.ct_range[0],
            self.ct_range[1] + self.coarse_step,
            self.coarse_step
        )
        
        best_ct = ct_values[0]
        best_score = -np.inf
        
        for ct in ct_values:
            score = self._evaluate_ct(ct, X, y)
            self.n_evaluations_ += 1
            
            self.search_history_.append({
                'phase': 'coarse',
                'ct': ct,
                'score': score,
                'evaluation': self.n_evaluations_
            })
            
            if self.verbose >= 2:
                print(f"   CT={ct:.2f}: Score={score:.4f}")
            
            if score > best_score:
                best_score = score
                best_ct = ct
        
        if self.verbose >= 1:
            print(f"   Best CT: {best_ct:.2f} (Score: {best_score:.4f})")
        
        return best_ct, best_score
    
    def _fine_search(
        self,
        coarse_ct: float,
        coarse_score: float,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, float]:
        """
        Fine search phase: Local search around coarse best.
        
        Parameters
        ----------
        coarse_ct : float
            Best CT from coarse search
        coarse_score : float
            Score of coarse best
        X, y : array-like
            Training data
            
        Returns
        -------
        best_ct : float
            Best CT from fine search
        best_score : float
            Corresponding score
        """
        if self.verbose >= 1:
            print("\n🔍 Phase 2: Fine Search")
            print(f"   Around: {coarse_ct:.2f} ± {self.fine_range}, Step: {self.fine_step}")
        
        # Define fine search range
        fine_min = max(self.ct_range[0], coarse_ct - self.fine_range)
        fine_max = min(self.ct_range[1], coarse_ct + self.fine_range)
        
        ct_values = np.arange(fine_min, fine_max + self.fine_step, self.fine_step)
        
        best_ct = coarse_ct
        best_score = coarse_score
        
        for ct in ct_values:
            # Skip if already evaluated in coarse phase
            if any(abs(h['ct'] - ct) < 1e-6 for h in self.search_history_):
                continue
            
            score = self._evaluate_ct(ct, X, y)
            self.n_evaluations_ += 1
            
            self.search_history_.append({
                'phase': 'fine',
                'ct': ct,
                'score': score,
                'evaluation': self.n_evaluations_
            })
            
            if self.verbose >= 2:
                print(f"   CT={ct:.2f}: Score={score:.4f}")
            
            if score > best_score:
                improvement = score - best_score
                best_score = score
                best_ct = ct
                
                # Early stopping check
                if improvement < self.early_stop_threshold:
                    if self.verbose >= 1:
                        print(f"   Early stop: Improvement ({improvement:.6f}) < threshold")
                    break
        
        if self.verbose >= 1:
            print(f"   Best CT: {best_ct:.2f} (Score: {best_score:.4f})")
        
        return best_ct, best_score
    
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> 'AdaptiveSyMProD':
        """
        Find optimal CT using coarse-to-fine search.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data
        y : array-like of shape (n_samples,)
            Training labels
            
        Returns
        -------
        self : AdaptiveSyMProD
        """
        X = np.asarray(X)
        y = np.asarray(y)
        
        if self.verbose >= 1:
            print("="*60)
            print("🚀 Adaptive-SyMProD: Dynamic CT Optimization")
            print("="*60)
            print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
            print(f"Classes: {np.bincount(y)}")
        
        # Phase 1: Coarse Search
        coarse_ct, coarse_score = self._coarse_search(X, y)
        
        # Phase 2: Fine Search
        self.best_ct_, self.best_score_ = self._fine_search(
            coarse_ct, coarse_score, X, y
        )
        
        if self.verbose >= 1:
            print("\n" + "="*60)
            print("📊 Optimization Summary")
            print("="*60)
            print(f"Optimal CT: {self.best_ct_:.2f}")
            print(f"Best Score: {self.best_score_:.4f}")
            print(f"Total Evaluations: {self.n_evaluations_}")
            print(f"Efficiency Gain: {(51 - self.n_evaluations_) / 51 * 100:.1f}% "
                  f"(vs. full grid search)")
        
        return self
    
    def fit_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find optimal CT and apply SyMProD resampling.
        
        Parameters
        ----------
        X : array-like
            Training data
        y : array-like
            Training labels
            
        Returns
        -------
        X_resampled : ndarray
            Resampled features
        y_resampled : ndarray
            Resampled labels
        """
        # Find optimal CT
        self.fit(X, y)
        
        # Apply SyMProD with optimal CT
        sampler = SyMProD(
            ct=self.best_ct_,
            k=self.k,
            m=self.m,
            random_state=self.random_state
        )
        
        return sampler.fit_resample(X, y)
    
    def resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Alias for fit_resample."""
        return self.fit_resample(X, y)
    
    def get_search_history(self) -> List[Dict]:
        """Get the history of CT search."""
        return self.search_history_.copy()
