# ORCID 显示方式优化选项

## 当前显示方式

```latex
\author{
 Jiangyuwen$^{1,*}$ (ORCID: 0009-0001-4022-1436)~~~~Ye Songyun$^{1,\dagger}$ (ORCID: 0009-0009-5048-3147)
}
```

**问题**：占用太多空间，显得冗长

---

## 方案1：使用 ORCID 图标链接（推荐 ⭐）

使用 ORCID 官方图标，点击可跳转，学术标准格式：

```latex
\usepackage{hyperref}
\usepackage{orcidlink}  % 添加此包

\author{
 Jiangyuwen$^{1,*}$\orcidlink{0009-0001-4022-1436}~~~~
 Ye Songyun$^{1,\dagger}$\orcidlink{0009-0009-5048-3147}\\[0.8em]
 \normalsize $^1$School of Artificial Intelligence...
}
```

**效果**：显示为小巧的 ORCID 图标（🟢），点击跳转到 ORCID 页面

---

## 方案2：脚注显示（最简洁）

将 ORCID 移到脚注，作者行保持简洁：

```latex
\author{
 Jiangyuwen$^{1,*}$~~~~Ye Songyun$^{1,\dagger}$\thanks{ORCID: 0009-0009-5048-3147}\\[0.8em]
 \normalsize $^1$School of Artificial Intelligence...
}

\footnotetext[1]{ORCID: 0009-0001-4022-1436}
```

**效果**：作者行只显示名字，ORCID 在页面底部脚注显示

---

## 方案3：小号字上标（紧凑）

使用小字号上标，不占用主行空间：

```latex
\author{
 Jiangyuwen$^{1,*}$\textsuperscript{\tiny ORCID:0009-0001-4022-1436}~~~~
 Ye Songyun$^{1,\dagger}$\textsuperscript{\tiny ORCID:0009-0009-5048-3147}\\[0.8em]
 \normalsize $^1$School of Artificial Intelligence...
}
```

**效果**：ORCID 以小字上标形式显示，不突兀

---

## 方案4：仅保留在标题页（完全隐藏）

从正文完全移除 ORCID，只在 `title_page.docx` 中显示：

```latex
\author{
 Jiangyuwen$^{1,*}$~~~~Ye Songyun$^{1,\dagger}$\\[0.8em]
 \normalsize $^1$School of Artificial Intelligence...
}
```

**效果**：正文作者行最简洁，ORCID 信息只在单独的 title_page 文件中

---

## 推荐方案

对于 **Pattern Recognition** 期刊投稿，推荐使用：

- **方案1（ORCID 图标）**：现代、专业、符合学术规范
- **方案4（完全隐藏）**：如果期刊不要求正文中显示 ORCID

---

## 快速实现

运行以下命令应用方案1（ORCID 图标）：

```bash
cd "/Users/jiangyuwen/Research/不均衡样本/IJSmartGrid_Submission/PR_Submission_Materials"
# 修改 Manuscript_PR_Ready.tex
```

或直接上传清理后的版本到 Overleaf。
