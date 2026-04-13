#!/usr/bin/env python3
"""
轻度不平衡数据集测试 - 快速版本
================================
特点：
1. 实时保存结果（断点续传）
2. 减少交叉验证折数（3折）
3. 减少CT搜索范围
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
from imblearn.over_sampling import SMOTE

sys.path.insert(0, 'Code/adaptive-symprod/src')
from symprod import SyMProD
from adaptive_symprod_v4 import AdaptiveSyMProD

# 创建结果目录
os.makedirs('Results/MildImbalance', exist_ok=True)
RESULTS_FILE = 'Results/MildImbalance/mild_results.json'

# 轻度不平衡数据集 (IR < 4) - 选择代表性的8个
MILD_DATASETS = [
    ('iris', 61, 2.00),
    ('wine', 187, 2.71),
    ('vehicle', 54, 3.25),
    ('pima', 37, 1.87),
    ('haberman', 43, 2.78),
    ('breast-wisc', 15, 1.90),
    ('credit-g', 31, 2.33),
    ('wdbc', 1510, 1.68),
]

# 分类器配置
CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}

SAMPLING_METHODS = ['None', 'SMOTE', 'SyMProD', 'Adaptive-SyMProD']


def load_results():
    """加载已有结果"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_results(results):
    """保存结果"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    # 同时保存CSV
    df = pd.DataFrame(results)
    df.to_csv('Results/MildImbalance/mild_results.csv', index=False)


def load_dataset(name, data_id):
    """从本地CSV加载数据集"""
    csv_path = f'Data/OpenML_27/{name}.csv'
    
    if not os.path.exists(csv_path):
        return None, None, None
    
    df = pd.read_csv(csv_path)
    y = df['target'].values
    X = df.drop('target', axis=1)
    
    # 处理缺失值
    if X.isnull().any().any():
        X = X.fillna(X.median())
    
    X = X.values
    
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    ir = n_neg / max(n_pos, 1)
    
    return X, y, ir


def evaluate_model(X, y, classifier, sampling_method, n_splits=3):
    """使用交叉验证评估模型"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    auc_scores, f1_scores, gm_scores, fm_scores = [], [], [], []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 采样
        if sampling_method == 'SMOTE':
            try:
                smote = SMOTE(random_state=42)
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
                                           ct_range=(0.5, 1.5), max_iter=5)
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull):
                        X_train_res, y_train_res = adaptive.fit_resample(X_train_scaled, y_train)
            except:
                X_train_res, y_train_res = X_train_scaled, y_train
        else:
            X_train_res, y_train_res = X_train_scaled, y_train
        
        # 训练
        clf = classifier.__class__(**classifier.get_params())
        clf.fit(X_train_res, y_train_res)
        
        y_pred = clf.predict(X_test_scaled)
        y_prob = clf.predict_proba(X_test_scaled)[:, 1] if hasattr(clf, 'predict_proba') else y_pred
        
        # 计算指标
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
    
    return {
        'auc': np.mean(auc_scores),
        'f1': np.mean(f1_scores),
        'gm': np.mean(gm_scores),
        'fm': np.mean(fm_scores)
    }


def run_experiment():
    """运行实验"""
    print("=" * 70)
    print("轻度不平衡数据集测试 - 快速版本")
    print("=" * 70)
    
    # 加载已有结果
    all_results = load_results()
    completed = set((r['dataset'], r['classifier'], r['sampling']) for r in all_results)
    
    print(f"已有结果: {len(all_results)}条记录")
    print(f"数据集: {[d[0] for d in MILD_DATASETS]}")
    print(f"分类器: {list(CLASSIFIERS.keys())}")
    print("=" * 70)
    
    total_tasks = len(MILD_DATASETS) * len(CLASSIFIERS) * len(SAMPLING_METHODS)
    completed_count = len(completed)
    
    for ds_idx, (name, data_id, expected_ir) in enumerate(MILD_DATASETS, 1):
        print(f"\n[{ds_idx}/{len(MILD_DATASETS)}] 数据集: {name}")
        
        X, y, actual_ir = load_dataset(name, data_id)
        if X is None:
            continue
        
        print(f"  样本数: {len(y)}, 特征数: {X.shape[1]}, IR: {actual_ir:.2f}")
        
        for clf_name, classifier in CLASSIFIERS.items():
            print(f"\n  分类器: {clf_name}")
            
            for sampling in SAMPLING_METHODS:
                task_key = (name, clf_name, sampling)
                if task_key in completed:
                    print(f"    采样: {sampling}... [跳过 - 已完成]")
                    continue
                
                print(f"    采样: {sampling}...", end=' ', flush=True)
                start_time = time.time()
                
                scores = evaluate_model(X, y, classifier, sampling)
                elapsed = time.time() - start_time
                
                result = {
                    'dataset': name,
                    'data_id': data_id,
                    'n_samples': int(len(y)),
                    'n_features': int(X.shape[1]),
                    'imbalance_ratio': float(actual_ir),
                    'classifier': clf_name,
                    'sampling': sampling,
                    'auc': round(scores['auc'], 4),
                    'f1': round(scores['f1'], 4),
                    'gm': round(scores['gm'], 4),
                    'fm': round(scores['fm'], 4),
                    'time': round(elapsed, 2)
                }
                
                all_results.append(result)
                save_results(all_results)
                completed_count += 1
                
                print(f"AUC={scores['auc']:.4f}, F1={scores['f1']:.4f}, time={elapsed:.2f}s "
                      f"[{completed_count}/{total_tasks}]")
    
    print("\n" + "=" * 70)
    print("实验完成!")
    print(f"结果保存: Results/MildImbalance/mild_results.csv")
    print_summary(all_results)
    
    return all_results


def print_summary(results):
    """打印汇总统计"""
    df = pd.DataFrame(results)
    
    print("\n" + "=" * 70)
    print("汇总统计 - 按采样方法")
    print("=" * 70)
    summary = df.groupby('sampling')[['auc', 'f1', 'gm', 'fm']].mean()
    print(summary.round(4))
    
    print("\n" + "=" * 70)
    print("汇总统计 - 按分类器")
    print("=" * 70)
    clf_summary = df.groupby('classifier')[['auc', 'f1', 'gm', 'fm']].mean()
    print(clf_summary.round(4))
    
    print("\n" + "=" * 70)
    print("各分类器在不同采样方法下的AUC表现")
    print("=" * 70)
    pivot = df.pivot_table(values='auc', index=['dataset', 'classifier'], 
                           columns='sampling', aggfunc='mean')
    print(pivot.round(4))


if __name__ == '__main__':
    run_experiment()
