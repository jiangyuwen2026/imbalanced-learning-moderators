#!/usr/bin/env python3
"""
Experiment: Adaptive-SyMProD on Lending Club Dataset

Expected Data Location: Data/raw/lending_club/loan.csv
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score
import warnings
warnings.filterwarnings('ignore')

from src.symprod import SyMProD
from src.adaptive_symprod import AdaptiveSyMProD
from src.metrics import compute_metrics


def load_and_preprocess_lending_club(data_path):
    """Load and preprocess Lending Club dataset."""
    print("Loading Lending Club dataset...")
    print(f"Path: {data_path}")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    
    # Read data (sample if too large for quick test)
    df = pd.read_csv(data_path)
    print(f"Original shape: {df.shape}")
    
    # Filter for completed loans
    df = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])]
    
    # Create binary target
    df['target'] = (df['loan_status'] == 'Charged Off').astype(int)
    
    # Select numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['target', 'id', 'member_id']]
    
    # Sample for faster experimentation (optional)
    if len(df) > 50000:
        print(f"Sampling 50,000 from {len(df)} for faster experimentation")
        df = df.sample(n=50000, random_state=42, stratify=df['target'])
    
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    y = df['target'].values
    
    print(f"Final shape: X={X.shape}, y={y.shape}")
    print(f"Class distribution: {np.bincount(y)} (IR={np.sum(y==0)/np.sum(y==1):.2f}:1)")
    
    return X.values, y, numeric_cols


def evaluate_methods(X, y, methods, cv_folds=3):
    """Evaluate multiple methods."""
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    results = {method: {'auc': [], 'f1': [], 'time': []} for method in methods.keys()}
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n  Fold {fold + 1}/{cv_folds}")
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        for method_name, sampler in methods.items():
            import time
            start = time.time()
            
            # Apply sampling
            if sampler is not None:
                try:
                    X_res, y_res = sampler.fit_resample(X_train_scaled, y_train)
                except Exception as e:
                    print(f"    {method_name}: Sampling failed - {e}")
                    X_res, y_res = X_train_scaled, y_train
            else:
                X_res, y_res = X_train_scaled, y_train
            
            # Train
            clf = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
            clf.fit(X_res, y_res)
            
            # Predict
            y_prob = clf.predict_proba(X_test_scaled)[:, 1]
            y_pred = (y_prob > 0.5).astype(int)
            
            # Metrics
            auc = roc_auc_score(y_test, y_prob)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            elapsed = time.time() - start
            
            results[method_name]['auc'].append(auc)
            results[method_name]['f1'].append(f1)
            results[method_name]['time'].append(elapsed)
            
            print(f"    {method_name}: AUC={auc:.4f}, F1={f1:.4f}, Time={elapsed:.2f}s")
    
    # Aggregate
    summary = {}
    for method_name, metrics in results.items():
        summary[method_name] = {
            'auc_mean': np.mean(metrics['auc']),
            'auc_std': np.std(metrics['auc']),
            'f1_mean': np.mean(metrics['f1']),
            'f1_std': np.std(metrics['f1']),
            'time_mean': np.mean(metrics['time']),
        }
    
    return summary


def main():
    """Main experiment."""
    print("="*70)
    print("🚀 Lending Club Experiment: Adaptive-SyMProD")
    print("="*70)
    
    # Check for dataset
    data_path = '/Users/jiangyuwen/Research/不均衡样本/Data/raw/lending_club/loan.csv'
    
    if not os.path.exists(data_path):
        print(f"\n❌ Dataset not found: {data_path}")
        print("\nPlease download the dataset first:")
        print("1. Visit: https://www.kaggle.com/datasets/wendykan/lending-club-loan-data")
        print("2. Click 'Download'")
        print("3. Extract to: Data/raw/lending_club/")
        print("\nOr use alternative: Give Me Some Credit dataset")
        return
    
    # Load data
    try:
        X, y, feature_names = load_and_preprocess_lending_club(data_path)
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        return
    
    # Define methods
    print("\n" + "="*70)
    print("📊 Evaluating Methods")
    print("="*70)
    
    methods = {
        'Baseline': None,
        'SMOTE': 'smote_placeholder',  # Will use imblearn if available
        'SyMProD_CT1.0': SyMProD(ct=1.0, random_state=42),
        'Adaptive': AdaptiveSyMProD(
            ct_range=(0.5, 1.5),
            coarse_step=0.2,
            fine_step=0.05,
            cv_folds=2,
            verbose=1,
            random_state=42
        )
    }
    
    # Try to use imblearn SMOTE
    try:
        from imblearn.over_sampling import SMOTE
        methods['SMOTE'] = SMOTE(random_state=42)
    except ImportError:
        print("⚠️  imblearn not available, skipping SMOTE")
        del methods['SMOTE']
    
    # Run evaluation
    results = evaluate_methods(X, y, methods, cv_folds=3)
    
    # Print summary
    print("\n" + "="*70)
    print("📈 Results Summary")
    print("="*70)
    print(f"{'Method':<20} {'AUC':>15} {'F1':>15} {'Time(s)':>10}")
    print("-"*70)
    
    for method_name, metrics in sorted(results.items(), 
                                        key=lambda x: x[1]['auc_mean'], 
                                        reverse=True):
        print(f"{method_name:<20} "
              f"{metrics['auc_mean']:>6.4f}±{metrics['auc_std']:<6.4f} "
              f"{metrics['f1_mean']:>6.4f}±{metrics['f1_std']:<6.4f} "
              f"{metrics['time_mean']:>10.2f}")
    
    # Save results
    results_df = []
    for method_name, metrics in results.items():
        results_df.append({
            'dataset': 'LendingClub',
            'method': method_name,
            **metrics
        })
    
    output_path = '/Users/jiangyuwen/Research/不均衡样本/Results/lending_club_results.csv'
    pd.DataFrame(results_df).to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    print("\n" + "="*70)
    print("✅ Experiment completed!")
    print("="*70)


if __name__ == "__main__":
    main()
