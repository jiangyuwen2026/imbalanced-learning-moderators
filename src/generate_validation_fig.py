#!/usr/bin/env python3
"""
Generate combined validation figure for Experiment A and B
"""

import matplotlib.pyplot as plt
import numpy as np

# Set up the figure with 2x2 layout
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Validation Experiments: Ceiling Effects and Metric-Dependence', 
             fontsize=14, fontweight='bold', y=0.98)

# ========== Experiment A: Ceiling Effect Control (Top Row) ==========
# Data from validation experiments
metrics_A = ['AUC-ROC', 'AUC-PR', 'F1-Score', 'G-Mean']
absolute_r = [-0.14, -0.08, -0.53, -0.40]
relative_r = [-0.41, -0.15, -0.75, -0.73]

# Plot 1: Absolute vs Relative improvement
ax1 = axes[0, 0]
x = np.arange(len(metrics_A))
width = 0.35
bars1 = ax1.bar(x - width/2, absolute_r, width, label='Absolute', color='#3498db', alpha=0.8)
bars2 = ax1.bar(x + width/2, relative_r, width, label='Relative', color='#e74c3c', alpha=0.8)
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax1.set_xlabel('Evaluation Metric', fontsize=10)
ax1.set_ylabel('Correlation with IR', fontsize=10)
ax1.set_title('(A) Ceiling Effect Control\nAbsolute vs. Relative Improvement', fontsize=11)
ax1.set_xticks(x)
ax1.set_xticklabels(metrics_A, rotation=15, ha='right')
ax1.legend(loc='lower left')
ax1.set_ylim(-1, 0.2)
ax1.grid(axis='y', alpha=0.3)

# Add significance markers
for i, (a, r) in enumerate(zip(absolute_r, relative_r)):
    if abs(r) > 0.7:
        ax1.annotate('***', xy=(i + width/2, r - 0.08), ha='center', fontsize=9, color='red')

# Plot 2: Effect size classification
ax2 = axes[0, 1]
effect_labels = ['Weak\n(|r|<0.3)', 'Small\n(0.3-0.5)', 'Medium\n(0.5-0.7)', 'Strong\n(|r|>0.7)']
effect_counts = [1, 1, 0, 2]  # Count of metrics in each category for relative
bars = ax2.barh(effect_labels, effect_counts, color=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c'])
ax2.set_xlabel('Number of Metrics', fontsize=10)
ax2.set_title('(B) Effect Size Distribution\n(Ceiling-Controlled)', fontsize=11)
ax2.set_xlim(0, 3)
for i, v in enumerate(effect_counts):
    ax2.text(v + 0.1, i, str(v), va='center')

# ========== Experiment B: Multi-Metric Validation (Bottom Row) ==========
# Data from validation experiments
metrics_B = ['Recall', 'Specificity', 'Bal-Acc', 'F1', 'G-Mean', 'AUC-ROC', 'AUC-PR', 'Precision']
correlations_B = [-0.86, -0.89, -0.72, -0.68, -0.67, -0.40, -0.32, 0.36]
colors_B = ['#e74c3c' if r < 0 else '#2ecc71' for r in correlations_B]

# Plot 3: Correlation by metric
ax3 = axes[1, 0]
y_pos = np.arange(len(metrics_B))
bars = ax3.barh(y_pos, correlations_B, color=colors_B, alpha=0.8)
ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(metrics_B)
ax3.set_xlabel('Correlation with IR', fontsize=10)
ax3.set_title('(C) Multi-Metric Validation\n8 Evaluation Metrics', fontsize=11)
ax3.set_xlim(-1, 0.5)
ax3.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, correlations_B)):
    x_pos = val - 0.05 if val < 0 else val + 0.05
    align = 'right' if val < 0 else 'left'
    ax3.annotate(f'{val:+.2f}', xy=(x_pos, i), ha=align, va='center', fontsize=9)

# Plot 4: Summary statistics
ax4 = axes[1, 1]
categories = ['Class-Specific\nMetrics', 'Ranking\nMetrics', 'All\nMetrics']
mean_r = [-0.72, -0.36, -0.47]
std_r = [0.10, 0.06, 0.08]
x_pos = np.arange(len(categories))
bars = ax4.bar(x_pos, mean_r, yerr=std_r, capsize=5, 
               color=['#e74c3c', '#3498db', '#9b59b6'], alpha=0.8)
ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax4.set_xticks(x_pos)
ax4.set_xticklabels(categories)
ax4.set_ylabel('Mean Correlation (r)', fontsize=10)
ax4.set_title('(D) Metric Category Comparison\n(Mean ± SD)', fontsize=11)
ax4.set_ylim(-1, 0.2)
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, mean_r)):
    ax4.annotate(f'{val:.2f}', xy=(i, val - 0.08), ha='center', fontsize=10, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save figure
plt.savefig('fig_combined_validation.pdf', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('fig_combined_validation.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: fig_combined_validation.pdf and fig_combined_validation.png")
