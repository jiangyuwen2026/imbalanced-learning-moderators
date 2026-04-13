#!/usr/bin/env python3
"""
Experiment: Adaptive-SyMProD on Bank Marketing Dataset

This serves as a proxy for large-scale credit scoring (41K samples)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
import time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from src.symprod import SyMProD
from src.adaptive_symprod import AdaptiveSyMProD


def load_bank_marketing():
    """Load Bank Marketing dataset."""
    data_path = '/Users/jiangyuwen/Research/不均衡样本/Data/raw/uci_benchmark/bank/bank-additional/bank-additional-full.csv'
    
    print("Loading Bank Marketing dataset...")
    df = pd.read_csv(data_path, sep=';')
    
    # Binary target: 'yes' (subscribed) vs 'no' (not subscribed)
    y = (df['y'] == 'yes').astype(int).values
    
    # Select features (mix of numeric and categorical)
    # For simplicity, use only numeric features
    numeric_cols = ['age', 'duration', 'campaign', 'pdays', 'previous',
                   'emp.var.rate', 'cons.price.idx', 'cons.conf.idx',
                   'euribor3m', 'nr.employed']
    
    # Add encoded categorical features
    categorical_cols = ['job', 'marital', 'education', 'default', 'housing',
                       'loan', 'contact', 'month', 'day_of_week', 'poutcome']
    
    X_numeric = df[numeric_cols].values
    
    # Encode categorical features
    from sklearn.preprocessing import LabelEncoder
    X_categorical = []
    for col in categorical_cols:
        le = LabelEncoder()
        X_categorical.append(le.fit_transform(df[col].astype(str)))
    X_categorical = np.column_stack(X_categorical)
    
    X = np.hstack([X_numeric, X_categorical])
    
    print(f"Dataset shape: X={X.shape}, y={y.shape}")
    print(f"Class distribution: {np.bincount(y)} (IR={np.sum(y==0)/np.sum(y==1):.2f}:1)")
    
    return X, y


def evaluate_method(X, y, sampler, classifier, cv_folds=3):
    """Evaluate a single method."""
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    auc_scores = []
    f1_scores = []
    gmean_scores = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"    Fold {fold_idx + 1}/{cv_folds}...", end=" ")
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale
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
        
        # Train (single thread to avoid multiprocessing issues)
        clf = classifier
        clf.fit(X_res, y_res)
        
        # Predict
        y_prob = clf.predict_proba(X_test_scaled)[:, 1]
        y_pred = (y_prob > 0.5).astype(int)
        
        # Metrics
        auc = roc_auc_score(y_test, y_prob)
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
        print(f"AUC={auc:.4f}")
    
    return {
        'auc_mean': np.mean(auc_scores),
        'auc_std': np.std(auc_scores),
        'f1_mean': np.mean(f1_scores),
        'f1_std': np.std(f1_scores),
        'gmean_mean': np.mean(gmean_scores),
        'gmean_std': np.std(gmean_scores),
    }


def main():
    """Main experiment."""
    print("="*70)
    print("🚀 Bank Marketing Experiment: Large-Scale Credit Scoring Proxy")
    print("="*70)
    print("Dataset: Bank Marketing (41,188 samples)")
    print("IR: 7.88:1 (highly imbalanced)")
    print("Purpose: Validate Adaptive-SyMProD on large-scale data")
    print("="*70)
    
    # Load data
    X, y = load_bank_marketing()
    
    # Define methods
    methods = {
        'Baseline': None,
        'SyMProD_CT0.8': SyMProD(ct=0.8, random_state=42),
        'SyMProD_CT1.0': SyMProD(ct=1.0, random_state=42),
        'SyMProD_CT1.2': SyMProD(ct=1.2, random_state=42),
    }
    
    # Add Adaptive (this will take longer)
    print("\n⚠️  Adaptive-SyMProD will take longer due to CT optimization...")
    methods['Adaptive'] = AdaptiveSyMProD(
        ct_range=(0.5, 1.5),
        coarse_step=0.2,
        fine_step=0.05,
        cv_folds=3,
        verbose=1,
        random_state=42
    )
    
    # Evaluate
    results = {}
    
    print("\n" + "="*70)
    print("📊 Evaluating Methods (3-fold CV)")
    print("="*70)
    
    for method_name, sampler in methods.items():
        print(f"\n🔍 {method_name}...")
        start = time.time()
        
        clf = LogisticRegression(max_iter=1000, random_state=42)
        metrics = evaluate_method(X, y, sampler, clf, cv_folds=3)
        elapsed = time.time() - start
        
        results[method_name] = metrics
        results[method_name]['time'] = elapsed
        
        print(f"   AUC: {metrics['auc_mean']:.4f}±{metrics['auc_std']:.4f}")
        print(f"   F1:  {metrics['f1_mean']:.4f}±{metrics['f1_std']:.4f}")
        print(f"   G-Mean: {metrics['gmean_mean']:.4f}±{metrics['gmean_std']:.4f}")
        print(f"   Time: {elapsed:.2f}s")
        
        if hasattr(sampler, 'best_ct_'):
            print(f"   Optimal CT: {sampler.best_ct_:.2f}")
    
    # Summary
    print("\n" + "="*70)
    print("📈 Summary (sorted by AUC)")
    print("="*70)
    print(f"{'Method':<20} {'AUC':>15} {'F1':>15} {'G-Mean':>10} {'Time(s)':>10}")
    print("-"*70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['auc_mean'], reverse=True)
    for method_name, metrics in sorted_results:
        print(f"{method_name:<20} "
              f"{metrics['auc_mean']:>6.4f}±{metrics['auc_std']:<6.4f} "
              f"{metrics['f1_mean']:>6.4f}±{metrics['f1_std']:<6.4f} "
              f"{metrics['gmean_mean']:>10.4f} "
              f"{metrics['time']:>10.2f}")
    
    # Save results
    import json
    output_path = '/Users/jiangyuwen/Research/不均衡样本/Results/bank_marketing_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")
    
    # Analysis
    print("\n" + "="*70)
    print("💡 Key Findings")
    print("="*70)
    
    baseline_auc = results['Baseline']['auc_mean']
    adaptive_auc = results['Adaptive']['auc_mean']
    improvement = (adaptive_auc - baseline_auc) / baseline_auc * 100
    
    print(f"1. Baseline AUC: {baseline_auc:.4f}")
    print(f"2. Adaptive AUC: {adaptive_auc:.4f} ({improvement:+.2f}%)")
    
    # Find best fixed CT
    fixed_ct_methods = {k: v for k, v in results.items() if 'CT' in k}
    if fixed_ct_methods:
        best_fixed = max(fixed_ct_methods.items(), key=lambda x: x[1]['auc_mean'])
        print(f"3. Best Fixed CT: {best_fixed[0]} (AUC={best_fixed[1]['auc_mean']:.4f})")
        
        if adaptive_auc >= best_fixed[1]['auc_mean'] - 0.001:
            print(f"   ✅ Adaptive matches or beats best fixed CT!")
        else:
            diff = best_fixed[1]['auc_mean'] - adaptive_auc
            print(f"   ℹ️  Adaptive within {diff:.4f} of best fixed CT")
    
    # Time efficiency
    grid_search_time = sum(results[m]['time'] for m in ['SyMProD_CT0.8', 'SyMProD_CT1.0', 'SyMProD_CT1.2'])
    adaptive_time = results['Adaptive']['time']
    time_saved = (grid_search_time - adaptive_time) / grid_search_time * 100
    
    print(f"\n4. Time Efficiency:")
    print(f"   Grid search (3 CTs): {grid_search_time:.2f}s")
    print(f"   Adaptive: {adaptive_time:.2f}s")
    print(f"   Time saved: {time_saved:.1f}%")
    
    print("\n" + "="*70)
    print("✅ Experiment completed!")
    print("="*70)


if __name__ == "__main__":
    main()
