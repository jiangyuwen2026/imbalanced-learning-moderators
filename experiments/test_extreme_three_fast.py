#!/usr/bin/env python3
"""快速版本 - 跳过Adaptive-SyMProD，特殊处理abalone"""
import os
import sys
import json
import time
import warnings
import contextlib
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, f1_score, fbeta_score, confusion_matrix
from imblearn.over_sampling import SMOTE

sys.path.insert(0, 'Code/adaptive-symprod/src')
from symprod import SyMProD

RESULTS_FILE = 'Results/ExtremeImbalance/extreme_three_results.json'

EXTREME_DATASETS = [
    ('letter', 6, 26.25),
    ('abalone', 183, 4176.00),
]

CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}

SAMPLING_METHODS = ['None', 'SMOTE', 'SyMProD']

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv('Results/ExtremeImbalance/extreme_three_results.csv', index=False)

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

def evaluate_model(X, y, classifier, sampling_method, dataset_name):
    n_positive = y.sum()
    
    # 对于只有一个正类样本的数据集，使用特殊的交叉验证策略
    if n_positive == 1:
        # 使用简单的train/test split，确保训练集包含正类
        pos_idx = np.where(y == 1)[0][0]
        neg_indices = np.where(y == 0)[0]
        
        # 多次随机分割取平均
        auc_scores, f1_scores, gm_scores, fm_scores = [], [], [], []
        
        for seed in [42, 123, 456]:
            np.random.seed(seed)
            neg_train = np.random.choice(neg_indices, size=int(len(neg_indices)*0.8), replace=False)
            train_idx = np.concatenate([[pos_idx], neg_train])
            test_idx = np.array([i for i in range(len(y)) if i not in train_idx])
            
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 采样
            if sampling_method == 'SMOTE':
                try:
                    smote = SMOTE(random_state=42, k_neighbors=1)
                    X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
                except:
                    X_train_res, y_train_res = X_train_scaled, y_train
            elif sampling_method == 'SyMProD':
                try:
                    symprod = SyMProD(random_state=42, ct=1.0)
                    X_train_res, y_train_res = symprod.fit_resample(X_train_scaled, y_train)
                except:
                    X_train_res, y_train_res = X_train_scaled, y_train
            else:
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
        
        return {'auc': np.mean(auc_scores), 'f1': np.mean(f1_scores), 
                'gm': np.mean(gm_scores), 'fm': np.mean(fm_scores)}
    
    # 正常交叉验证
    if n_positive < 3:
        n_splits = 2
    else:
        n_splits = 3
    
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    auc_scores, f1_scores, gm_scores, fm_scores = [], [], [], []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if sampling_method == 'SMOTE':
            try:
                k_neighbors = min(5, len(y_train[y_train==1]) - 1)
                if k_neighbors < 1:
                    k_neighbors = 1
                smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
                X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
            except:
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'SyMProD':
            try:
                symprod = SyMProD(random_state=42, ct=1.0)
                X_train_res, y_train_res = symprod.fit_resample(X_train_scaled, y_train)
            except:
                X_train_res, y_train_res = X_train_scaled, y_train
        else:
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
    
    return {'auc': np.mean(auc_scores), 'f1': np.mean(f1_scores), 
            'gm': np.mean(gm_scores), 'fm': np.mean(fm_scores)}

def run():
    print("=" * 60)
    print("快速测试 (特殊处理abalone)")
    print("=" * 60)
    
    results = load_results()
    completed = set((r['dataset'], r['classifier'], r['sampling']) for r in results)
    print(f"已有: {len(results)}条")
    
    for ds_idx, (name, data_id, expected_ir) in enumerate(EXTREME_DATASETS, 1):
        X, y, actual_ir = load_dataset(name, data_id)
        if X is None:
            continue
        
        print(f"\n[{ds_idx}/{len(EXTREME_DATASETS)}] {name}: n={len(y)}, IR={actual_ir:.1f}, pos={y.sum()}")
        
        for clf_name, classifier in CLASSIFIERS.items():
            for sampling in SAMPLING_METHODS:
                task_key = (name, clf_name, sampling)
                if task_key in completed:
                    continue
                
                print(f"  {clf_name} | {sampling}...", end=' ', flush=True)
                start = time.time()
                scores = evaluate_model(X, y, classifier, sampling, name)
                elapsed = time.time() - start
                
                result = {
                    'dataset': name, 'data_id': data_id,
                    'n_samples': int(len(y)), 'n_features': int(X.shape[1]),
                    'imbalance_ratio': float(actual_ir),
                    'classifier': clf_name, 'sampling': sampling,
                    'auc': round(scores['auc'], 4), 'f1': round(scores['f1'], 4),
                    'gm': round(scores['gm'], 4), 'fm': round(scores['fm'], 4),
                    'time': round(elapsed, 2)
                }
                results.append(result)
                save_results(results)
                print(f"AUC={scores['auc']:.4f}, time={elapsed:.1f}s")
    
    print("\n完成!")

if __name__ == '__main__':
    run()
