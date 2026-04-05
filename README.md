# Data Characteristics as Critical Moderators of Oversampling Method Selection

[![Paper](https://img.shields.io/badge/Paper-Pattern%20Recognition-blue)](https://www.sciencedirect.com/journal/pattern-recognition)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

This repository contains the code and data for the paper "Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection" submitted to Pattern Recognition.

## 📋 Abstract

The prevailing IR-threshold paradigm posits a positive correlation between imbalance ratio (IR) and oversampling effectiveness, yet this assumption remains empirically unsubstantiated through controlled experimentation. We conducted 12 controlled experiments (N>100 dataset variants) that systematically manipulated IR while holding data characteristics (class separability, cluster structure) constant via algorithmic generation of Gaussian mixture datasets. Upon controlling for confounding variables, IR exhibited a weak to moderate negative correlation with oversampling benefits (ranging from r=-0.15 for AUC-ROC to r=-0.86 for Recall, mean r=-0.47 across metrics). Class separability emerged as a substantially stronger moderator (ρ=-0.72, p=0.003), explaining significantly more variance in method effectiveness than IR alone. Method selection should be guided by data characteristics rather than IR in isolation. We propose a "Context Matters" framework that integrates IR, class separability, and cluster structure to provide evidence-based selection criteria for practitioners.

## 🔑 Keywords

- Class imbalance
- Oversampling method selection
- Imbalance ratio
- Data characteristics
- Class separability

## 📁 Repository Structure

```
.
├── src/                          # Source code
│   ├── validate_algorithm1.py    # Algorithm 1 validation script
│   └── validate_separability.py  # Separability measure validation
├── data/                         # Dataset information
│   └── README.md                 # Dataset descriptions
├── results/                      # Validation results
│   └── algorithm1_validation.csv # Algorithm 1 validation results
├── figures/                      # Paper figures
│   ├── figure3_moderation_effects.png
│   ├── fig_combined_validation.pdf
│   └── supplementary_E2_sampling_distribution.png
├── docs/                         # Paper and documentation
│   ├── Manuscript_PR_Ready.tex   # Main LaTeX manuscript
│   ├── Response_to_Reviewers.md  # Response to reviewers
│   └── ...                       # Additional documentation
├── requirements.txt              # Python dependencies
├── LICENSE                       # License file
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jiangyuwen2026/imbalanced-learning-moderators.git
cd imbalanced-learning-moderators
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Required Packages

```
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
matplotlib>=3.4.0
seaborn>=0.11.0
imblearn>=0.9.0
scipy>=1.7.0
```

## 📝 Usage

### Running Algorithm 1 Validation

```bash
cd src
python validate_algorithm1.py
```

This script validates the proposed selection algorithm against baseline strategies on real-world datasets.

### Running Separability Measure Validation

```bash
cd src
python validate_separability.py
```

This script validates the separability measure's predictive validity on real datasets.

## 📊 Experimental Design

### 12 Controlled Experiments

The study comprises three stages:

#### Stage 1: Observational Baseline
- **Experiment 1**: Cross-dataset analysis (17 real datasets from OpenML)
- **Result**: r = +0.9662, p < 0.001 (positive correlation in observational data)

#### Stage 2: Controlled Manipulation
- **Experiments 2-6 (B1)**: Within-dataset IR manipulation (5 datasets)
- **Experiment 7 (B2)**: Generated Gaussian mixtures (12 synthetic configurations)
- **Result**: r = -0.765, p < 0.001 (negative correlation with controlled confounds)

#### Stage 3: Moderation Testing
- **Experiment 8 (C1)**: Separability variation (6 levels)
- **Experiment 9 (C2)**: Cluster structure (5 configurations)
- **Experiment 10 (C3)**: Sample size variation (6 levels)
- **Experiment 11 (C4)**: Combined moderation (full factorial)
- **Experiment 12 (C5)**: Validation on held-out data

### Key Findings

1. **Negative Independent Effect**: IR exhibits negative correlation with oversampling benefits (mean r=-0.47) when confounds are controlled
2. **Separability as Primary Moderator**: ρ=-0.72, p=0.003 (95% CI: [-0.891, -0.412])
3. **Multi-factor Moderation**: Cluster structure and sample size also show significant moderating effects
4. **No Universal Optimality**: Method selection should be contingent upon measured data characteristics

## 🔬 Datasets

### Real Datasets (17 from OpenML)

| Dataset | Domain | IR | n | d |
|---------|--------|----|---|---|
| sonar | Signal | 1.14 | 208 | 60 |
| wdbc | Medical | 1.68 | 569 | 30 |
| ionosphere | Radar | 1.79 | 351 | 34 |
| churn | Business | 6.07 | 5000 | 16 |
| glass | Material | 22.78 | 214 | 9 |
| ecoli | Biology | 167.00 | 336 | 7 |
| ... | ... | ... | ... | ... |

### Synthetic Datasets

- **Imbalance Ratio**: 2, 5, 10, 15, 20, 30, 50, 80
- **Separability**: 0.3, 0.5, 0.8, 1.0, 1.5, 2.0
- **Cluster Structure**: 1, 2, 3, 5 clusters

## 📈 Results

### Main Results

| Metric | Correlation with IR | Effect Size |
|--------|---------------------|-------------|
| Recall | r = -0.86*** | Large |
| Specificity | r = -0.89*** | Large |
| F1-Score | r = -0.68*** | Medium-Large |
| G-Mean | r = -0.67*** | Medium-Large |
| AUC-ROC | r = -0.40*** | Medium |
| AUC-PR | r = -0.32** | Small-Medium |

***p < 0.001, **p < 0.01

### Separability Moderation

- **Low Separability (S < 0.5)**: Cohen's d = 0.82 (large effect)
- **High Separability (S > 1.0)**: Cohen's d = 0.34 (medium effect)
- **Overall Correlation**: ρ = -0.72, p = 0.003

## 📚 Citation

If you use this code or data in your research, please cite:

```bibtex
@article{jiang2026imbalance,
  title={Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection},
  author={Jiang, Yuwen and Ye, Songyun},
  journal={Pattern Recognition},
  year={2026},
  publisher={Elsevier}
}
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or inquiries, please contact:

- **Jiang Yuwen**: jiangyuwen@gzist.edu.cn
- **Ye Songyun** (Corresponding Author): yesongyun@gzist.edu.cn

**Affiliation**: School of Artificial Intelligence, Guangzhou Institute of Science and Technology, Guangzhou, China

## 🙏 Acknowledgments

This research was supported by the Guangzhou Institute of Science and Technology. We thank the reviewers for their constructive feedback.

## 🔗 Related Links

- [Pattern Recognition Journal](https://www.sciencedirect.com/journal/pattern-recognition)
- [OpenML Datasets](https://www.openml.org/)
- [imbalanced-learn Documentation](https://imbalanced-learn.org/)

---

**Last Updated**: April 5, 2026
