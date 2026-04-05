# Datasets

This directory contains information about the datasets used in the paper.

## Real Datasets (17 from OpenML)

All real datasets were obtained from [OpenML](https://www.openml.org/) and represent diverse domains:

| ID | Dataset | Domain | IR | n | d | OpenML ID |
|----|---------|--------|----|---|---|-----------|
| 1 | sonar | Signal | 1.14 | 208 | 60 | 40 |
| 2 | wdbc | Medical | 1.68 | 569 | 30 | 15 |
| 3 | ionosphere | Radar | 1.79 | 351 | 34 | 59 |
| 4 | breast-wisc | Medical | 1.86 | 699 | 9 | 15 |
| 5 | diabetes | Medical | 1.87 | 768 | 8 | 37 |
| 6 | adult | Social | 3.17 | 48842 | 14 | 1590 |
| 7 | churn | Business | 6.07 | 5000 | 16 | 40701 |
| 8 | vehicle | Image | 9.32 | 846 | 18 | 54 |
| 9 | pima | Medical | 13.41 | 768 | 8 | 37 |
| 10 | german | Credit | 15.08 | 1000 | 20 | 31 |
| 11 | segment | Image | 26.67 | 2310 | 19 | 40996 |
| 12 | glass | Material | 22.78 | 214 | 9 | 41 |
| 13 | yeast | Biology | 77.59 | 1484 | 8 | 181 |
| 14 | satimage | Image | 96.57 | 6435 | 36 | 182 |
| 15 | page-blocks | Text | 167.86 | 5473 | 10 | 30 |
| 16 | ecoli | Biology | 167.00 | 336 | 7 | 39 |
| 17 | abalone | Biology | 162.00 | 4177 | 8 | 1557 |

## Synthetic Datasets

Gaussian mixture datasets were generated with the following parameter ranges:

### Experiment 7 (B2): IR Manipulation
- **IR values**: 2, 5, 10, 15, 20, 30, 50, 80
- **Fixed parameters**: d=20, S=0.8, k=2
- **Repetitions**: 10 random seeds

### Experiment 8 (C1): Separability Variation
- **Separability (S)**: 0.3, 0.5, 0.8, 1.0, 1.5, 2.0
- **Fixed parameters**: IR=10, d=20, k=2
- **Repetitions**: 10 random seeds

### Experiment 9 (C2): Cluster Structure
- **Cluster number (k)**: 1, 2, 3, 4, 5
- **Fixed parameters**: IR=10, d=20, S=0.8
- **Repetitions**: 10 random seeds

### Experiment 10 (C3): Sample Size
- **Sample sizes (n)**: 200, 500, 1000, 2000, 5000, 10000
- **Fixed parameters**: IR=10, d=20, S=0.8, k=2
- **Repetitions**: 10 random seeds

### Experiment 11 (C4): Full Factorial
- **Combined design**: All combinations of IR × S × k
- **Total configurations**: 192
- **Repetitions**: 5 random seeds

## Data Access

The real datasets are publicly available from OpenML. Synthetic datasets were generated using the `make_classification` and custom Gaussian mixture functions in scikit-learn.

To regenerate the synthetic datasets, see the code in `src/generate_synthetic_data.py` (coming soon).

## Citation

If you use these datasets, please cite both this paper and the original OpenML sources:

```bibtex
@article{jiang2026imbalance,
  title={Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection},
  author={Jiang, Yuwen and Ye, Songyun},
  journal={Pattern Recognition},
  year={2026},
  publisher={Elsevier}
}

@article{vanschoren2014openml,
  title={OpenML: Networked science in machine learning},
  author={Vanschoren, Joaquin and van Rijn, Jan N and Bischl, Bernd and Torgo, Luis},
  journal={ACM SIGKDD Explorations Newsletter},
  volume={15},
  number={2},
  pages={49--60},
  year={2014}
}
```
