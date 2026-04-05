# 需要修正的问题及解决方案

**文档**: Manuscript_PR.tex  
**目标**: Pattern Recognition期刊格式要求

---

## 🚨 高优先级修正（必须完成）

### 问题1: 文档类不正确

**当前状态**:
```latex
\documentclass{ijSmartGrid}
```

**问题**: 使用的是IJSmartGrid期刊的文档类，不是标准article类

**解决方案**:
```latex
\documentclass[12pt,a4paper,oneside]{article}
```

---

### 问题2: 缺少双倍行距设置

**当前状态**: 未检测到setspace包和doublespacing命令

**问题**: PR要求单栏双倍行距

**解决方案**: 在导言区添加
```latex
\usepackage{setspace}
\doublespacing
```

---

### 问题3: 缺少页面设置

**当前状态**: 未使用geometry包

**问题**: 需要设置2.54cm页边距

**解决方案**: 在导言区添加
```latex
\usepackage[margin=2.54cm]{geometry}
```

---

## 🔧 完整修正后的导言区

将Manuscript_PR.tex的开头部分替换为以下内容：

```latex
%% Paper for Pattern Recognition Journal
%% Reformatted from: Beyond Imbalance Ratio: Data Characteristics as Critical Moderators

\documentclass[12pt,a4paper,oneside]{article}

%% === Page Layout (PR Requirements) ===
\usepackage[margin=2.54cm]{geometry}
\usepackage{setspace}
\doublespacing

%% ---- Additional packages (add as needed) ----
\usepackage{booktabs}      % Professional tables
\usepackage{multirow}      % Multi-row table cells
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{xcolor}
\usepackage{subcaption}    % Sub-figures
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta}
\usepackage{amsthm}
\usepackage{amsmath}
\usepackage{amssymb}
\theoremstyle{definition}
\newtheorem{hypothesis}{Hypothesis}
\usepackage{hyperref}      % Clickable links in PDF (load last)
\hypersetup{
  colorlinks = true,
  linkcolor  = black,
  citecolor  = black,
  urlcolor   = black
}

%% ---- Custom hyphenation to prevent overflow ----
\hyphenation{over-sam-pling im-bal-anced sep-a-ra-bil-ity}

%% ============================================================
%%  TITLE BLOCK INFORMATION
%% ============================================================

\title{Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection}

\author{
  Jiangyuwen$^{1,*}$, Ye Songyun$^{1,\dagger}$
}

\date{
  $^1$School of Artificial Intelligence, Guangzhou Institute of Science and Technology, Guangzhou, China\\[0.5em]
  $^*$jiangyuwen@gzist.edu.cn\\
  $^\dagger$Corresponding author: yesongyun@gzist.edu.cn
}

%% ============================================================
%%  DOCUMENT BODY
%% ============================================================
\begin{document}

\maketitle

%% ---- Abstract (max 250 words, no citations) ----
\begin{abstract}
...
```

---

## 📋 修正步骤清单

### 步骤1: 备份原文件
```bash
cp Manuscript_PR.tex Manuscript_PR.tex.backup
```

### 步骤2: 修改文档类
1. 打开 `Manuscript_PR.tex`
2. 将第4行 `\documentclass{ijSmartGrid}` 替换为 `\documentclass[12pt,a4paper,oneside]{article}`

### 步骤3: 添加格式包
在第7行之前添加：
```latex
%% === Page Layout (PR Requirements) ===
\usepackage[margin=2.54cm]{geometry}
\usepackage{setspace}
\doublespacing
```

### 步骤4: 修改作者格式
将原有的复杂作者格式简化为：
```latex
\author{
  Jiangyuwen$^{1,*}$, Ye Songyun$^{1,\dagger}$
}

\date{
  $^1$School of Artificial Intelligence, Guangzhou Institute of Science and Technology, Guangzhou, China\\[0.5em]
  $^*$jiangyuwen@gzist.edu.cn\\
  $^\dagger$Corresponding author: yesongyun@gzist.edu.cn
}
```

### 步骤5: 删除IJSmartGrid专用命令
删除或注释掉以下命令（如果存在）：
- `\ijaffiliation{...}`
- `\ijemail{...}`
- `\corresponding{...}`
- `\receivedaccepted{...}`
- `\ijshortauthor{...}`
- `\ijvolume{...}`
- `\ijissue{...}`
- `\ijpubmonth{...}`
- `\ijpubyear{...}`
- `\ijarticletype{...}`

### 步骤6: 编译测试
```bash
pdflatex Manuscript_PR.tex
bibtex Manuscript_PR
pdflatex Manuscript_PR.tex
pdflatex Manuscript_PR.tex
```

---

## ✅ 修正后检查清单

修正完成后，确认：
- [ ] 文档类是 `\documentclass[12pt,a4paper,oneside]{article}`
- [ ] 包含 `\usepackage[margin=2.54cm]{geometry}`
- [ ] 包含 `\usepackage{setspace}` 和 `\doublespacing`
- [ ] 作者格式简化
- [ ] 无IJSmartGrid专用命令
- [ ] 编译成功，无错误
- [ ] 输出PDF为单栏双倍行距格式
- [ ] 页数在20-35页之间

---

## 🎯 预期结果

修正后，论文应该：
1. ✅ 使用标准article类编译
2. ✅ 显示为单栏格式
3. ✅ 行距为双倍
4. ✅ 页边距为2.54cm
5. ✅ 总页数约28页
6. ✅ 符合Pattern Recognition格式要求

---

## 🆘 常见问题

### Q: 编译报错 "Undefined control sequence"
**A**: 检查是否删除了所有IJSmartGrid专用命令

### Q: 页边距不正确
**A**: 确保geometry包已加载且参数正确 `[margin=2.54cm]`

### Q: 行距仍然是单倍
**A**: 确保在`\begin{document}`之前使用了`\doublespacing`

### Q: 图表位置错乱
**A**: 标准article类的浮动体参数与IJSmartGrid不同，可能需要调整`[!ht]`参数

---

*修正指南生成时间: 2025年4月*
*目标期刊: Pattern Recognition*
