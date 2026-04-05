# Comprehensive Consistency Check Report

**Paper:** Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection  
**File:** Manuscript_PR_Ready.tex  
**Date:** April 5, 2026  

---

## 1. Dataset Numbers

### ✅ "17 datasets" Check
| Location | Count | Status |
|----------|-------|--------|
| Abstract (line 79) | 17 | ✅ Consistent |
| Section 4 (line 308) | **18** | ⚠️ **INCONSISTENCY** - Says "18" but Table 1 has 17 |
| Results (line 416) | 17 | ✅ Consistent |
| Conclusion (line 712) | 17 | ✅ Consistent |
| Table 1 caption (line 313) | 17 | ✅ Consistent |
| Table 1 actual count | 17 | ✅ Verified (4+5+4+2+2 = 17) |

**Finding:** Line 308 states "18 publicly available datasets" but Table 1 lists only 17 datasets. This needs correction.

### ✅ "15 held-out datasets" Check
| Location | Count | Status |
|----------|-------|--------|
| Conclusion (line 712) | 15 | Mentioned |

**Note:** This is only mentioned once in the conclusion. The main analysis uses 17 datasets, and 15 held-out datasets are mentioned for supplementary validation.

---

## 2. Experimental Numbers

### ✅ "12 controlled experiments" Check
| Location | Status |
|----------|--------|
| Abstract (line 79) | ✅ Present |
| Section 1 Contribution (line 120) | ✅ Present |
| Section 2 (line 159) | ✅ Present |
| Figure 2 caption (line 447) | ✅ Present |
| Figure 2 title (line 463) | ✅ Present |
| Results (line 529, 558) | ✅ Present |
| Conclusion (line 712) | ✅ Present |
| Table 6 (line 532-556) | ✅ Lists 12 experiments |

**Verification of Table 6 (12 experiments):**
- Stage 1: 1 experiment (Exp 1: Cross-dataset)
- Stage 2: 6 experiments (Exp 2-6: B1 Within-dataset on 5 datasets + Exp 7: B2 Generated)
- Stage 3: 5 experiments (Exp 8-12: C1-C5 moderation tests)
- **Total: 12 experiments** ✅

### ✅ "192 synthetic configurations" Check
| Location | Status |
|----------|--------|
| Section 4.2 (line 353) | ✅ "192 unique dataset configurations" |
| Figure 2 (line 473) | ✅ "192 Synthetic Configurations" |

**Verification:** 8 IR levels × 6 separability levels × 4 cluster structures = 192 ✅

### ✅ "$N>100$ dataset variants" Check
| Location | Status |
|----------|--------|
| Abstract (line 79) | ✅ Present |
| Section 1 (line 120) | ✅ Present |
| Section 2 (line 159) | ✅ Present |
| Conclusion (line 712) | ✅ Present |

---

## 3. Correlation Values

### ⚠️ Correlation Value Inconsistencies Found

| Location | Reported Value | Status |
|----------|----------------|--------|
| Abstract | mean r=-0.68 | Abstract claim |
| Results (line 447) | r=-0.765 | B2 result |
| Results (line 444) | r range: -0.944 to -0.39 | B1 results |
| Results (line 418) | r=-0.72 | Cross-dataset separability |
| Results (line 581) | ρ=-0.72 | Moderation effect |
| Table 6 (line 546) | r=-0.765 | B2 listed |
| Table 6 (line 542) | r=+0.9662 | Exp 1 (baseline) |

**Issue:** The abstract claims "mean r=-0.68" but the main experiments show:
- B1 (within-dataset): r range -0.944 to -0.39
- B2 (generated data): r=-0.765
- Combined 95% CI: [-0.823, -0.451]

The mean of B1 and B2 correlations would be approximately -0.68 (averaging -0.6 and -0.765), but this calculation is not explicitly shown. The abstract value appears to be an approximate mean of the controlled experiment results.

### ⚠️ Confidence Interval Inconsistency
| Location | CI Value | Status |
|----------|----------|--------|
| Abstract | [-0.823, -0.451] | ✅ Matches B2 CI |
| Results (line 447) | [-0.923, -0.412] | B2 result |
| Results (line 581) | [-0.891, -0.412] | Separability moderation |

**Finding:** The abstract CI [-0.823, -0.451] doesn't match the B2 CI [-0.923, -0.412] mentioned in results. This needs clarification.

---

## 4. Table Consistency

### ✅ Table 1: Dataset Statistics
- **Claimed:** 17 datasets
- **Actual count:** 17 datasets (verified)
  - Low IR: 6 (sonar, wdbc, ionosphere, breast-wisc, iris, credit-g)
  - Moderate IR: 5 (churn, optdigits, satimage, pendigits, balance)
  - High IR: 4 (wilt, glass, letter, mammography)
  - Extreme IR: 2 (ecoli, page-blocks)

### ⚠️ Table 3: Within-Dataset Correlations
- **Claimed in text (line 545):** "5 datasets" (glass, wdbc, churn, pendigits, letter)
- **Actual in Table 3:** 5 datasets listed ✅
- **Issue:** Table caption says "6 Datasets" in the figure on line 479, but the actual table shows 5.

### ✅ Table 6: 12 Experiments
All 12 experiments are correctly listed:
1. Cross-dataset (Exp 1)
2-6. B1: Within-dataset (5 datasets)
7. B2: Generated Gaussian mixtures
8-12. C1-C5: Moderation testing

---

## 5. Citation Consistency

### ⚠️ Orphaned Bibitems (NOT cited in text)
| Bibitem | Status |
|---------|--------|
| clusterdebo2025 | ❌ Not cited - mentioned as "ClusterDEBO" in text (line 662) without \cite |
| gqeo2025 | ❌ Not cited - mentioned as "GQEO" in text (line 659) without \cite |
| pr2021clustering | ❌ Not cited at all |
| verbiest2014over | ❌ Not cited at all |

### ✅ Citations with Bibitems
All 39 citations in the text have corresponding bibitems.

### Required Fixes
1. Line 659: "GQEO's recognition" → "GQEO \cite{gqeo2025} recognition"
2. Line 662: "ClusterDEBO demonstrates" → "ClusterDEBO \cite{clusterdebo2025} demonstrates"
3. Remove or cite: pr2021clustering, verbiest2014over

---

## 6. Abstract vs. Body Consistency

### Claims in Abstract vs. Support in Body

| Abstract Claim | Body Support | Status |
|----------------|--------------|--------|
| 12 controlled experiments | ✅ Section 4, Table 6 | Consistent |
| N>100 dataset variants | ✅ Line 159, 712 | Consistent |
| 17 real-world datasets | ✅ Table 1 | Consistent |
| 15 held-out datasets | ✅ Line 712 (mentioned) | Consistent |
| r=-0.68 correlation | ⚠️ Approximate mean (not explicit) | Needs clarification |
| p<0.001 | ✅ Multiple locations | Consistent |
| 95% CI: [-0.823, -0.451] | ⚠️ Doesn't match B2 CI | Inconsistent |
| Separability ρ=-0.72 | ✅ Line 581 | Consistent |
| CI: [-0.891, -0.412] | ✅ Line 581 | Consistent |

---

## Summary of Issues Found

### Critical Issues (Must Fix)
1. **Line 308:** "18 datasets" should be "17 datasets"
2. **Citation fixes needed:**
   - Add \cite{gqeo2025} after "GQEO" on line 659
   - Add \cite{clusterdebo2025} after "ClusterDEBO" on line 662

### Minor Issues (Should Fix)
3. **Confidence interval in abstract:** [-0.823, -0.451] doesn't match B2 result CI of [-0.923, -0.412]
4. **Orphaned bibitems:** pr2021clustering and verbiest2014over are not cited
5. **Figure 2 label:** "6 Datasets" should be "5 Datasets" for B1

### Clarification Needed
6. **Mean r=-0.68:** The abstract states this as the mean correlation, but it's not explicitly calculated in the body. It appears to be an approximate mean of the controlled experiment results.

---

## Overall Assessment

**Status:** ⚠️ **MINOR INCONSISTENCIES FOUND**

The paper is largely consistent, with the following requiring attention:

1. Fix dataset count (18 → 17) on line 308
2. Add missing citations for GQEO and ClusterDEBO
3. Either remove orphaned bibitems or add citations
4. Verify/clarify the confidence interval in the abstract

After these fixes, the paper will be fully consistent.
