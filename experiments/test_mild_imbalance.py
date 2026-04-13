#!/usr/bin/env python3
"""
轻度不平衡数据集测试
=====================
针对IR < 4的数据集，使用3种分类器进行对比测试

分类器:
1. Logistic Regression (LR)
2. Gradient Boosting Decision Tree (GBDT)
3. Decision Tree (DT)

采样方法:
- None (基准)
- SMOTE
- SyMProD
- Adaptive-SyMProD
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

# 轻度不平衡数据集 (IR < 4)
MILD_DATASETS = [
    ('iris', 61, 2.00),
    ('wine', 187, 2.71),
    ('vehicle', 54, 3.25),
    ('pima', 37, 1.87),
    ('haberman', 43, 2.78),
    ('breast-wisc', 15, 1.90),
    ('credit-a', 29, 1.25),
    ('credit-g', 31, 2.33),
    ('ionosphere', 59, 1.79),
    ('sonar', 40, 1.14),
    ('wdbc', 1510, 1.68),
]

# 分类器配置
CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}

# 采样方法
SAMPLING_METHODS = ['None', 'SMOTE', 'SyMProD', 'Adaptive-SyMProD']


def load_dataset(name, data_id):
    """从本地CSV加载数据集"""
    csv_path = f'Data/OpenML_27/{name}.csv'
    
    if not os.path.exists(csv_path):
        print(f"  ❌ 文件不存在: {csv_path}")
        return None, None, None
    
    df = pd.read_csv(csv_path)
    y = df['target'].values
    X = df.drop('target', axis=1)
    
    # 处理缺失值 - 用中位数填充
    if X.isnull().any().any():
        X = X.fillna(X.median())
    
    X = X.values
    
    # 计算实际IR
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    ir = n_neg / max(n_pos, 1)
    
    return X, y, ir


def evaluate_model(X, y, classifier, clf_name, sampling_method, n_splits=5):
    """
    使用交叉验证评估模型
    
    Returns:
        dict: 包含AUC, F1, GM, FM的结果
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    auc_scores = []
    f1_scores = []
    gm_scores = []
    fm_scores = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # 标准化
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 应用采样方法
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
            except Exception as e:
                print(f"    SyMProD失败: {e}")
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'Adaptive-SyMProD':
            try:
                adaptive = AdaptiveSyMProD(random_state=42, search_strategy='hybrid')
                # 抑制冗长输出
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull):
                        X_train_res, y_train_res = adaptive.fit_resample(X_train_scaled, y_train)
            except Exception as e:
                print(f"    Adaptive-SyMProD失败: {e}")
                X_train_res, y_train_res = X_train_scaled, y_train
        else:
            X_train_res, y_train_res = X_train_scaled, y_train
        
        # 训练模型
        clf = classifier.__class__(**classifier.get_params())
        clf.fit(X_train_res, y_train_res)
        
        # 预测
        y_pred = clf.predict(X_test_scaled)
        y_prob = clf.predict_proba(X_test_scaled)[:, 1] if hasattr(clf, 'predict_proba') else y_pred
        
        # 计算指标
        try:
            auc = roc_auc_score(y_test, y_prob)
        except:
            auc = 0.5
        
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # G-Mean
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            sensitivity = tp / max(tp + fn, 1)
            specificity = tn / max(tn + fp, 1)
            gm = np.sqrt(sensitivity * specificity)
        else:
            gm = 0
        
        # F-Measure (F0.5, F2的平均)
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
    """运行完整实验"""
    print("=" * 70)
    print("轻度不平衡数据集测试 (IR < 4)")
    print("=" * 70)
    print(f"分类器: {list(CLASSIFIERS.keys())}")
    print(f"采样方法: {SAMPLING_METHODS}")
    print(f"数据集: {len(MILD_DATASETS)}个")
    print("=" * 70)
    
    all_results = []
    
    for ds_idx, (name, data_id, expected_ir) in enumerate(MILD_DATASETS, 1):
        print(f"\n[{ds_idx}/{len(MILD_DATASETS)}] 数据集: {name}")
        
        # 加载数据
        X, y, actual_ir = load_dataset(name, data_id)
        if X is None:
            continue
        
        print(f"  样本数: {len(y)}, 特征数: {X.shape[1]}, IR: {actual_ir:.2f}")
        
        # 对每个分类器进行测试
        for clf_name, classifier in CLASSIFIERS.items():
            print(f"\n  分类器: {clf_name}")
            
            for sampling in SAMPLING_METHODS:
                print(f"    采样: {sampling}...", end=' ')
                start_time = time.time()
                
                scores = evaluate_model(X, y, classifier, clf_name, sampling)
                elapsed = time.time() - start_time
                
                result = {
                    'dataset': name,
                    'data_id': data_id,
                    'n_samples': len(y),
                    'n_features': X.shape[1],
                    'imbalance_ratio': actual_ir,
                    'classifier': clf_name,
                    'sampling': sampling,
                    'auc': round(scores['auc'], 4),
                    'f1': round(scores['f1'], 4),
                    'gm': round(scores['gm'], 4),
                    'fm': round(scores['fm'], 4),
                    'time': round(elapsed, 2)
                }
                
                all_results.append(result)
                print(f"AUC={scores['auc']:.4f}, F1={scores['f1']:.4f}, time={elapsed:.2f}s")
    
    # 保存结果
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('Results/MildImbalance/mild_imbalance_results.csv', index=False)
    
    with open('Results/MildImbalance/mild_imbalance_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("实验完成!")
    print(f"结果保存: Results/MildImbalance/mild_imbalance_results.csv")
    
    # 打印汇总统计
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
    print("详细结果 - 按数据集和分类器")
    print("=" * 70)
    
    pivot = df.pivot_table(
        values='auc',
        index=['dataset', 'classifier'],
        columns='sampling',
        aggfunc='mean'
    )
    print(pivot.round(4))


if __name__ == '__main__':
    run_experiment()
