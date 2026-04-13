#!/usr/bin/env python3
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE

import sys
sys.path.insert(0, 'Code/adaptive-symprod/src')
from symprod import SyMProD

def make_ds(n, d, ir, seed):
    w = [ir/(1+ir), 1/(1+ir)]
    X, y = make_classification(n_samples=n, n_features=d, n_informative=d//2,
                               n_redundant=d//4, weights=w, flip_y=0.05, random_state=seed)
    return X, y

def calc_metrics(y_true, y_pred, y_proba):
    auc = roc_auc_score(y_true, y_proba)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    sen, spe = tp/(tp+fn), tn/(tn+fp)
    gm = np.sqrt(sen*spe)
    prc = tp/(tp+fp) if (tp+fp)>0 else 0
    fm = np.sqrt(prc*sen)
    return {'AUC':auc, 'F1':f1, 'GM':gm, 'FM':fm}

def evaluate(X, y, sn):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = {'AUC':[], 'F1':[], 'GM':[], 'FM':[]}
    
    for tr, te in skf.split(X, y):
        X_train, X_test = X[tr], X[te]
        y_train, y_test = y[tr], y[te]
        
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        if sn == 'None':
            Xr, yr = X_train, y_train
        elif sn == 'SMOTE':
            k = min(5, (y_train==1).sum()-1)
            s = SMOTE(random_state=42, k_neighbors=max(1,k))
            Xr, yr = s.fit_resample(X_train, y_train)
        else:
            s = SyMProD(ct=1.0, random_state=42)
            Xr, yr = s.fit_resample(X_train, y_train)
        
        clf = LogisticRegression(max_iter=1000, random_state=42)
        clf.fit(Xr, yr)
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]
        
        m = calc_metrics(y_test, y_pred, y_proba)
        for k in scores:
            scores[k].append(m[k])
    
    return {k: np.mean(v) for k, v in scores.items()}

DATASETS = [
    ('mild-01', 500, 10, 1.5, 1), ('mild-02', 600, 12, 2.0, 2), ('mild-03', 700, 15, 2.5, 3),
    ('mild-04', 800, 18, 3.0, 4), ('mild-05', 900, 20, 3.5, 5), ('mild-06', 550, 10, 1.8, 6),
    ('mild-07', 650, 14, 2.2, 7), ('mild-08', 750, 16, 2.8, 8), ('mild-09', 850, 18, 3.2, 9),
    ('mod-01', 800, 15, 4.0, 10), ('mod-02', 1000, 20, 5.0, 11), ('mod-03', 1200, 25, 6.0, 12),
    ('mod-04', 1400, 30, 7.0, 13), ('mod-05', 1000, 18, 8.0, 14), ('mod-06', 1500, 35, 9.0, 15),
    ('mod-07', 2000, 40, 10.0, 16), ('mod-08', 1800, 28, 12.0, 17), ('mod-09', 2200, 32, 15.0, 18),
    ('mod-10', 2500, 45, 8.5, 19), ('mod-11', 1200, 22, 6.5, 20), ('mod-12', 1600, 28, 11.0, 21),
    ('ext-01', 2000, 20, 20.0, 22), ('ext-02', 2500, 25, 25.0, 23), ('ext-03', 3000, 30, 30.0, 24),
    ('ext-04', 2200, 22, 22.0, 25), ('ext-05', 2800, 28, 28.0, 26), ('ext-06', 3500, 35, 35.0, 27),
]

print("运行27数据集实验...")
samplers = ['None', 'SMOTE', 'SyMProD']
results = []

for name, n, d, ir, seed in DATASETS:
    g = '轻度不平衡' if ir < 4 else ('中度不平衡' if ir < 20 else '极度不平衡')
    X, y = make_ds(n, d, ir, seed)
    
    for sn in samplers:
        m = evaluate(X, y, sn)
        results.append({'dataset':name, 'group':g, 'IR':ir, 'sampler':sn, **m})

with open('Results/experiment_27_3methods.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"✅ 完成！保存了 {len(results)} 条结果")
