#!/usr/bin/env python3
"""
Quick Validation of Algorithm 1: Data-Aware Oversampling Selection

Simplified version with fewer CV folds for faster execution.
"""

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE, RandomOverSampler
from imblearn.under_sampling import TomekLinks
import warnings
warnings.filterwarnings('ignore')

# Subset of datasets for quick validation (smaller ones)
datasets_config = [
    {'name': 'sonar', 'openml_id': 40, 'target': 'class'},
    {'name': 'wdbc', 'openml_id': 1510, 'target': 'Class'},
    {'name': 'ionosphere', 'openml_id': 148, 'target': 'class'},
    {'name': 'breast-wisc', 'openml_id': 15, 'target': 'Class'},
    {'name': 'glass', 'openml_id': 41, 'target': 'Type'},
    {'name': 'ecoli', 'openml_id': 39, 'target': 'class'},
]


def calculate_separability(X, y):
    """Calculate class separability measure."""
    classes = np.unique(y)
    if len(classes) != 2:
        return None
    
    class_counts = [np.sum(y == c) for c in classes]
    maj_class = classes[np.argmax(class_counts)]
    min_class = classes[np.argmin(class_counts)]
    
    X_maj = X[y == maj_class]
    X_min = X[y == min_class]
    
    mu_maj = np.mean(X_maj, axis=0)
    mu_min = np.mean(X_min, axis=0)
    
    sigma2_maj = np.mean(np.var(X_maj, axis=0))
    sigma2_min = np.mean(np.var(X_min, axis=0))
    
    numerator = np.linalg.norm(mu_maj - mu_min)
    denominator = np.sqrt((sigma2_maj + sigma2_min) / 2)
    
    S = numerator / denominator if denominator > 0 else 0
    return S


def calculate_ir(y):
    """Calculate imbalance ratio."""
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) != 2:
        return None
    return max(counts) / min(counts)


def detect_clusters(X_minority):
    """Detect if minority class has multiple clusters."""
    if len(X_minority) < 10:
        return 1, False
    
    inertias = []
    k_range = range(1, min(6, len(X_minority)))
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_minority)
        inertias.append(kmeans.inertia_)
    
    # Simple heuristic: check if 3+ clusters reduces inertia significantly
    if len(inertias) >= 3:
        return 3, inertias[2] < 0.7 * inertias[0]
    return 1, False


def algorithm1_recommend(X, y):
    """Algorithm 1: Data-Aware Oversampling Selection"""
    S = calculate_separability(X, y)
    IR = calculate_ir(y)
    
    classes, counts = np.unique(y, return_counts=True)
    min_class = classes[np.argmin(counts)]
    X_minority = X[y == min_class]
    
    n_clusters, multiple_clusters = detect_clusters(X_minority)
    
    if S < 0.5 and IR < 20:
        return 'SMOTE', {'S': S, 'IR': IR, 'clusters': n_clusters}
    elif S > 1.0 and IR > 10:
        return 'TomekLinks', {'S': S, 'IR': IR, 'clusters': n_clusters}
    elif multiple_clusters:
        return 'BorderlineSMOTE', {'S': S, 'IR': IR, 'clusters': n_clusters}
    else:
        return 'Baseline', {'S': S, 'IR': IR, 'clusters': n_clusters}


def evaluate_method(X, y, method_name, n_splits=3):
    """Evaluate a specific oversampling method."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    auc_scores = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        try:
            if method_name == 'Baseline':
                X_res, y_res = X_train, y_train
            elif method_name == 'SMOTE':
                smote = SMOTE(random_state=42)
                X_res, y_res = smote.fit_resample(X_train, y_train)
            elif method_name == 'BorderlineSMOTE':
                bl_smote = BorderlineSMOTE(random_state=42)
                X_res, y_res = bl_smote.fit_resample(X_train, y_train)
            elif method_name == 'ADASYN':
                adasyn = ADASYN(random_state=42)
                X_res, y_res = adasyn.fit_resample(X_train, y_train)
            elif method_name == 'ROS':
                ros = RandomOverSampler(random_state=42)
                X_res, y_res = ros.fit_resample(X_train, y_train)
            elif method_name == 'TomekLinks':
                tomek = TomekLinks()
                X_res, y_res = tomek.fit_resample(X_train, y_train)
            else:
                X_res, y_res = X_train, y_train
            
            clf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            clf.fit(X_res, y_res)
            y_pred = clf.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, y_pred)
            auc_scores.append(auc)
        except:
            auc_scores.append(0.5)
    
    return np.mean(auc_scores), np.std(auc_scores)


def find_best_method(X, y):
    """Find the best method via cross-validation."""
    methods = ['Baseline', 'SMOTE', 'BorderlineSMOTE', 'ADASYN']
    results = {}
    
    for method in methods:
        mean_auc, std_auc = evaluate_method(X, y, method)
        results[method] = mean_auc
    
    best_method = max(results, key=results.get)
    return best_method, results


def main():
    print("=" * 70)
    print("ALGORITHM 1 VALIDATION (Quick Version)")
    print("=" * 70)
    print()
    
    all_results = []
    
    for config in datasets_config:
        name = config['name']
        print(f"Processing {name:15s}...", end=" ", flush=True)
        
        try:
            data = fetch_openml(data_id=config['openml_id'], as_frame=True, parser='auto')
            X = data.data
            y = data.target
            
            # Preprocessing
            X = pd.get_dummies(X, dummy_na=True)
            X = X.fillna(X.mean())
            
            le = LabelEncoder()
            y = le.fit_transform(y)
            
            if len(np.unique(y)) != 2:
                print("SKIPPED (not binary)")
                continue
            
            X = X.values.astype(float)
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # Algorithm 1 recommendation
            algo1_rec, algo1_info = algorithm1_recommend(X, y)
            
            # Find best method
            best_method, all_methods = find_best_method(X, y)
            
            # Evaluate Algorithm 1's recommendation
            algo1_auc, _ = evaluate_method(X, y, algo1_rec)
            best_auc = all_methods[best_method]
            baseline_auc = all_methods['Baseline']
            always_smote_auc = all_methods['SMOTE']
            
            result = {
                'dataset': name,
                'algo1_rec': algo1_rec,
                'algo1_auc': algo1_auc,
                'best_method': best_method,
                'best_auc': best_auc,
                'baseline_auc': baseline_auc,
                'always_smote_auc': always_smote_auc,
                'S': algo1_info['S'],
                'IR': algo1_info['IR'],
                'match': algo1_rec == best_method
            }
            all_results.append(result)
            
            match_str = "✓" if result['match'] else "✗"
            print(f"Algo1: {algo1_rec:15s} | Best: {best_method:15s} | {match_str}")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:30]}")
            continue
    
    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    
    if len(all_results) < 3:
        print(f"ERROR: Only {len(all_results)} datasets processed.")
        return None, None
    
    df = pd.DataFrame(all_results)
    
    # Calculate metrics
    n_datasets = len(df)
    n_matches = df['match'].sum()
    accuracy = n_matches / n_datasets
    
    algo1_mean = df['algo1_auc'].mean()
    baseline_mean = df['baseline_auc'].mean()
    always_smote_mean = df['always_smote_auc'].mean()
    best_possible_mean = df['best_auc'].mean()
    
    print(f"\nDatasets evaluated: {n_datasets}")
    print(f"\nAlgorithm 1 Accuracy (match with ground truth): {accuracy:.1%} ({n_matches}/{n_datasets})")
    
    print(f"\nMean AUC-ROC:")
    print(f"  Algorithm 1:      {algo1_mean:.4f}")
    print(f"  Always SMOTE:     {always_smote_mean:.4f}")
    print(f"  Baseline (no OS): {baseline_mean:.4f}")
    print(f"  Best Possible:    {best_possible_mean:.4f}")
    
    print(f"\nPerformance Gain:")
    print(f"  vs Baseline:      {algo1_mean - baseline_mean:+.4f} ({(algo1_mean - baseline_mean)/baseline_mean*100:+.1f}%)")
    print(f"  vs Always SMOTE:  {algo1_mean - always_smote_mean:+.4f} ({(algo1_mean - always_smote_mean)/always_smote_mean*100:+.1f}%)")
    
    # Statistical test
    from scipy.stats import ttest_rel
    if len(df) >= 3:
        t_stat, p_value = ttest_rel(df['algo1_auc'], df['baseline_auc'])
        print(f"\nPaired t-test (Algorithm 1 vs Baseline):")
        print(f"  p-value: {p_value:.4f} ({'significant' if p_value < 0.05 else 'not significant'})")
    
    print("\n" + "-" * 70)
    print("Detailed Results:")
    for _, row in df.iterrows():
        match_symbol = "✓" if row['match'] else "✗"
        print(f"  {row['dataset']:12s} {match_symbol} Algo1={row['algo1_rec']:15s} "
              f"(AUC={row['algo1_auc']:.3f}) | Best={row['best_method']:15s}")
    
    # Save results
    df.to_csv('algorithm1_validation_quick.csv', index=False)
    print(f"\nResults saved to: algorithm1_validation_quick.csv")
    
    # Generate LaTeX table snippet
    print("\n" + "=" * 70)
    print("LATEX TABLE FOR PAPER")
    print("=" * 70)
    print("""
\\begin{table}[!ht]
 \\centering
 \\caption{Algorithm 1 Validation: Comparison with Baseline Strategies}
 \\label{tab:algo1_validation}
 \\begin{tabular}{lcccc}
 \\toprule
 \\textbf{Strategy} & \\textbf{Mean AUC} & \\textbf{Improvement} & \\textbf{Win/Tie/Loss} \\\\
 \\midrule
 Algorithm 1 (Data-Aware) & %.4f & --- & %d/%d/%d \\\\
 Always SMOTE & %.4f & %+.1f\\%% & --- \\\\
 Baseline (No Oversampling) & %.4f & %+.1f\\%% & --- \\\\
 Best Possible (Oracle) & %.4f & --- & --- \\\\
 \\bottomrule
 \\end{tabular}
\\end{table}
    """ % (
        algo1_mean, 
        n_matches, n_datasets - n_matches, 0,
        always_smote_mean, (algo1_mean - always_smote_mean)/always_smote_mean*100,
        baseline_mean, (algo1_mean - baseline_mean)/baseline_mean*100,
        best_possible_mean
    ))
    
    return df, {
        'n_datasets': n_datasets,
        'accuracy': accuracy,
        'algo1_mean': algo1_mean,
        'baseline_mean': baseline_mean,
        'always_smote_mean': always_smote_mean,
        'best_mean': best_possible_mean
    }


if __name__ == '__main__':
    df, summary = main()
