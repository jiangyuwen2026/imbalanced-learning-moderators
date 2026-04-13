#!/usr/bin/env python3
"""继续测试heart-statlog"""
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
from symprod import SyMProD
from adaptive_symprod_v4 import AdaptiveSyMProD

RESULTS_FILE = 'Results/ExtremeImbalance/heart_statlog_results.json'
NEGATIVE_SAMPLING_RATIO = 0.1

CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}
SAMPLING_METHODS = ['None', 'SMOTE', 'SyMProD', 'Adaptive-SyMProD']

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv('Results/ExtremeImbalance/heart_statlog_results.csv', index=False)

def load_and_sample_data():
    csv_path = 'Data/OpenML_27/heart-statlog.csv'
    df = pd.read_csv(csv_path)
    pos_samples = df[df['target'] == 1]
    neg_samples = df[df['target'] == 0]
    neg_sampled = neg_samples.sample(n=int(len(neg_samples) * NEGATIVE_SAMPLING_RATIO), random_state=42)
    df_sampled = pd.concat([pos_samples, neg_sampled]).sample(frac=1, random_state=42)
    y = df_sampled['target'].values
    X = df_sampled.drop('target', axis=1).values
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    ir = n_neg / max(n_pos, 1)
    return X, y, ir

def evaluate_model(X, y, classifier, sampling_method, n_splits=3):
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
                from imblearn.over_sampling import SMOTE
                smote = SMOTE(random_state=42, k_neighbors=2)
                X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
            except:
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'SyMProD':
            try:
                symprod = SyMProD(random_state=42, ct=1.0)
                X_train_res, y_train_res = symprod.fit_resample(X_train_scaled, y_train)
            except:
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'Adaptive-SyMProD':
            try:
                adaptive = AdaptiveSyMProD(random_state=42, search_strategy='hybrid',
                                           ct_range=(0.5, 1.5), max_iter=3, cv_folds=2, verbose=0)
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull):
                        X_train_res, y_train_res = adaptive.fit_resample(X_train_scaled, y_train)
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
    
    return {'auc': np.mean(auc_scores), 'f1': np.mean(f1_scores), 
            'gm': np.mean(gm_scores), 'fm': np.mean(fm_scores)}

def run():
    X, y, ir = load_and_sample_data()
    results = load_results()
    completed = set((r['classifier'], r['sampling']) for r in results)
    
    print(f"已有: {len(results)}条记录，继续测试...")
    
    for clf_name, classifier in CLASSIFIERS.items():
        for sampling in SAMPLING_METHODS:
            if (clf_name, sampling) in completed:
                print(f"✓ {clf_name} | {sampling} [跳过]")
                continue
            
            print(f"→ {clf_name} | {sampling}...", end=' ', flush=True)
            start = time.time()
            scores = evaluate_model(X, y, classifier, sampling)
            elapsed = time.time() - start
            
            result = {
                'dataset': 'heart-statlog', 'data_id': 1567,
                'n_samples_original': 1025009, 'n_samples_used': int(len(y)),
                'n_features': X.shape[1], 'imbalance_ratio': float(ir),
                'sampling_ratio': NEGATIVE_SAMPLING_RATIO,
                'classifier': clf_name, 'sampling': sampling,
                'auc': round(scores['auc'], 4), 'f1': round(scores['f1'], 4),
                'gm': round(scores['gm'], 4), 'fm': round(scores['fm'], 4),
                'time': round(elapsed, 2)
            }
            results.append(result)
            save_results(results)
            print(f"AUC={scores['auc']:.4f}, time={elapsed:.1f}s")
    
    print("\n完成!")
    df = pd.DataFrame(results)
    print("\n按采样方法汇总:")
    print(df.groupby('sampling')[['auc', 'f1', 'gm']].mean().round(4))
    print("\n按分类器汇总:")
    print(df.groupby('classifier')[['auc', 'f1', 'gm']].mean().round(4))

if __name__ == '__main__':
    run()
