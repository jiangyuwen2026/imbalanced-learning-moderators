#!/usr/bin/env python3
"""
Validation of Separability Measure Predictive Validity

This script validates whether the proposed separability measure (Eq. 2 in paper)
actually predicts oversampling effectiveness on real datasets.

Expected outcome: r(S, Delta_AUC) ≈ -0.72 (consistent with paper's claim)
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# Dataset configurations from Table 1
datasets_config = [
    {'name': 'sonar', 'openml_id': 40, 'target': 'class'},
    {'name': 'wdbc', 'openml_id': 1510, 'target': 'Class'},
    {'name': 'ionosphere', 'openml_id': 148, 'target': 'class'},
    {'name': 'breast-wisc', 'openml_id': 15, 'target': 'Class'},
    {'name': 'credit-g', 'openml_id': 31, 'target': 'class'},
    {'name': 'churn', 'openml_id': 40701, 'target': 'class'},
    {'name': 'optdigits', 'openml_id': 980, 'target': 'class'},
    {'name': 'satimage', 'openml_id': 182, 'target': 'class'},
    {'name': 'pendigits', 'openml_id': 32, 'target': 'class'},
    {'name': 'balance', 'openml_id': 11, 'target': 'class'},
    {'name': 'wilt', 'openml_id': 40983, 'target': 'class'},
    {'name': 'glass', 'openml_id': 41, 'target': 'Type'},
    {'name': 'letter', 'openml_id': 6, 'target': 'class'},
    {'name': 'mammography', 'openml_id': 310, 'target': 'class'},
    {'name': 'ecoli', 'openml_id': 39, 'target': 'class'},
    {'name': 'page-blocks', 'openml_id': 30, 'target': 'class'},
]


def calculate_separability(X, y):
    """
    Calculate class separability measure from Eq. 2 in paper.
    S = ||mu_maj - mu_min|| / sqrt((sigma^2_maj + sigma^2_min)/2)
    
    Returns separability score S.
    """
    classes = np.unique(y)
    if len(classes) != 2:
        raise ValueError("Only binary classification supported")
    
    # Identify majority and minority classes
    class_counts = [np.sum(y == c) for c in classes]
    maj_class = classes[np.argmax(class_counts)]
    min_class = classes[np.argmin(class_counts)]
    
    # Get samples for each class
    X_maj = X[y == maj_class]
    X_min = X[y == min_class]
    
    # Calculate means
    mu_maj = np.mean(X_maj, axis=0)
    mu_min = np.mean(X_min, axis=0)
    
    # Calculate variances (mean of variances across features)
    sigma2_maj = np.mean(np.var(X_maj, axis=0))
    sigma2_min = np.mean(np.var(X_min, axis=0))
    
    # Separability measure
    numerator = np.linalg.norm(mu_maj - mu_min)
    denominator = np.sqrt((sigma2_maj + sigma2_min) / 2)
    
    S = numerator / denominator if denominator > 0 else 0
    return S


def evaluate_smote_improvement(X, y, n_splits=5):
    """
    Evaluate SMOTE improvement over baseline on a dataset.
    
    Returns: Delta_AUC = AUC(SMOTE) - AUC(Baseline)
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    auc_baseline = []
    auc_smote = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Baseline (no oversampling)
        clf_base = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_base.fit(X_train, y_train)
        y_pred_base = clf_base.predict_proba(X_test)[:, 1]
        auc_baseline.append(roc_auc_score(y_test, y_pred_base))
        
        # With SMOTE
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        clf_smote = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_smote.fit(X_train_res, y_train_res)
        y_pred_smote = clf_smote.predict_proba(X_test)[:, 1]
        auc_smote.append(roc_auc_score(y_test, y_pred_smote))
    
    delta_auc = np.mean(auc_smote) - np.mean(auc_baseline)
    return delta_auc


def main():
    print("=" * 70)
    print("VALIDATION OF SEPARABILITY MEASURE PREDICTIVE VALIDITY")
    print("=" * 70)
    print()
    
    results = []
    
    for config in datasets_config:
        name = config['name']
        print(f"Processing {name}...", end=" ")
        
        try:
            # Fetch dataset
            data = fetch_openml(data_id=config['openml_id'], as_frame=True, parser='auto')
            X = data.data
            y = data.target
            
            # Handle categorical features
            X = pd.get_dummies(X, dummy_na=True)
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Encode labels
            le = LabelEncoder()
            y = le.fit_transform(y)
            
            # Ensure binary
            if len(np.unique(y)) != 2:
                print(f"SKIPPED (not binary: {len(np.unique(y))} classes)")
                continue
            
            # Convert to numpy
            X = X.values.astype(float)
            
            # Standardize
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # Calculate separability
            S = calculate_separability(X, y)
            
            # Evaluate SMOTE improvement
            delta_auc = evaluate_smote_improvement(X, y)
            
            results.append({
                'dataset': name,
                'separability_S': S,
                'delta_auc': delta_auc
            })
            
            print(f"S={S:.3f}, ΔAUC={delta_auc:+.4f}")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
            continue
    
    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    if len(results) < 5:
        print(f"ERROR: Only {len(results)} datasets processed. Need at least 5 for correlation analysis.")
        return
    
    df = pd.DataFrame(results)
    
    # Calculate correlation
    r, p_value = stats.pearsonr(df['separability_S'], df['delta_auc'])
    
    print(f"\nDatasets processed: {len(results)}")
    print(f"\nCorrelation Analysis:")
    print(f"  r(S, ΔAUC) = {r:.3f}")
    print(f"  p-value = {p_value:.4f}")
    print(f"  95% CI = [{r - 1.96*np.sqrt((1-r**2)/(len(results)-2)):.3f}, "
          f"{r + 1.96*np.sqrt((1-r**2)/(len(results)-2)):.3f}]")
    
    print(f"\nExpected from paper: ρ = -0.72 (p = 0.003)")
    print(f"Validation result: ρ = {r:.2f} (p = {p_value:.3f})")
    
    if r < -0.5 and p_value < 0.05:
        print("\n✓ VALIDATED: Separability measure shows expected negative correlation with SMOTE effectiveness")
    elif r < 0 and p_value < 0.1:
        print("\n~ PARTIALLY VALIDATED: Negative correlation observed but weaker than expected")
    else:
        print("\n✗ NOT VALIDATED: Correlation does not match expected pattern")
    
    print()
    print("Detailed Results:")
    print(df.to_string(index=False))
    
    # Save results
    df.to_csv('separability_validation_results.csv', index=False)
    print(f"\nResults saved to: separability_validation_results.csv")
    
    # Generate simple plot if matplotlib available
    try:
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(df['separability_S'], df['delta_auc'], s=100, alpha=0.6)
        
        # Add trend line
        z = np.polyfit(df['separability_S'], df['delta_auc'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df['separability_S'].min(), df['separability_S'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', alpha=0.8, label=f'r = {r:.3f}')
        
        # Labels
        for i, row in df.iterrows():
            ax.annotate(row['dataset'], (row['separability_S'], row['delta_auc']),
                       fontsize=8, alpha=0.7)
        
        ax.set_xlabel('Class Separability (S)', fontsize=12)
        ax.set_ylabel('SMOTE Improvement (ΔAUC)', fontsize=12)
        ax.set_title('Separability vs. SMOTE Effectiveness\n(Validation on Real Datasets)', fontsize=13)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('separability_validation_plot.png', dpi=300, bbox_inches='tight')
        plt.savefig('separability_validation_plot.pdf', bbox_inches='tight')
        print("Plot saved to: separability_validation_plot.png/pdf")
        
    except ImportError:
        print("Matplotlib not available, skipping plot generation")


if __name__ == '__main__':
    main()
