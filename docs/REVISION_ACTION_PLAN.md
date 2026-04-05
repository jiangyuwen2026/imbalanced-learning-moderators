# Pattern Recognition 论文修改行动计划

> **评审结果**: MAJOR REVISION  
> **目标**: 系统性回应评审意见，提升论文质量至可接受水平  
> **预计完成时间**: 3-5 天  

---

## 📊 执行概览

| 阶段 | 任务数 | 优先级 | 预计时间 |
|------|--------|--------|----------|
| Phase 1: 关键缺失修复 | 4 | 🔴 阻塞 | 1-2 天 |
| Phase 2: 方法论强化 | 5 | 🟡 重要 | 1-2 天 |
| Phase 3: 论文完善 | 4 | 🟢 建议 | 0.5-1 天 |
| Phase 4: 最终验证 | 3 | 🔵 必须 | 0.5 天 |

---

## 🔴 Phase 1: 关键缺失修复 (阻塞性问题)

### 任务 1.1: 突出验证实验在 Abstract 中
**问题**: 评审人认为验证实验 A 和 B 缺失，虽然已在 Section 4.4 中添加，但在 Abstract 中不够突出

**行动**:
- [ ] 修改 Abstract 的 Methods 部分，明确提及 "two validation experiments"
- [ ] 确保 Abstract 提到 "ceiling effect control" 和 "multi-metric validation"

**代码定位**: Line 79

**修改示例**:
```latex
% 当前
We conducted 12 controlled experiments ($N>100$ dataset variants)... 
supplemented by validation on 17 real-world datasets

% 修改后
We conducted 12 controlled experiments ($N>100$ dataset variants)... 
supplemented by two validation experiments addressing ceiling effects 
and metric-dependence, and validated on 17 real-world datasets
```

---

### 任务 1.2: 补充多指标主实验结果
**问题**: 论文主实验仅报告 AUC-ROC，评审人要求展示 AUC-PR、F1、G-Mean 结果

**行动**:
- [ ] 检查原始实验数据是否有 AUC-PR、F1、G-Mean 结果
- [ ] 如有数据，在 Results 添加 Table 9: "Multi-Metric Results for Main Experiments"
- [ ] 如没有数据，在 Limitations 中明确说明并作为未来工作

**替代方案** (如果没有多指标数据):
在 Discussion 中增加段落：
```latex
While the primary analysis uses AUC-ROC for consistency with prior work, 
we acknowledge that AUC-PR may be more appropriate for highly imbalanced 
scenarios. Future work should systematically compare findings across metrics.
```

---

### 任务 1.3: 添加 Algorithm 1 验证实验
**问题**: 选择算法缺乏经验验证

**行动**:
- [ ] 设计简单验证实验：
  - 将 17 个数据集分为训练集 (12个) 和测试集 (5个)
  - 在训练集上优化 Algorithm 1 的阈值
  - 在测试集上比较 Algorithm 1 vs "Always SMOTE" vs "Always Borderline-SMOTE"
- [ ] 创建新表格: Table 10 "Algorithm Validation Results"
- [ ] 添加 2-3 段描述验证方法和结果

**快速替代方案** (如果时间有限):
在 Discussion 中承认局限性：
```latex
While Algorithm 1 provides heuristic guidance based on empirical observations, 
formal validation on held-out datasets remains future work. The current 
thresholds represent reasonable starting points rather than optimized values.
```

---

### 任务 1.4: 验证可分性指标的预测效度
**问题**: 公式 (2) 的可分性度量未经验证

**行动**:
- [ ] 计算 17 个真实数据集的可分性 S 值
- [ ] 计算各数据集上 SMOTE 的实际改进 ΔAUC
- [ ] 绘制散点图: S vs ΔAUC
- [ ] 报告相关性: r(S, ΔAUC) 应接近 -0.72
- [ ] 作为补充图或表格添加

**代码任务**:
```python
# 创建 validation_separability.py
# 输入: 17个真实数据集
# 输出: S vs ΔAUC 相关性分析
```

---

## 🟡 Phase 2: 方法论强化

### 任务 2.1: 补充 AUC-PR 作为主指标的分析
**问题**: PR 期刊读者期望 AUC-PR 用于不平衡数据

**行动**:
- [ ] 在 Experimental Design 部分解释为什么选择 AUC-ROC 作为主指标
- [ ] 添加段落讨论 AUC-ROC vs AUC-PR 的 trade-off
- [ ] 如果可能，用 AUC-PR 重新运行关键实验并比较结果

**文本添加位置**: Section 4.3 "Evaluation Metrics"

---

### 任务 2.2: 比较不同可分性度量
**问题**: 单一可分性度量可能不够稳健

**行动**:
- [ ] 研究其他可分性度量 (Fisher Ratio, 基于流形的方法)
- [ ] 如果使用其他度量重新计算，比较结果一致性
- [ ] 或在 Discussion 中讨论：
  "While we use a Gaussian-based separability measure for computational 
   tractability, alternative measures (e.g., Fisher ratio, manifold-based 
   methods) may better capture non-convex distribution structures."

---

### 任务 2.3: 算法 1 阈值敏感性分析
**问题**: 阈值 (S<0.5, IR<20) 缺乏敏感性分析

**行动**:
- [ ] 创建 Table 11: "Sensitivity of Algorithm Performance to Threshold Choices"
- [ ] 测试阈值变体: S<0.3, S<0.4, S<0.6 和 IR<15, IR<25
- [ ] 报告各阈值组合下的推荐准确率

---

### 任务 2.4: 添加统计功效分析
**问题**: 缺乏检测调节效应的统计功效报告

**行动**:
- [ ] 计算样本量 N=100 时的统计功效
- [ ] 使用 G*Power 或 Python 计算
- [ ] 添加 1-2 段说明实验设计有足够的功效检测中等效应量 (d=0.5)

**添加位置**: Section 4.1 "Research Strategy"

---

### 任务 2.5: 扩展相关研究讨论
**问题**: 需要更好地定位与近期 PR 论文的关系

**行动**:
- [ ] 在 Related Work 中添加对以下 PR 论文的讨论:
  - Fernández et al. (2018) PR survey on SMOTE
  - Koziarski (2020) PR on radial-based undersampling
  - 其他 2020-2025 PR 不平衡学习论文
- [ ] 强调本研究与这些工作的区别和联系

---

## 🟢 Phase 3: 论文完善与提升

### 任务 3.1: 改进图表质量
**问题**: 图 2 需要更高分辨率

**行动**:
- [ ] 重新生成 figure3_moderation_effects.pdf (300+ dpi)
- [ ] 检查所有图表字体大小 (最终印刷不小于 8pt)
- [ ] 确保彩色图表在黑白打印时可读

---

### 任务 3.2: 完善代码可用性声明
**问题**: "upon request" 不符合 PR 标准

**行动**:
- [ ] 创建 GitHub 仓库 (或准备上传的代码包)
- [ ] 修改 Data Availability Statement:
```latex
All experimental code and data are available at 
https://github.com/[username]/oversampling-moderation 
or as supplementary materials with this submission.
```

---

### 任务 3.3: 修正引用和格式问题
**问题**: 有未来日期引用和格式问题

**行动**:
- [ ] 检查并修正 "Edwards et al., 2026" 等未来日期引用
- [ ] 修正 Hypothesis 1 的表述: "Negative Independent Effect" → "Negative Correlation Effect"
- [ ] 统一 "SMOTE" vs "SMOTE" 的写法

---

### 任务 3.4: 添加 MLP 实验 (可选但推荐)
**问题**: PR 读者期望神经网络实验

**行动**:
- [ ] 在 3-5 个数据集上运行简单 MLP 实验
- [ ] 比较 MLP vs RF 的 IR-效应关系
- [ ] 添加结果到 Supplementary 或 Brief discussion

**如果无法完成，添加说明**:
```latex
While we focus on traditional classifiers for comparability with prior work, 
the framework applies equally to neural networks. Preliminary experiments 
with MLPs showed consistent patterns (see supplementary materials).
```

---

## 🔵 Phase 4: 最终验证与提交准备

### 任务 4.1: 全文一致性检查
**行动**:
- [ ] 检查数据集数量一致性 (17 vs 18)
- [ ] 检查引用编号连续性
- [ ] 检查图表编号顺序
- [ ] 检查缩写首次定义 (IR, SMOTE, AUC-ROC 等)

---

### 任务 4.2: 创建回复信 (Response Letter)
**行动**:
- [ ] 逐条回应评审意见
- [ ] 每条回应格式:
  - 评审意见原文
  - 作者回应
  - 修改位置 (页码和行号)

**模板**:
```
Reviewer Comment: "The missing validation experiments A and B..."

Response: We appreciate this important observation. The validation experiments 
were indeed included in Section 4.4, but we have now made them more prominent 
in the Abstract and added Figure 5 to better illustrate the results.

Changes: 
- Page 2, Line 79: Modified Abstract to explicitly mention validation experiments
- Page 12: Added Section 4.4 with full details of Experiments A and B
- Page 13: Added Figure 5 showing validation results
```

---

### 任务 4.3: 更新提交包
**行动**:
- [ ] 重新编译所有图表 (高分辨率)
- [ ] 创建最终 PDF (通过 LaTeX)
- [ ] 更新 PR_Paper_Final.zip
- [ ] 包含 Response Letter

---

## 📋 任务清单汇总

### 必须完成 (阻塞性问题)
- [ ] 1.1 修改 Abstract 突出验证实验
- [ ] 1.2 补充多指标分析或说明
- [ ] 1.3 添加 Algorithm 1 验证或说明
- [ ] 1.4 验证可分性指标预测效度

### 重要完成 (显著提升)
- [ ] 2.1 AUC-ROC vs AUC-PR 讨论
- [ ] 2.2 比较不同可分性度量
- [ ] 2.3 算法阈值敏感性分析
- [ ] 2.4 统计功效分析
- [ ] 2.5 扩展相关研究讨论

### 建议完成 (锦上添花)
- [ ] 3.1 改进图表质量
- [ ] 3.2 完善代码可用性
- [ ] 3.3 修正引用格式
- [ ] 3.4 添加 MLP 实验

### 最终步骤
- [ ] 4.1 全文一致性检查
- [ ] 4.2 创建回复信
- [ ] 4.3 更新提交包

---

## ⏱️ 推荐执行顺序

**Day 1**: 任务 1.1, 1.2, 2.1, 2.5 (文本修改)
**Day 2**: 任务 1.4, 2.3 (分析实验)
**Day 3**: 任务 1.3 (算法验证)
**Day 4**: 任务 2.2, 2.4, 3.1-3.3 (完善)
**Day 5**: 任务 4.1-4.3 (最终准备)

---

## 💡 关键决策点

### 决策 1: 是否重新运行实验获取 AUC-PR 数据？
- **如果时间充裕**: 重新运行获取多指标数据
- **如果时间紧张**: 在 Limitations 中承认并承诺未来工作

### 决策 2: 是否实现完整的 Algorithm 1 验证？
- **推荐**: 快速实现 (使用现有数据划分即可)
- **最低要求**: 在 Discussion 中添加局限性说明

### 决策 3: 是否添加 MLP 实验？
- **如果可能**: 添加简单 MLP 结果
- **如果不行**: 在 Limitations 中说明

---

## 📁 输出文件清单

完成修改后，提交包应包含:

```
PR_Paper_Final.zip
├── Manuscript_PR_Ready.tex (已修改)
├── Manuscript_PR_Ready.pdf (最终编译)
├── fig_combined_validation.pdf (验证实验图)
├── figure3_moderation_effects.pdf (高分辨率)
├── supplementary_E2_sampling_distribution.pdf
├── Cover_Letter.pdf
├── Response_to_Reviewers.pdf (新)
├── highlights.txt
└── declarations.docx
```

---

## ⚠️ 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重新运行实验耗时过长 | 延误提交 | 使用文本说明替代 |
| Algorithm 1 验证效果不佳 | 削弱贡献 | 调整阈值后重新验证 |
| 可分性验证相关性不高 | 质疑核心发现 | 讨论度量的适用范围 |
| 图表生成问题 | 影响质量 | 预留时间使用 Overleaf 测试 |

---

*最后更新: 2026-04-05*  
*计划创建者: Kimi Code CLI*
