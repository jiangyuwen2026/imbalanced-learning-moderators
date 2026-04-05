# Overleaf 上传指南 - 解决编译错误

## 问题原因

错误：`LaTeX Error: File 'ijSmartGrid.cls' not found`

**原因**：`Manuscript_PR.tex` 使用了 `\documentclass{ijSmartGrid}`，这需要特殊的 `.cls` 文件。

## 解决方案

### 正确的投稿文件

使用 **`Manuscript_PR_Ready.tex`**（不是 `Manuscript_PR.tex`）

```latex
\documentclass[12pt,a4paper]{article}  % ✅ 标准article类
```

### 清理步骤

#### 步骤1：删除旧文件
在 Overleaf 项目中删除以下文件：
- `Manuscript_PR.tex`（旧格式，不需要）
- `ijSmartGrid.cls`（如果存在）
- 所有 `.aux` 文件（辅助文件）

#### 步骤2：只上传正确的文件

**必需文件列表**:
```
Manuscript_PR_Ready.tex          ← 主文件（使用这个！）
figure3_moderation_effects.png   ← 图3
fig_combined_validation.png      ← 图4
supplementary_E2_sampling_distribution.png  ← 图5
```

**不要上传**:
- `Manuscript_PR.tex`
- `ijSmartGrid.cls`
- 任何 `.aux`, `.log`, `.out` 文件

#### 步骤3：设置主文件

1. 在 Overleaf 左侧面板中，点击 `Manuscript_PR_Ready.tex`
2. 点击右上角的齿轮图标 ⚙️
3. 选择 "Set as Main File"

#### 步骤4：重新编译

点击 "Recompile" 按钮

---

## 快速修复：清理后的提交包

已创建 `overleaf_clean_upload.zip`，包含：
- ✅ Manuscript_PR_Ready.tex（主文件）
- ✅ 所有图片文件
- ❌ 不含 Manuscript_PR.tex
- ❌ 不含任何辅助文件

直接上传此zip文件到 Overleaf 即可！

---

## 文件区别

| 文件 | 文档类 | 用途 |
|------|--------|------|
| Manuscript_PR_Ready.tex | article | ✅ Pattern Recognition投稿（用这个） |
| Manuscript_PR.tex | ijSmartGrid | ❌ 旧版本，不需要 |

---

## 如果问题仍然存在

1. 创建全新的 Overleaf 项目
2. 上传 `overleaf_clean_upload.zip`
3. 确保主文件设置为 `Manuscript_PR_Ready.tex`
4. 重新编译

---

## 成功编译的标志

看到以下输出表示成功：
```
Output written on Manuscript_PR_Ready.pdf (28 pages, ...)
Transcript written on Manuscript_PR_Ready.log.
```
