# Figure Checklist for Pattern Recognition Submission

> **Document Purpose**: Verify all figures are correctly referenced and included in the submission package

---

## 📊 Figures in the Manuscript

### Figure 1: Theoretical Framework
- **Type**: TikZ diagram (embedded in LaTeX)
- **Location**: Section 3.2, Line ~191
- **Label**: `\label{fig:framework}`
- **Status**: ✅ Embedded (no external file needed)

### Figure 2: Controlled Experiments Workflow
- **Type**: TikZ diagram (embedded in LaTeX)
- **Location**: Section 4.2, Line ~449
- **Label**: `\label{fig:controlled_summary}`
- **Status**: ✅ Embedded (no external file needed)

### Figure 3: Separability Moderation Effects
- **Type**: External image
- **Location**: Section 5.3, Line 581
- **File**: `figure3_moderation_effects.png`
- **Label**: `\label{fig:sep_moderation}`
- **Caption**: "Separability moderates oversampling effectiveness. Low separability data benefits more from oversampling."
- **Status**: ✅ Included in PR_Paper_Final.zip
- **Formats Available**: PNG (405KB), PDF (570KB)

### Figure 4: Boundary Visualization
- **Type**: External image
- **Location**: Section 5.5, Line 715
- **File**: `supplementary_E2_sampling_distribution.png`
- **Label**: `\label{fig:boundary_viz}`
- **Caption**: "Comparison of SMOTE and BorderlineSMOTE: SMOTE generates samples through linear interpolation..."
- **Status**: ✅ Included in PR_Paper_Final.zip
- **Formats Available**: PNG (814KB), PDF (910KB)

### Figure 5: Validation Experiments Summary
- **Type**: External image
- **Location**: Section 4.4, Line 683
- **File**: `fig_combined_validation.pdf`
- **Label**: `\label{fig:validation}`
- **Caption**: "Validation experiments demonstrating metric-dependence and ceiling effects..."
- **Status**: ✅ Included in PR_Paper_Final.zip
- **Formats Available**: PDF (35KB), PNG (401KB)

---

## 📁 Files in Submission Package

### External Image Files (6 files)

| Filename | Format | Size | Status |
|----------|--------|------|--------|
| figure3_moderation_effects.png | PNG | 405KB | ✅ Included |
| figure3_moderation_effects.pdf | PDF | 570KB | ✅ Included |
| supplementary_E2_sampling_distribution.png | PNG | 814KB | ✅ Included |
| supplementary_E2_sampling_distribution.pdf | PDF | 910KB | ✅ Included |
| fig_combined_validation.png | PNG | 401KB | ✅ Included |
| fig_combined_validation.pdf | PDF | 35KB | ✅ Included |

### Embedded Figures (2 figures)

| Figure | Type | Status |
|--------|------|--------|
| Figure 1: Theoretical Framework | TikZ | ✅ Embedded in .tex |
| Figure 2: Controlled Experiments | TikZ | ✅ Embedded in .tex |

---

## ✅ Pre-Submission Verification

### Checklist

- [x] All external figure files exist
- [x] All external figure files are included in PR_Paper_Final.zip
- [x] Both PNG and PDF formats included (LaTeX can use either)
- [x] Figure labels match references in text
- [x] All figures have captions
- [x] No orphaned figure references

### Verification Commands

```bash
# Check all figure references in manuscript
grep -n "includegraphics" Manuscript_PR_Ready.tex

# Check all figure labels
grep -n "label{fig:" Manuscript_PR_Ready.tex

# List all image files in zip
unzip -l PR_Paper_Final.zip | grep -E "\.(png|pdf)$"
```

---

## 📋 Submission Package Structure

```
PR_Paper_Final.zip/
├── Manuscript_PR_Ready.tex          (Main manuscript)
├── figure3_moderation_effects.png   (Figure 3)
├── figure3_moderation_effects.pdf   (Figure 3, alternative format)
├── fig_combined_validation.png      (Figure 5)
├── fig_combined_validation.pdf      (Figure 5, alternative format)
├── supplementary_E2_sampling_distribution.png  (Figure 4)
├── supplementary_E2_sampling_distribution.pdf  (Figure 4, alternative format)
└── [other files...]
```

---

## 🎯 Notes for Editors/Reviewers

1. **TikZ Figures**: Figures 1 and 2 are embedded TikZ diagrams and will render automatically when compiling the LaTeX file.

2. **Image Formats**: Both PNG and PDF versions are provided for maximum compatibility:
   - PDF is preferred for vector-quality output
   - PNG is provided as fallback

3. **Figure Resolution**: All raster images (PNG) are at least 300 DPI, suitable for print publication.

4. **Color Figures**: All figures are designed to be readable in both color and grayscale printing.

---

## 🔍 Troubleshooting

### If figures don't display in compiled PDF:

1. **Check file paths**: Ensure images are in the same directory as the .tex file
2. **Check file names**: Verify exact spelling matches the `\includegraphics` command
3. **For Overleaf**: Upload all image files to the project root directory
4. **For local LaTeX**: Run `pdflatex` or `xelatex` with images in the working directory

---

**Last Updated**: 2026-04-05  
**Document Version**: 1.0
