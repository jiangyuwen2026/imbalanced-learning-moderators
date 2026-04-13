#!/usr/bin/env python3
"""
补测中度不平衡数据集的Adaptive-SyMProD
"""

import os
import sys
import json
import time
import warnings
import contextlib
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, f1_score, fbeta_score, confusion_matrix

sys.path.insert(0, 'Code/adaptive-symprod/src')
from adaptive_symprod_v4 import AdaptiveSyMProD

RESULTS_FILE = 'Results/ModerateImbalance/moderate_results.json'

MODERATE_DATASETS = [
    ('mammography', 310, 42.01),
    ('churn', 40701, 6.07),
    ('balance', 11, 11.76),
    ('optdigits', 28, 9.14),
    ('pendigits', 32, 9.42),
    ('satimage', 182, 9.29),
]

CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}


def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv('Results/ModerateImbalance/moderate_results.csv', index=False)


def load_dataset(name, data_id):
    csv_path = f'Data/OpenML_27/{name}.csv'
    if not os.path.exists(csv_path):
        return None, None, None
    df = pd.read_csv(csv_path)
    y = df['target'].values
    X = df.drop('target', axis=1)
    if X.isnull().any().any():
        X = X.fillna(X.median())
    X = X.values
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    ir = n_neg / max(n_pos, 1)
    return X, y, ir


def evaluate_adaptive(X, y, classifier, n_splits=3):
    """仅测试Adaptive-SyMProD"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    auc_scores, f1_scores, gm_scores, fm_scores = [], [], [], []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        try:
            adaptive = AdaptiveSyMProD(
                random_state=42, 
                search_strategy='hybrid',
                ct_range=(0.5, 1.5),
                cv_folds=2,
                max_iter=3,
                verbose=0
            )
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    X_train_res, y_train_res = adaptive.fit_resample(X_train_scaled, y_train)
        except Exception as e:
            print(f"[失败: {str(e)[:40]}]", end=' ')
            X_train_res, y_train_res = X_train_scaled, y_train
        
        clf = classifier.__class__(**classifier.get_params())
        clf.fit(X_train_res, y_train_res)
        
        y_pred = clf.predict(X_test_scaled)
        y_prob = clf.predict_proba(X_test_scaled)[:, 1] if hasattr(clf, 'predict_proba') else y_pred
        
        try:
            auc = roc_auc_score(y_test, y_prob)
        except:
            auc = 0.5
        
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            sensitivity = tp / max(tp + fn, 1)
            specificity = tn / max(tn + fp, 1)
            gm = np.sqrt(sensitivity * specificity)
        else:
            gm = 0
        
        f05 = fbeta_score(y_test, y_pred, beta=0.5, zero_division=0)
        f2 = fbeta_score(y_test, y_pred, beta=2, zero_division=0)
        fm = (f05 + f2) / 2
        
        auc_scores.append(auc)
        f1_scores.append(f1)
        gm_scores.append(gm)
        fm_scores.append(fm)
    
    return {
        'auc': np.mean(auc_scores),
        'f1': np.mean(f1_scores),
        'gm': np.mean(gm_scores),
        'fm': np.mean(fm_scores)
    }


def run_adaptive_tests():
    print("=" * 70)
    print("补测 Adaptive-SyMProD (中度不平衡数据集)")
    print("=" * 70)
    
    all_results = load_results()
    existing_adaptive = set((r['dataset'], r['classifier']) for r in all_results if r['sampling'] == 'Adaptive-SyMProD')
    
    print(f"已有Adaptive结果: {len(existing_adaptive)}条")
    print("=" * 70)
    
    count = 0
    for ds_idx, (name, data_id, expected_ir) in enumerate(MODERATE_DATASETS, 1):
        X, y, actual_ir = load_dataset(name, data_id)
        if X is None:
            continue
        
        for clf_name, classifier in CLASSIFIERS.items():
            if (name, clf_name) in existing_adaptive:
                print(f"[{ds_idx}/{len(MODERATE_DATASETS)}] {name} | {clf_name} | Adaptive-SyMProD... [跳过]")
                continue
            
            print(f"[{ds_idx}/{len(MODERATE_DATASETS)}] {name} | {clf_name} | Adaptive-SyMProD...", end=' ', flush=True)
            start_time = time.time()
            
            scores = evaluate_adaptive(X, y, classifier)
            elapsed = time.time() - start_time
            
            # 查找并更新现有记录，或添加新记录
            existing_idx = None
            for i, r in enumerate(all_results):
                if r['dataset'] == name and r['classifier'] == clf_name and r['sampling'] == 'Adaptive-SyMProD':
                    existing_idx = i
                    break
            
            result = {
                'dataset': name,
                'data_id': data_id,
                'n_samples': int(len(y)),
                'n_features': int(X.shape[1]),
                'imbalance_ratio': float(actual_ir),
                'classifier': clf_name,
                'sampling': 'Adaptive-SyMProD',
                'auc': round(scores['auc'], 4),
                'f1': round(scores['f1'], 4),
                'gm': round(scores['gm'], 4),
                'fm': round(scores['fm'], 4),
                'time': round(elapsed, 2)
            }
            
            if existing_idx is not None:
                all_results[existing_idx] = result
            else:
                all_results.append(result)
            
            save_results(all_results)
            count += 1
            print(f"AUC={scores['auc']:.4f}, time={elapsed:.1f}s [{count}]")
    
    print(f"\n完成！更新了{count}条Adaptive-SyMProD记录")


if __name__ == '__main__':
    run_adaptive_tests()
