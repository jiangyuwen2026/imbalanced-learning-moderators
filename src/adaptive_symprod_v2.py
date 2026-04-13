"""
Adaptive-SyMProD V2: Enhanced Dynamic CT Optimization

Improvements over V1:
    1. Multi-metric fusion (AUC + KS + F1 weighted average)
    2. Repeated cross-validation for stability
    3. Bayesian Optimization for efficient search
    4. Ensemble of top-k CT values
    5. Meta-learning: use dataset statistics to guide search

Author: Research Team
Version: 2.0.0
"""

import numpy as np
from typing import Optional, Tuple, Dict, List, Callable, Union
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier
import warnings
from scipy import stats

from .symprod import SyMProD


class AdaptiveSyMProDV2:
    """
    Enhanced Adaptive-SyMProD with multiple improvements.
    
    Parameters
    ----------
    ct_range : tuple, default=(0.3, 2.0)
        Extended search range (wider than V1)
    search_strategy : str, default='bayesian'
        Search strategy: 'bayesian', 'adaptive', or 'grid'
    n_repeats : int, default=3
        Number of repeats for repeated CV (stability)
    cv_folds : int, default=3
        Number of CV folds
    metrics : list or str, default=['auc', 'ks', 'f1']
        Metrics to optimize (multi-metric fusion)
    metric_weights : dict, optional
        Weights for each metric
    use_ensemble : bool, default=True
        Whether to ensemble top-k CT values
    top_k : int, default=3
        Number of top CT values to ensemble
    random_state : int, optional
        Random seed
    verbose : int, default=1
        Verbosity level
    """
    
    def __init__(
        self,
        ct_range: Tuple[float, float] = (0.3, 2.0),
        search_strategy: str = 'bayesian',
        n_repeats: int = 3,
        cv_folds: int = 3,
        metrics: Union[List[str], str] = ['auc', 'ks', 'f1'],
        metric_weights: Optional[Dict[str, float]] = None,
        use_ensemble: bool = True,
        top_k: int = 3,
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None,
        verbose: int = 1
    ):
        self.ct_range = ct_range
        self.search_strategy = search_strategy
        self.n_repeats = n_repeats
        self.cv_folds = cv_folds
        self.metrics = metrics if isinstance(metrics, list) else [metrics]
        self.metric_weights = metric_weights or {'auc': 0.5, 'ks': 0.3, 'f1': 0.2}
        self.use_ensemble = use_ensemble
        self.top_k = top_k
        self.k = k
        self.m = m
        self.random_state = random_state
        self.verbose = verbose
        
        # Attributes
        self.best_ct_ = None
        self.best_score_ = None
        self.search_history_ = []
        self.top_cts_ = []  # For ensemble
        self.n_evaluations_ = 0
        self._rng = np.random.RandomState(random_state)
        
    def _compute_metrics(self, y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        """Compute multiple metrics."""
        from sklearn.metrics import roc_auc_score, f1_score, roc_curve, confusion_matrix
        
        metrics = {}
        
        # AUC
        if 'auc' in self.metrics:
            metrics['auc'] = roc_auc_score(y_true, y_prob)
        
        # KS
        if 'ks' in self.metrics:
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            metrics['ks'] = np.max(tpr - fpr)
        
        # F1
        if 'f1' in self.metrics:
            y_pred = (y_prob > 0.5).astype(int)
            metrics['f1'] = f1_score(y_true, y_pred)
        
        # G-Mean
        if 'gmean' in self.metrics:
            y_pred = (y_prob > 0.5).astype(int)
            cm = confusion_matrix(y_true, y_pred)
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                metrics['gmean'] = np.sqrt(sensitivity * specificity)
        
        return metrics
    
    def _fusion_score(self, metrics: Dict[str, float]) -> float:
        """Compute weighted fusion score from multiple metrics."""
        score = 0.0
        total_weight = 0.0
        
        for metric, weight in self.metric_weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _evaluate_ct_stable(
        self,
        ct: float,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, Dict[str, float]]:
        """
        Evaluate CT with repeated cross-validation for stability.
        
        Returns
        -------
        mean_score : float
            Mean fusion score across repeats
        metric_details : dict
            Detailed metrics
        """
        classifier = GradientBoostingClassifier(
            n_estimators=50,
            random_state=self.random_state,
            max_depth=3
        )
        
        # Repeated Stratified K-Fold
        rskf = RepeatedStratifiedKFold(
            n_splits=self.cv_folds,
            n_repeats=self.n_repeats,
            random_state=self.random_state
        )
        
        all_scores = []
        all_metrics = {m: [] for m in self.metrics}
        
        for train_idx, val_idx in rskf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Apply SyMProD
            sampler = SyMProD(ct=ct, k=self.k, m=self.m, random_state=self.random_state)
            
            try:
                X_res, y_res = sampler.fit_resample(X_train, y_train)
            except:
                all_scores.append(0.0)
                continue
            
            # Train and evaluate
            clf = clone(classifier)
            try:
                clf.fit(X_res, y_res)
                y_prob = clf.predict_proba(X_val)[:, 1]
                
                metrics = self._compute_metrics(y_val, y_prob)
                fusion_score = self._fusion_score(metrics)
                
                all_scores.append(fusion_score)
                for m in self.metrics:
                    if m in metrics:
                        all_metrics[m].append(metrics[m])
            except:
                all_scores.append(0.0)
        
        # Compute mean and std
        mean_score = np.mean(all_scores) if all_scores else 0.0
        std_score = np.std(all_scores) if all_scores else 0.0
        
        metric_details = {
            'fusion_score': mean_score,
            'fusion_std': std_score,
            **{m: np.mean(v) if v else 0.0 for m, v in all_metrics.items()}
        }
        
        # Adjust score by stability (prefer stable CT values)
        stability_bonus = 1.0 / (1.0 + std_score)  # Lower std = higher bonus
        adjusted_score = mean_score * (0.9 + 0.1 * stability_bonus)
        
        return adjusted_score, metric_details
    
    def _bayesian_search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_iterations: int = 20
    ) -> Tuple[float, float]:
        """
        Bayesian Optimization for CT search.
        
        Uses Gaussian Process surrogate model with Expected Improvement acquisition.
        """
        try:
            from skopt import gp_minimize
            from skopt.space import Real
            
            if self.verbose >= 1:
                print("\n🔍 Bayesian Optimization")
                print(f"   Iterations: {n_iterations}")
            
            # Objective function (to minimize, so negate score)
            def objective(ct_list):
                ct = ct_list[0]
                score, _ = self._evaluate_ct_stable(ct, X, y)
                self.n_evaluations_ += 1
                return -score
            
            # Run optimization
            result = gp_minimize(
                objective,
                dimensions=[Real(self.ct_range[0], self.ct_range[1], name='ct')],
                n_calls=n_iterations,
                n_random_starts=5,
                random_state=self.random_state,
                verbose=self.verbose >= 2
            )
            
            best_ct = result.x[0]
            best_score = -result.fun
            
            # Store history
            for i, (ct, score) in enumerate(zip(result.x_iters, result.func_vals)):
                self.search_history_.append({
                    'iteration': i,
                    'ct': ct[0],
                    'score': -score
                })
            
            return best_ct, best_score
            
        except ImportError:
            if self.verbose >= 1:
                print("\n⚠️  scikit-optimize not available, falling back to adaptive search")
            return self._adaptive_search(X, y)
    
    def _adaptive_search(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, float]:
        """
        Enhanced adaptive search with success-based region focusing.
        """
        if self.verbose >= 1:
            print("\n🔍 Enhanced Adaptive Search")
        
        # Phase 1: Initial exploration
        explore_points = np.linspace(self.ct_range[0], self.ct_range[1], 8)
        
        candidates = []
        for ct in explore_points:
            score, details = self._evaluate_ct_stable(ct, X, y)
            self.n_evaluations_ += 1
            candidates.append((ct, score, details))
            
            if self.verbose >= 2:
                print(f"   CT={ct:.2f}: Fusion={score:.4f}")
        
        # Phase 2: Focus on promising regions
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_3 = candidates[:3]
        
        if self.verbose >= 1:
            print(f"   Top 3: {[(c[0], c[1]) for c in top_3]}")
        
        # Phase 3: Fine-tune around top candidates
        best_ct, best_score = top_3[0][0], top_3[0][1]
        
        for ct_center, _, _ in top_3:
            # Local search around each top candidate
            local_range = 0.15
            local_points = np.linspace(
                max(self.ct_range[0], ct_center - local_range),
                min(self.ct_range[1], ct_center + local_range),
                5
            )
            
            for ct in local_points:
                # Skip if already evaluated
                if any(abs(c[0] - ct) < 0.01 for c in candidates):
                    continue
                
                score, details = self._evaluate_ct_stable(ct, X, y)
                self.n_evaluations_ += 1
                candidates.append((ct, score, details))
                
                if score > best_score:
                    best_score = score
                    best_ct = ct
        
        # Sort and store top-k for ensemble
        candidates.sort(key=lambda x: x[1], reverse=True)
        self.top_cts_ = [(c[0], c[1]) for c in candidates[:self.top_k]]
        
        return best_ct, best_score
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'AdaptiveSyMProDV2':
        """Find optimal CT using enhanced search."""
        X = np.asarray(X)
        y = np.asarray(y)
        
        if self.verbose >= 1:
            print("="*60)
            print("🚀 Adaptive-SyMProD V2: Enhanced CT Optimization")
            print("="*60)
            print(f"Dataset: {X.shape[0]} samples, IR={np.sum(y==0)/np.sum(y==1):.2f}:1")
            print(f"Strategy: {self.search_strategy}")
            print(f"Metrics: {self.metrics} with weights {self.metric_weights}")
            print(f"Repeated CV: {self.n_repeats} repeats × {self.cv_folds} folds")
        
        # Search for best CT
        if self.search_strategy == 'bayesian':
            self.best_ct_, self.best_score_ = self._bayesian_search(X, y)
        else:
            self.best_ct_, self.best_score_ = self._adaptive_search(X, y)
        
        if self.verbose >= 1:
            print("\n" + "="*60)
            print("📊 Optimization Summary")
            print("="*60)
            print(f"Best CT: {self.best_ct_:.2f}")
            print(f"Best Fusion Score: {self.best_score_:.4f}")
            print(f"Evaluations: {self.n_evaluations_}")
            if self.use_ensemble and self.top_cts_:
                print(f"Top {self.top_k} CTs for ensemble: {[f'{c[0]:.2f}' for c in self.top_cts_]}")
        
        return self
    
    def fit_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Find optimal CT and resample."""
        self.fit(X, y)
        
        if self.use_ensemble and len(self.top_cts_) > 1:
            # Ensemble: generate samples from top-k CT values
            return self._ensemble_resample(X, y)
        else:
            # Single best CT
            sampler = SyMProD(
                ct=self.best_ct_,
                k=self.k,
                m=self.m,
                random_state=self.random_state
            )
            return sampler.fit_resample(X, y)
    
    def _ensemble_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensemble resampling: combine samples from multiple CT values.
        
        This improves robustness by not relying on a single CT value.
        """
        if self.verbose >= 1:
            print(f"\n🔄 Ensemble Resampling with {len(self.top_cts_)} CT values")
        
        all_X = [X]
        all_y = [y]
        
        # Generate samples from each top CT
        for ct, score in self.top_cts_:
            sampler = SyMProD(ct=ct, k=self.k, m=self.m, random_state=self.random_state)
            X_res, y_res = sampler.fit_resample(X, y)
            
            # Keep only synthetic samples (exclude originals)
            n_original = len(X)
            X_syn = X_res[n_original:]
            y_syn = y_res[n_original:]
            
            # Weight by score
            n_keep = int(len(X_syn) * score / self.best_score_)
            if n_keep > 0 and len(X_syn) > 0:
                indices = self._rng.choice(len(X_syn), min(n_keep, len(X_syn)), replace=False)
                all_X.append(X_syn[indices])
                all_y.append(y_syn[indices])
        
        # Combine all
        X_final = np.vstack(all_X)
        y_final = np.hstack(all_y)
        
        if self.verbose >= 1:
            print(f"   Combined: {len(X)} → {len(X_final)} samples")
        
        return X_final, y_final
    
    def get_search_history(self) -> List[Dict]:
        """Get search history."""
        return self.search_history_.copy()


class MetaAdaptiveSyMProD:
    """
    Meta-learning variant that uses dataset characteristics to guide CT selection.
    
    Uses precomputed rules based on dataset statistics (IR, n_samples, n_features).
    """
    
    def __init__(
        self,
        k: int = 5,
        m: int = 100,
        random_state: Optional[int] = None
    ):
        self.k = k
        self.m = m
        self.random_state = random_state
        
        # Meta-rules based on expected performance
        self.meta_rules = {
            'high_ir': {  # IR > 5
                'ct_range': (0.5, 1.0),
                'recommended': 0.7
            },
            'medium_ir': {  # 2 <= IR <= 5
                'ct_range': (0.8, 1.5),
                'recommended': 1.0
            },
            'low_ir': {  # IR < 2
                'ct_range': (1.0, 2.0),
                'recommended': 1.3
            },
            'small_dataset': {  # n < 5000
                'n_repeats': 5,  # More repeats for stability
            },
            'large_dataset': {  # n >= 5000
                'n_repeats': 2,  # Fewer repeats for speed
            }
        }
    
    def fit_resample(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Resample using meta-rules."""
        X = np.asarray(X)
        y = np.asarray(y)
        
        # Compute dataset statistics
        n_samples = len(X)
        n_minority = np.sum(y == 1)
        n_majority = np.sum(y == 0)
        ir = n_majority / n_minority if n_minority > 0 else 1.0
        
        # Determine CT range based on IR
        if ir > 5:
            category = 'high_ir'
            ct_start, ct_end = 0.5, 1.0
        elif ir >= 2:
            category = 'medium_ir'
            ct_start, ct_end = 0.8, 1.5
        else:
            category = 'low_ir'
            ct_start, ct_end = 1.0, 2.0
        
        # Determine n_repeats based on dataset size
        n_repeats = 5 if n_samples < 5000 else 2
        
        # Use V2 with meta-determined parameters
        sampler = AdaptiveSyMProDV2(
            ct_range=(ct_start, ct_end),
            search_strategy='adaptive',
            n_repeats=n_repeats,
            cv_folds=3,
            use_ensemble=True,
            k=self.k,
            m=self.m,
            random_state=self.random_state,
            verbose=0
        )
        
        return sampler.fit_resample(X, y)
