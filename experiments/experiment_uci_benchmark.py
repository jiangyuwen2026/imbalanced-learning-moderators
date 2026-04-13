#!/usr/bin/env python3
"""
Experiment: Compare SyMProD and Adaptive-SyMProD on UCI Benchmark Datasets

Datasets: 9 UCI datasets (processed for binary classification)
Methods: Baseline, SMOTE, SyMProD (fixed CT), Adaptive-SyMProD
Metrics: AUC, F1, G-Mean
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from src.symprod import SyMProD
from src.adaptive_symprod import AdaptiveSyMProD
from src.metrics import compute_metrics

# Dataset configuration
DATASETS = {
    'ecoli': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/ecoli/ecoli_binary.csv',
    'glass': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/glass/glass_binary.csv',
    'haberman': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/haberman/haberman_binary.csv',
    'ionosphere': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/ionosphere/ionosphere_binary.csv',
    'pima': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/pima/pima_binary.csv',
    'wine': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/wine/wine_binary.csv',
    'yeast': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/yeast/yeast_binary.csv',
    'abalone': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/abalone/abalone_binary.csv',
    'bank': '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/bank/bank_binary.csv',
}


def load_dataset(name, path):
    """Load and preprocess dataset."""
    df = pd.read_csv(path)
    
    # Find target column
    if 'binary_class' in df.columns:
        y = df['binary_class'].values
        X = df.drop('binary_class', axis=1)
    else:
        y = df.iloc[:, -1].values
        X = df.iloc[:, :-1]
    
    # Select only numeric columns
    X = X.select_dtypes(include=[np.number])
    
    # Handle any NaN values
    X = X.fillna(X.mean())
    
    return X.values, y


def evaluate_method(X, y, sampler, classifier, cv_folds=5, random_state=42):
    """Evaluate a method using cross-validation."""
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    auc_scores = []
    f1_scores = []
    gmean_scores = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Apply sampling
        if sampler is not None:
            try:
                X_res, y_res = sampler.fit_resample(X_train_scaled, y_train)
            except:
                X_res, y_res = X_train_scaled, y_train
        else:
            X_res, y_res = X_train_scaled, y_train
        
        # Train classifier
        clf = classifier
        clf.fit(X_res, y_res)
        
        # Predict
        if hasattr(clf, 'predict_proba'):
            y_prob = clf.predict_proba(X_test_scaled)[:, 1]
        else:
            y_prob = clf.predict(X_test_scaled)
        
        # Compute metrics
        auc = roc_auc_score(y_test, y_prob)
        y_pred = (y_prob > 0.5).astype(int)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # G-Mean
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            gmean = np.sqrt(sensitivity * specificity)
        else:
            gmean = 0
        
        auc_scores.append(auc)
        f1_scores.append(f1)
        gmean_scores.append(gmean)
    
    return {
        'auc_mean': np.mean(auc_scores),
        'auc_std': np.std(auc_scores),
        'f1_mean': np.mean(f1_scores),
        'f1_std': np.std(f1_scores),
        'gmean_mean': np.mean(gmean_scores),
        'gmean_std': np.std(gmean_scores),
    }


def run_experiment(dataset_name, X, y):
    """Run experiment on a single dataset."""
    print(f"\n{'='*70}")
    print(f"📊 Dataset: {dataset_name}")
    print(f"   Samples: {len(X)}, Features: {X.shape[1]}")
    print(f"   IR: {np.sum(y==0)/np.sum(y==1):.2f}:1")
    print(f"{'='*70}")
    
    results = {}
    
    # Classifier
    clf = LogisticRegression(max_iter=1000, random_state=42)
    
    # 1. Baseline
    print("\n  Testing Baseline...")
    results['Baseline'] = evaluate_method(X, y, None, clf)
    
    # 2. SyMProD with different CT values
    for ct in [0.8, 1.0, 1.2]:
        print(f"  Testing SyMProD (CT={ct})...")
        sampler = SyMProD(ct=ct, random_state=42)
        results[f'SyMProD_CT{ct}'] = evaluate_method(X, y, sampler, clf)
    
    # 3. Adaptive-SyMProD (simplified for speed)
    print("  Testing Adaptive-SyMProD...")
    sampler = AdaptiveSyMProD(
        ct_range=(0.5, 1.5),
        coarse_step=0.2,
        fine_step=0.05,
        cv_folds=2,
        verbose=0,
        random_state=42
    )
    results['Adaptive'] = evaluate_method(X, y, sampler, clf)
    
    # Print results
    print(f"\n  Results (AUC mean ± std):")
    print(f"  {'Method':<20} {'AUC':>12} {'F1':>12} {'G-Mean':>12}")
    print(f"  {'-'*60}")
    for method, metrics in results.items():
        print(f"  {method:<20} "
              f"{metrics['auc_mean']:>6.4f}±{metrics['auc_std']:<4.4f} "
              f"{metrics['f1_mean']:>6.4f}±{metrics['f1_std']:<4.4f} "
              f"{metrics['gmean_mean']:>6.4f}±{metrics['gmean_std']:<4.4f}")
    
    return results


def main():
    """Main experiment."""
    print("="*70)
    print("🚀 UCI Benchmark Experiment: SyMProD vs Adaptive-SyMProD")
    print("="*70)
    print(f"Datasets: {len(DATASETS)}")
    print(f"Methods: Baseline, SyMProD (CT=0.8,1.0,1.2), Adaptive-SyMProD")
    print(f"Classifier: Logistic Regression")
    print(f"CV: 5-fold Stratified")
    
    all_results = {}
    
    for name, path in DATASETS.items():
        if not os.path.exists(path):
            print(f"\n⚠️  Dataset {name} not found, skipping...")
            continue
        
        try:
            X, y = load_dataset(name, path)
            results = run_experiment(name, X, y)
            all_results[name] = results
        except Exception as e:
            print(f"\n❌ Error processing {name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Overall summary
    print("\n" + "="*70)
    print("📊 OVERALL SUMMARY")
    print("="*70)
    
    # Aggregate AUC across datasets
    methods = ['Baseline', 'SyMProD_CT0.8', 'SyMProD_CT1.0', 'SyMProD_CT1.2', 'Adaptive']
    method_auc = {m: [] for m in methods}
    
    for dataset, results in all_results.items():
        for method in methods:
            if method in results:
                method_auc[method].append(results[method]['auc_mean'])
    
    print(f"\n{'Method':<20} {'Mean AUC':>12} {'Std AUC':>12} {'Avg Rank':>12}")
    print(f"{'-'*60}")
    
    # Compute average ranks
    ranks = {m: [] for m in methods}
    for dataset in all_results.keys():
        dataset_aucs = [(m, all_results[dataset][m]['auc_mean']) for m in methods if m in all_results[dataset]]
        dataset_aucs.sort(key=lambda x: x[1], reverse=True)
        for rank, (method, _) in enumerate(dataset_aucs, 1):
            ranks[method].append(rank)
    
    # Print summary
    for method in methods:
        if method_auc[method]:
            mean_auc = np.mean(method_auc[method])
            std_auc = np.std(method_auc[method])
            mean_rank = np.mean(ranks[method])
            print(f"{method:<20} {mean_auc:>12.4f} {std_auc:>12.4f} {mean_rank:>12.2f}")
    
    # Save results
    results_df = []
    for dataset, results in all_results.items():
        for method, metrics in results.items():
            results_df.append({
                'dataset': dataset,
                'method': method,
                **metrics
            })
    
    df = pd.DataFrame(results_df)
    output_path = '/Users/jiangyuwen/Research/不均衡样本/Results/uci_benchmark_results.csv'
    df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    print("\n" + "="*70)
    print("✅ Experiment completed!")
    print("="*70)


if __name__ == "__main__":
    main()
