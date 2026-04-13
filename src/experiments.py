"""
Experimental Framework for Adaptive-SyMProD

Provides:
    - Complete experiment pipeline
    - Comparison with baseline methods
    - Statistical significance testing
    - Result persistence
"""

import numpy as np
import pickle
import json
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.base import clone
import warnings

from .metrics import compute_metrics, MetricsTracker
from .symprod import SyMProD
from .adaptive_symprod import AdaptiveSyMProD


class ExperimentRunner:
    """
    Complete experimental framework for comparing oversampling methods.
    
    Parameters
    ----------
    random_state : int, default=42
        Random seed for reproducibility
    verbose : int, default=1
        Verbosity level
    output_dir : str, optional
        Directory to save results
    
    Attributes
    ----------
    tracker : MetricsTracker
        Tracks all experimental results
    """
    
    def __init__(
        self,
        random_state: int = 42,
        verbose: int = 1,
        output_dir: Optional[str] = None
    ):
        self.random_state = random_state
        self.verbose = verbose
        self.output_dir = Path(output_dir) if output_dir else None
        self.tracker = MetricsTracker()
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_single_experiment(
        self,
        X: np.ndarray,
        y: np.ndarray,
        classifier,
        sampler=None,
        dataset_name: str = "dataset",
        method_name: str = "method",
        n_splits: int = 5,
        shuffle: bool = True
    ) -> Dict[str, Any]:
        """
        Run single experiment with cross-validation.
        
        Parameters
        ----------
        X, y : array-like
            Dataset
        classifier : estimator
            Classifier to use
        sampler : sampler, optional
            Oversampling method
        dataset_name : str
            Name of dataset
        method_name : str
            Name of method
        n_splits : int, default=5
            Number of CV folds
        shuffle : bool, default=True
            Whether to shuffle data
            
        Returns
        -------
        results : dict
            Aggregated results across folds
        """
        if self.verbose >= 1:
            print(f"\n{'='*60}")
            print(f"🧪 Experiment: {method_name} on {dataset_name}")
            print(f"{'='*60}")
            print(f"Dataset: {len(X)} samples, IR={np.sum(y==0)/np.sum(y==1):.2f}:1")
            print(f"CV: {n_splits}-fold Stratified")
        
        # Stratified K-Fold
        skf = StratifiedKFold(
            n_splits=n_splits,
            shuffle=shuffle,
            random_state=self.random_state
        )
        
        fold_results = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
            if self.verbose >= 2:
                print(f"\n  Fold {fold_idx + 1}/{n_splits}")
            
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Apply oversampling
            if sampler is not None:
                try:
                    X_train_res, y_train_res = sampler.fit_resample(X_train, y_train)
                    if self.verbose >= 2:
                        print(f"    Resampled: {len(y_train)} -> {len(y_train_res)}")
                except Exception as e:
                    warnings.warn(f"Sampler failed: {e}. Using original data.")
                    X_train_res, y_train_res = X_train, y_train
            else:
                X_train_res, y_train_res = X_train, y_train
            
            # Train and evaluate
            clf = clone(classifier)
            clf.fit(X_train_res, y_train_res)
            
            # Predict
            if hasattr(clf, 'predict_proba'):
                y_prob = clf.predict_proba(X_test)[:, 1]
            else:
                y_prob = clf.predict(X_test)
            
            # Compute metrics
            metrics = compute_metrics(y_test, y_prob)
            metrics['fold'] = fold_idx
            fold_results.append(metrics)
        
        # Aggregate results
        aggregated = self._aggregate_fold_results(fold_results)
        aggregated['dataset'] = dataset_name
        aggregated['method'] = method_name
        aggregated['n_folds'] = n_splits
        
        # Track result
        self.tracker.add_result(
            method=method_name,
            dataset=dataset_name,
            metrics=aggregated
        )
        
        if self.verbose >= 1:
            print(f"\n  Results (mean ± std):")
            print(f"    AUC: {aggregated['auc']:.4f} ± {aggregated['auc_std']:.4f}")
            print(f"    KS:  {aggregated['ks']:.4f} ± {aggregated['ks_std']:.4f}")
            print(f"    F1:  {aggregated['f1']:.4f} ± {aggregated['f1_std']:.4f}")
        
        return aggregated
    
    def _aggregate_fold_results(self, fold_results: List[Dict]) -> Dict:
        """Aggregate results across CV folds."""
        metrics_to_aggregate = ['auc', 'ks', 'f1', 'gmean', 'precision', 'recall']
        
        aggregated = {}
        for metric in metrics_to_aggregate:
            values = [r[metric] for r in fold_results if metric in r]
            aggregated[metric] = np.mean(values)
            aggregated[f'{metric}_std'] = np.std(values)
        
        aggregated['all_folds'] = fold_results
        return aggregated
    
    def compare_methods(
        self,
        X: np.ndarray,
        y: np.ndarray,
        classifier,
        samplers: Dict[str, Any],
        dataset_name: str = "dataset",
        n_splits: int = 5
    ) -> Dict[str, Dict]:
        """
        Compare multiple oversampling methods.
        
        Parameters
        ----------
        X, y : array-like
            Dataset
        classifier : estimator
            Classifier to use
        samplers : dict
            Dictionary mapping method names to samplers
        dataset_name : str
            Name of dataset
        n_splits : int
            Number of CV folds
            
        Returns
        -------
        comparison : dict
            Results for each method
        """
        results = {}
        
        for method_name, sampler in samplers.items():
            results[method_name] = self.run_single_experiment(
                X=X, y=y,
                classifier=classifier,
                sampler=sampler,
                dataset_name=dataset_name,
                method_name=method_name,
                n_splits=n_splits
            )
        
        return results
    
    def run_full_experiment(
        self,
        datasets: Dict[str, tuple],
        classifiers: Dict[str, Any],
        samplers: Dict[str, Any],
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Run full experimental comparison across datasets and classifiers.
        
        Parameters
        ----------
        datasets : dict
            Dictionary mapping dataset names to (X, y) tuples
        classifiers : dict
            Dictionary mapping classifier names to estimators
        samplers : dict
            Dictionary mapping sampler names to samplers
        n_splits : int
            Number of CV folds
            
        Returns
        -------
        all_results : dict
            Complete experimental results
        """
        all_results = {}
        
        for dataset_name, (X, y) in datasets.items():
            dataset_results = {}
            
            for clf_name, classifier in classifiers.items():
                if self.verbose >= 1:
                    print(f"\n{'#'*70}")
                    print(f"# Dataset: {dataset_name} | Classifier: {clf_name}")
                    print(f"{'#'*70}")
                
                comparison = self.compare_methods(
                    X=X, y=y,
                    classifier=classifier,
                    samplers=samplers,
                    dataset_name=f"{dataset_name}_{clf_name}",
                    n_splits=n_splits
                )
                
                dataset_results[clf_name] = comparison
            
            all_results[dataset_name] = dataset_results
        
        # Save results
        if self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.output_dir / f"results_{timestamp}.pkl"
            with open(results_file, 'wb') as f:
                pickle.dump(all_results, f)
            
            if self.verbose >= 1:
                print(f"\n💾 Results saved to: {results_file}")
        
        return all_results
    
    def statistical_test(
        self,
        method1: str,
        method2: str,
        metric: str = 'auc',
        dataset_filter: Optional[str] = None
    ) -> Dict:
        """
        Perform statistical significance test between two methods.
        
        Uses Wilcoxon signed-rank test (non-parametric paired test).
        
        Parameters
        ----------
        method1, method2 : str
            Names of methods to compare
        metric : str, default='auc'
            Metric to compare
        dataset_filter : str, optional
            Filter results by dataset name
            
        Returns
        -------
        test_result : dict
            Statistical test results
        """
        from scipy.stats import wilcoxon, ranksums
        
        results = self.tracker.get_results()
        
        # Filter results
        if dataset_filter:
            results = [r for r in results if dataset_filter in r.get('dataset', '')]
        
        # Extract values for each method
        values1 = [r[metric] for r in results if r.get('method') == method1]
        values2 = [r[metric] for r in results if r.get('method') == method2]
        
        if len(values1) != len(values2) or len(values1) == 0:
            return {'error': 'Insufficient or mismatched data'}
        
        # Wilcoxon signed-rank test (paired)
        try:
            statistic, pvalue = wilcoxon(values1, values2)
            test_name = 'Wilcoxon'
        except:
            # Fallback to ranksums if wilcoxon fails
            statistic, pvalue = ranksums(values1, values2)
            test_name = 'Ranksums'
        
        return {
            'test': test_name,
            'method1': method1,
            'method2': method2,
            'metric': metric,
            'n_samples': len(values1),
            'mean1': np.mean(values1),
            'mean2': np.mean(values2),
            'statistic': statistic,
            'pvalue': pvalue,
            'significant': pvalue < 0.05
        }
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate experimental report.
        
        Parameters
        ----------
        output_file : str, optional
            Path to save report
            
        Returns
        -------
        report : str
            Formatted report text
        """
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("Adaptive-SyMProD Experimental Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("="*80)
        
        # Get all results
        results_df = self.tracker.to_dataframe()
        
        if len(results_df) == 0:
            report_lines.append("\nNo results to report.")
            return "\n".join(report_lines)
        
        # Summary by method
        report_lines.append("\n" + "-"*80)
        report_lines.append("Results by Method (Mean ± Std)")
        report_lines.append("-"*80)
        
        summary = self.tracker.get_summary('auc')
        for method, stats in sorted(summary.items()):
            report_lines.append(
                f"{method:30s} AUC: {stats['mean']:.4f} ± {stats['std']:.4f} "
                f"[{stats['min']:.4f}, {stats['max']:.4f}] (n={stats['count']})"
            )
        
        # Ranking
        report_lines.append("\n" + "-"*80)
        report_lines.append("Method Ranking (by AUC)")
        report_lines.append("-"*80)
        
        ranked = sorted(summary.items(), key=lambda x: x[1]['mean'], reverse=True)
        for rank, (method, stats) in enumerate(ranked, 1):
            report_lines.append(f"{rank}. {method}: {stats['mean']:.4f}")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text


def create_baseline_samplers(random_state: int = 42) -> Dict[str, Any]:
    """
    Create dictionary of baseline samplers for comparison.
    
    Parameters
    ----------
    random_state : int
        Random seed
        
    Returns
    -------
    samplers : dict
        Dictionary of samplers
    """
    try:
        from imblearn.over_sampling import (
            SMOTE, BorderlineSMOTE, ADASYN,
            SVMSMOTE, KMeansSMOTE
        )
        from imblearn.combine import SMOTEENN, SMOTETomek
        
        samplers = {
            'None': None,
            'Random': 'random',  # Placeholder, will use RandomOverSampler
            'SMOTE': SMOTE(random_state=random_state),
            'BorderlineSMOTE': BorderlineSMOTE(random_state=random_state),
            'ADASYN': ADASYN(random_state=random_state),
            'SyMProD_CT0.8': SyMProD(ct=0.8, random_state=random_state),
            'SyMProD_CT1.0': SyMProD(ct=1.0, random_state=random_state),
            'SyMProD_CT1.2': SyMProD(ct=1.2, random_state=random_state),
            'AdaptiveSyMProD': AdaptiveSyMProD(random_state=random_state, verbose=0),
        }
        
        # Add optional samplers if available
        try:
            samplers['SVMSMOTE'] = SVMSMOTE(random_state=random_state)
        except:
            pass
            
        try:
            from imblearn.over_sampling import SMOTENC
            # For categorical features
        except:
            pass
        
    except ImportError:
        warnings.warn("imbalanced-learn not installed. Only SyMProD variants available.")
        samplers = {
            'None': None,
            'SyMProD_CT0.8': SyMProD(ct=0.8, random_state=random_state),
            'SyMProD_CT1.0': SyMProD(ct=1.0, random_state=random_state),
            'SyMProD_CT1.2': SyMProD(ct=1.2, random_state=random_state),
            'AdaptiveSyMProD': AdaptiveSyMProD(random_state=random_state, verbose=0),
        }
    
    return samplers


def create_classifiers(random_state: int = 42) -> Dict[str, Any]:
    """
    Create dictionary of classifiers for experiments.
    
    Parameters
    ----------
    random_state : int
        Random seed
        
    Returns
    -------
    classifiers : dict
        Dictionary of classifiers
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    
    classifiers = {
        'LR': LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            class_weight='balanced'
        ),
        'RF': RandomForestClassifier(
            n_estimators=100,
            random_state=random_state
        ),
        'GBDT': GradientBoostingClassifier(
            n_estimators=100,
            random_state=random_state
        ),
    }
    
    # Add XGBoost if available
    try:
        from xgboost import XGBClassifier
        classifiers['XGB'] = XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=random_state
        )
    except ImportError:
        pass
    
    return classifiers
