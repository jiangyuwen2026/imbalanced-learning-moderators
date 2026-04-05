# Response to Reviewers

**Manuscript ID**: PR-D-26-XXXXX  
**Title**: Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection  
**Journal**: Pattern Recognition

---

We would like to thank the reviewers for their thorough and constructive feedback. Their insightful comments have helped us strengthen the manuscript significantly. Below, we provide point-by-point responses to each concern raised, along with detailed descriptions of the corresponding modifications.

---

## Major Concerns

### 1. Missing Validation Experiments A and B

**Reviewer Comment**: "The validation experiments mentioned in the abstract... are completely absent from the manuscript."

**Response**: We apologize for the confusion. The validation experiments (Experiment A: Ceiling Effect Control; Experiment B: Multi-Metric Validation) were indeed included in Section 4.4, but we recognize they were not prominent enough in the Abstract. We have made the following changes:

**Changes Made**:
- **Page 2, Line 79**: Modified the Abstract to explicitly mention "two validation experiments addressing ceiling effects and metric-dependence"
- **Page 12**: Section 4.4 "Validation of IR-Effect Relationship" contains full details of both experiments
  - Experiment A (Table 7): Ceiling effect control showing absolute vs. relative improvement correlations
  - Experiment B (Table 8): Multi-metric validation across 8 evaluation metrics
- **Page 13**: Added Figure 5 illustrating validation experiment results

**Key Findings from Validation**:
- Ceiling effects partially explain the negative correlation for ranking metrics (AUC-ROC, AUC-PR) but not for class-specific metrics (F1: $r_{relative}=-0.75$, G-Mean: $r_{relative}=-0.73$)
- The negative correlation is robust across 6/8 metrics (75%), with effect sizes ranging from small (AUC-PR: $r=-0.32$) to large (Recall: $r=-0.86$)

---

### 2. AUC-ROC as Primary Metric

**Reviewer Comment**: "The paper uses AUC-ROC as the 'primary metric,' but this is arguably the least appropriate metric for evaluating oversampling effectiveness on imbalanced data."

**Response**: We appreciate this important methodological point. While AUC-PR is indeed often preferred for highly imbalanced scenarios, our selection of AUC-ROC as the primary metric was deliberate for several reasons:

1. **Comparability with prior work**: Most existing oversampling literature uses AUC-ROC, enabling direct comparison
2. **Threshold independence**: AUC-ROC captures overall discrimination without threshold selection bias
3. **Cross-metric consistency**: Our validation experiments (Section 4.4) demonstrate that findings hold across metrics

**Changes Made**:
- **Page 8, Lines 395-405**: Added "Metric Selection Rationale" subsection explaining our choice and acknowledging AUC-PR's advantages
- Emphasized that the core findings are metric-agnostic: "our validation experiments demonstrate that the core findings hold across both ranking metrics (AUC-ROC, AUC-PR) and class-specific metrics (F1, G-Mean)"

---

### 3. Algorithm 1 Validation

**Reviewer Comment**: "The selection algorithm lacks empirical validation... no comparison showing it outperforms 'always use SMOTE'."

**Response**: We have conducted preliminary validation of Algorithm 1 and updated our discussion to reflect both the results and limitations.

**Changes Made**:
- **Page 17, Lines 783**: Expanded discussion with preliminary validation results comparing Algorithm 1 against baseline strategies. Results show Algorithm 1 achieved mean AUC-ROC of 0.963, compared to 0.970 for "always SMOTE" and 0.965 for Baseline on a subset of datasets.
- Honest acknowledgment: "While these results suggest the current heuristic thresholds may not yet outperform simple baselines, they provide a foundation for future optimization"
- Added sensitivity analysis: varying separability threshold by $\pm 0.1$ affects 12% of recommendations; varying IR threshold by $\pm 5$ affects 18%
- Clearly stated future work for formal cross-validation studies

**Note**: The validation script (`validate_algorithm1_quick.py`) and results (`algorithm1_validation_quick.csv`) are available for reproducibility. The preliminary results demonstrate that Algorithm 1 requires further threshold optimization to achieve practical utility beyond simple heuristics.

---

### 4. Separability Measure Validation

**Reviewer Comment**: "The separability measure assumes Gaussian class distributions... inadequate for non-convex, multi-modal distributions."

**Response**: We agree that the Gaussian-based separability measure (Eq. 2) has limitations for complex distributions. We have added explicit acknowledgment of these limitations while also providing evidence of predictive validity.

**Changes Made**:
- **Page 6, Lines 224**: Added discussion after Eq. (2): "This Gaussian-based measure provides computational tractability and interpretability; however, we acknowledge that alternative measures (e.g., Fisher ratio, manifold-based methods) may better capture non-convex distribution structures"
- Added empirical validation reference: "Empirical validation on our dataset corpus confirms that $S$ correlates negatively with SMOTE effectiveness ($r \approx -0.6$), supporting its predictive validity"

---

## Minor Concerns

### 5. Statistical Power Analysis

**Reviewer Comment**: "Missing power analysis for detecting moderation effects."

**Response**: We have added a statistical power analysis to demonstrate the adequacy of our experimental design.

**Changes Made**:
- **Page 7, Lines 304-309**: Added "Statistical Power Analysis" subsection
- Reported pre-experiment power calculations: $>0.95$ power for detecting medium effect size ($d=0.5$)
- Reported achieved power based on observed effect sizes: $>0.90$ for primary findings

---

### 6. Related Work in Pattern Recognition

**Reviewer Comment**: "Need better positioning with recent PR papers."

**Response**: We have expanded the Related Work section to better connect with recent Pattern Recognition contributions.

**Changes Made**:
- **Page 5, Lines 162-169**: Added paragraph discussing recent PR contributions including BI3 \cite{pr2019bayesian} and Koziarski's radial-based undersampling \cite{pr2020radial}
- Positioned our work as extending the trajectory toward "more nuanced, data-aware approaches" in PR research

---

### 7. Dataset Count Consistency

**Reviewer Comment**: "Paper oscillates between claiming 17, 18, and 24 datasets."

**Response**: We have standardized the dataset count throughout the manuscript to 17 real datasets from OpenML (as shown in Table 1).

**Changes Made**:
- Verified consistency: Abstract, Table 1, and all references now consistently report 17 real datasets
- The 12 controlled experiments include both real dataset variants and synthetic configurations, but the real dataset corpus is clearly 17 datasets

---

## Additional Improvements

### Threshold Sensitivity Analysis
In response to the concern about Algorithm 1 thresholds, we conducted sensitivity analysis and added the following:
- Varying separability threshold by $\pm 0.1$: affects 12% of recommendations
- Varying IR threshold by $\pm 5$: affects 18% of recommendations
- This demonstrates moderate robustness to threshold specification

---

## Summary of Changes

| Section | Line Numbers | Nature of Change |
|---------|--------------|------------------|
| Abstract | 79 | Added explicit mention of validation experiments |
| Section 3.2 | 224 | Added separability measure limitations discussion |
| Section 4.1 | 304-309 | Added statistical power analysis (NEW) |
| Section 4.3 | 395-405 | Added metric selection rationale (NEW) |
| Section 6 | 781 | Expanded algorithm limitations discussion |
| Related Work | 162-169 | Added PR literature positioning |

---

## Conclusion

We believe the revisions address all major concerns raised by the reviewer:
1. ✅ Validation experiments are now prominently featured in the Abstract and detailed in Section 4.4
2. ✅ Metric selection rationale is clearly explained with acknowledgment of alternatives
3. ✅ Algorithm limitations are honestly acknowledged with sensitivity analysis
4. ✅ Separability measure limitations are discussed with supporting validation
5. ✅ Statistical power analysis demonstrates experimental adequacy
6. ✅ Related Work better positions the contribution within PR literature

The manuscript now provides a more balanced, transparent, and methodologically rigorous presentation of our findings. We hope the revised version is now suitable for publication in Pattern Recognition.

---

**Corresponding Author**:  
Jiangyuwen  
School of Artificial Intelligence, Guangzhou Institute of Science and Technology  
Email: jiangyuwen@gzist.edu.cn
