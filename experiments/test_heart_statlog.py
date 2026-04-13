#!/usr/bin/env python3
"""
Heart-statlog数据集测试
=======================
IR: 128,125 (极度不平衡)
样本数: 1,025,009 (超大规模)
策略: 对负类进行随机下采样以加速测试，保留所有正样本
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
os.makedirs('Results/ExtremeImbalance', exist_ok=True)
RESULTS_FILE = 'Results/ExtremeImbalance/heart_statlog_results.json'

# 分类器配置
CLASSIFIERS = {
    'LR': LogisticRegression(max_iter=1000, random_state=42),
    'GBDT': GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42),
    'DT': DecisionTreeClassifier(random_state=42, max_depth=10)
}

SAMPLING_METHODS = ['None', 'SMOTE', 'SyMProD', 'Adaptive-SyMProD']

# 子采样比例 - 保留所有正样本，负类采样比例
NEGATIVE_SAMPLING_RATIO = 0.1  # 只保留10%的负类样本


def load_and_sample_data():
    """加载数据并对负类进行下采样"""
    csv_path = 'Data/OpenML_27/heart-statlog.csv'
    print(f"📊 加载数据集: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"   原始样本数: {len(df):,}")
    
    # 分离正负类
    pos_samples = df[df['target'] == 1]
    neg_samples = df[df['target'] == 0]
    
    print(f"   正类样本: {len(pos_samples)}")
    print(f"   负类样本: {len(neg_samples):,}")
    
    # 对负类进行随机下采样
    neg_sampled = neg_samples.sample(n=int(len(neg_samples) * NEGATIVE_SAMPLING_RATIO), 
                                      random_state=42)
    
    # 合并
    df_sampled = pd.concat([pos_samples, neg_sampled]).sample(frac=1, random_state=42)
    
    y = df_sampled['target'].values
    X = df_sampled.drop('target', axis=1).values
    
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    ir = n_neg / max(n_pos, 1)
    
    print(f"\n📊 子采样后:")
    print(f"   样本数: {len(y):,} (原始 {len(df):,} 的 {len(y)/len(df)*100:.1f}%)")
    print(f"   正类: {n_pos}, 负类: {n_neg:,}")
    print(f"   IR: {ir:.2f}")
    
    return X, y, ir


def evaluate_model(X, y, classifier, sampling_method, n_splits=3):
    """评估模型"""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    auc_scores, f1_scores, gm_scores, fm_scores = [], [], [], []
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
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
            except Exception as e:
                print(f"      [SMOTE失败: {e}]", end='')
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'SyMProD':
            try:
                symprod = SyMProD(random_state=42, ct=1.0)
                X_train_res, y_train_res = symprod.fit_resample(X_train_scaled, y_train)
            except Exception as e:
                print(f"      [SyMProD失败: {e}]", end='')
                X_train_res, y_train_res = X_train_scaled, y_train
        elif sampling_method == 'Adaptive-SyMProD':
            try:
                adaptive = AdaptiveSyMProD(random_state=42, search_strategy='hybrid',
                                           ct_range=(0.5, 1.5), max_iter=3, cv_folds=2, verbose=0)
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull):
                        X_train_res, y_train_res = adaptive.fit_resample(X_train_scaled, y_train)
            except Exception as e:
                print(f"      [Adaptive失败: {str(e)[:30]}]", end='')
                X_train_res, y_train_res = X_train_scaled, y_train
        else:
            X_train_res, y_train_res = X_train_scaled, y_train
        
        # 训练
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
    print("Heart-statlog数据集测试")
    print("=" * 70)
    print(f"负类采样比例: {NEGATIVE_SAMPLING_RATIO*100:.0f}%")
    print("=" * 70)
    
    # 加载数据
    X, y, ir = load_and_sample_data()
    
    all_results = []
    total_tasks = len(CLASSIFIERS) * len(SAMPLING_METHODS)
    completed = 0
    
    print("\n" + "=" * 70)
    print("开始测试...")
    print("=" * 70)
    
    for clf_name, classifier in CLASSIFIERS.items():
        print(f"\n分类器: {clf_name}")
        
        for sampling in SAMPLING_METHODS:
            completed += 1
            print(f"  [{completed}/{total_tasks}] 采样: {sampling}...", end=' ', flush=True)
            start_time = time.time()
            
            scores = evaluate_model(X, y, classifier, sampling)
            elapsed = time.time() - start_time
            
            result = {
                'dataset': 'heart-statlog',
                'data_id': 1567,
                'n_samples_original': 1025009,
                'n_samples_used': int(len(y)),
                'n_features': X.shape[1],
                'imbalance_ratio': float(ir),
                'sampling_ratio': NEGATIVE_SAMPLING_RATIO,
                'classifier': clf_name,
                'sampling': sampling,
                'auc': round(scores['auc'], 4),
                'f1': round(scores['f1'], 4),
                'gm': round(scores['gm'], 4),
                'fm': round(scores['fm'], 4),
                'time': round(elapsed, 2)
            }
            
            all_results.append(result)
            
            # 保存结果
            with open(RESULTS_FILE, 'w') as f:
                json.dump(all_results, f, indent=2)
            
            print(f"AUC={scores['auc']:.4f}, F1={scores['f1']:.4f}, GM={scores['gm']:.4f}, time={elapsed:.1f}s")
    
    print("\n" + "=" * 70)
    print("实验完成!")
    print("=" * 70)
    
    # 打印汇总
    df = pd.DataFrame(all_results)
    print("\n汇总统计:")
    print("-" * 70)
    summary = df.groupby('sampling')[['auc', 'f1', 'gm', 'fm']].mean()
    print(summary.round(4))
    
    print("\n各分类器表现:")
    print("-" * 70)
    clf_summary = df.groupby('classifier')[['auc', 'f1', 'gm', 'fm']].mean()
    print(clf_summary.round(4))
    
    # 保存CSV
    df.to_csv('Results/ExtremeImbalance/heart_statlog_results.csv', index=False)
    print(f"\n结果已保存:")
    print(f"  - {RESULTS_FILE}")
    print(f"  - Results/ExtremeImbalance/heart_statlog_results.csv")
    
    return all_results


if __name__ == '__main__':
    run_experiment()
