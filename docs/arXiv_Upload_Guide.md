# arXiv 论文上传完整指南

**论文标题**: Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection  
**目标平台**: arXiv (cs.LG - Machine Learning)  
**创建日期**: 2026-04-05

---

## 📋 一、上传前准备

### 1.1 注册 arXiv 账号

1. 访问 https://arxiv.org/user/register
2. 填写注册信息：
   - **Username**: 建议用机构邮箱前缀
   - **Email**: 使用机构邮箱 (如 jiangyuwen@gzist.edu.cn)
   - **Password**: 设置强密码
3. 验证邮箱（会收到验证邮件）
4. 等待账号激活（通常几分钟到几小时）

### 1.2 获取投稿权限（首次投稿需要）

arXiv 要求首次投稿者获得"Endorsement"：

**方法1：通过机构邮箱自动获得**
- 使用 .edu 邮箱注册通常自动获得权限

**方法2：请求推荐**
- 请已发表过arXiv论文的同事推荐
- 在 https://arxiv.org/auth/endorse 申请

**方法3：提交至指定类别**
- 选择 "cs.LG" (Machine Learning) 通常较容易获得权限

---

## 📁 二、准备上传文件

### 2.1 arXiv 接受的文件格式

| 格式 | 说明 | 推荐度 |
|------|------|--------|
| **TeX/LaTeX** | 源文件上传（推荐） | ⭐⭐⭐⭐⭐ |
| **PDF** | 直接上传PDF | ⭐⭐⭐ |
| **HTML** | 实验性支持 | ⭐ |

**推荐使用 LaTeX 源文件上传**（便于arXiv重新编译）

### 2.2 准备文件清单

在 `PR_Submission_Materials` 目录下创建 `arxiv_submission` 文件夹：

```bash
mkdir -p arxiv_submission
cd arxiv_submission
```

**必需文件**:

```
arxiv_submission/
├── main.tex                    # 主文件（从Manuscript_PR_Ready.tex复制）
├── figure3_moderation_effects.png    # 图3
├── fig_combined_validation.png       # 图4
├── supplementary_E2_sampling_distribution.png  # 图5
└── (其他依赖文件)
```

### 2.3 修改主文件以适应arXiv

创建 `arxiv_main.tex`：

```latex
%% arXiv Submission Version
%% Original: Manuscript_PR_Ready.tex

\documentclass[12pt,a4paper]{article}

%% arXiv 推荐包
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{xcolor}
\usepackage{subcaption}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta}
\usepackage{amsthm}
\usepackage{hyperref}
\usepackage{url}

%% 页面设置（arXiv接受单栏格式）
\usepackage[margin=2.5cm]{geometry}

%% 定理环境
\theoremstyle{definition}
\newtheorem{hypothesis}{Hypothesis}

%% hyperref 设置
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue,
    breaklinks=true
}

%% 标题信息
\title{Beyond Imbalance Ratio: Data Characteristics as Critical Moderators \\
of Oversampling Method Selection}

\author{
    Jiangyuwen$^{1}$ \and Ye Songyun$^{1}$\\
    $^1$School of Artificial Intelligence, \\
    Guangzhou Institute of Science and Technology, Guangzhou, China\\
    \texttt{jiangyuwen@gzist.edu.cn}, \texttt{yesongyun@gzist.edu.cn}
}

\date{\today}

\begin{document}

\maketitle

%% 添加arXiv说明（可选）
\begin{abstract}
[保持原文摘要]
\end{abstract}

%% 正文内容...
[复制Manuscript_PR_Ready.tex的正文内容]

\end{document}
```

### 2.4 创建提交包

```bash
cd /Users/jiangyuwen/Research/不均衡样本/IJSmartGrid_Submission/PR_Submission_Materials

# 创建arXiv提交目录
mkdir -p arxiv_submission

# 复制主文件
cp Manuscript_PR_Ready.tex arxiv_submission/main.tex

# 复制图片
cp figure3_moderation_effects.png arxiv_submission/
cp fig_combined_validation.png arxiv_submission/
cp supplementary_E2_sampling_distribution.png arxiv_submission/
cp figure3_moderation_effects.pdf arxiv_submission/
cp fig_combined_validation.pdf arxiv_submission/
cp supplementary_E2_sampling_distribution.pdf arxiv_submission/

# 创建tar.gz压缩包
cd arxiv_submission
tar -czvf ../arxiv_submission.tar.gz .

# 验证压缩包
cd ..
ls -lh arxiv_submission.tar.gz
```

---

## 🚀 三、arXiv 上传步骤

### 3.1 登录 arXiv

1. 访问 https://arxiv.org/login
2. 输入用户名和密码
3. 进入用户主页

### 3.2 开始新提交

1. 点击 **"Sumbmit a new article"**
2. 或访问 https://arxiv.org/submit

### 3.3 填写元数据（Metadata）

#### 步骤1：选择类别 (Select a category)

| 主要类别 | 说明 |
|---------|------|
| **cs.LG** | Machine Learning (推荐主类别) |
| cs.AI | Artificial Intelligence |
| stat.ML | Machine Learning (Statistics) |
| cs.SE | Software Engineering |

**建议**: 
- 主类别: `cs.LG`
- 次要类别: `cs.AI`, `stat.ML`

#### 步骤2：填写标题 (Title)

```
Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection
```

#### 步骤3：填写作者 (Authors)

```
Jiangyuwen, Ye Songyun
```

或分开填写：
- Author 1: Jiangyuwen
- Author 2: Ye Songyun

#### 步骤4：填写摘要 (Abstract)

复制 `Manuscript_PR_Ready.tex` 中的摘要内容：

```
Background: The prevailing IR-threshold paradigm posits a positive correlation between imbalance ratio (IR) and oversampling effectiveness, yet this assumption remains empirically unsubstantiated through controlled experimentation.

Methods: We conducted 12 controlled experiments (N>100 dataset variants) that systematically manipulated IR while holding data characteristics (class separability, cluster structure) constant via algorithmic generation of Gaussian mixture datasets. Two additional validation experiments examined ceiling effects and metric-dependence. All methods were evaluated on 17 real-world datasets from OpenML.

Results: Upon controlling for confounding variables, IR exhibited a weak to moderate negative correlation with oversampling benefits (ranging from r=-0.15 for AUC-ROC to r=-0.86 for Recall, mean r=-0.47 across metrics). Class separability emerged as a substantially stronger moderator (ρ=-0.72, p=0.003), accounting for significantly more variance in method effectiveness than IR alone.

Conclusion: Method selection should be guided by data characteristics rather than IR in isolation. We propose a "Context Matters" framework that integrates IR, class separability, and cluster structure to provide evidence-based selection criteria for practitioners.
```

**字数**: 约150词（符合arXiv要求）

#### 步骤5：填写评论/报告号 (Comments)

可选填写：
```
Submitted to Pattern Recognition. 12 controlled experiments, 17 real datasets, 192 synthetic configurations.
```

#### 步骤6：选择许可协议 (License)

| 许可协议 | 说明 | 推荐 |
|---------|------|------|
| **arXiv.org perpetual, non-exclusive license** | 标准许可，允许arXiv永久展示 | ⭐ 推荐 |
| CC BY 4.0 | 创作共用署名许可 | ⭐⭐ 更开放 |
| CC BY-SA 4.0 | 署名-相同方式共享 | |
| CC BY-NC-SA 4.0 | 署名-非商业-相同方式共享 | |
| CC Zero | 公共领域 dedication | |

**建议**: 选择 **CC BY 4.0**（最开放的学术许可）

---

### 3.4 上传文件

#### 方式1：直接上传 TeX 源文件（推荐）

1. 点击 **"Upload file"** 或 **"Choose File"**
2. 选择 `arxiv_submission.tar.gz`
3. 点击 **"Upload"**
4. arXiv 会自动解压并处理

#### 方式2：使用 TeX Live 编译

arXiv 使用 TeX Live 2023 或 2024：
- 支持的编译方式: `pdflatex`, `latex`, `xelatex`, `lualatex`
- 默认使用 `pdflatex`

#### 方式3：上传 PDF（备用）

如果 LaTeX 编译有问题，可以直接上传 PDF：
1. 在本地编译生成 PDF
2. 选择 **"PDF only"** 选项
3. 上传 PDF 文件

**注意**: PDF 上传后会经过审核，可能需要更长时间

---

### 3.5 预览和验证

上传后会显示：
1. **TeX 处理结果**: 显示编译日志
2. **PDF 预览**: 生成的PDF预览
3. **错误检查**: 如有编译错误会显示

**常见问题解决**:

| 问题 | 解决方法 |
|------|---------|
| 图片找不到 | 确保图片路径正确，使用相对路径 |
| 缺少包 | 使用arXiv标准包，避免自定义包 |
| 编译超时 | 简化文档，减少复杂图表 |
| 字体问题 | 使用标准字体，嵌入所有字体 |

---

### 3.6 提交审核

1. 确认所有信息正确
2. 点击 **"Submit"** 或 **"Submit article"**
3. 系统会显示提交确认页面
4. 保存 **arXiv ID**（如 arXiv:2504.00001）

---

## ⏱️ 四、时间线预期

| 阶段 | 时间 |
|------|------|
| 文件处理和编译 | 几分钟 |
| 自动审核（类别检查） | 几小时 |
| 最终发布 | 通常24-48小时 |
| 邮件通知 | 发布后发送 |

---

## 🔗 五、发布后操作

### 5.1 获取 arXiv 链接

发布后论文地址格式：
```
https://arxiv.org/abs/2504.00001    # 摘要页面
https://arxiv.org/pdf/2504.00001    # PDF下载
```

### 5.2 添加到简历/主页

在 CV 或个人主页添加：
```
arXiv:2504.00001 [cs.LG]
```

### 5.3 分享论文

- **Twitter/X**: 使用 #arXiv #MachineLearning 标签
- **LinkedIn**: 分享研究亮点
- **ResearchGate**: 同步上传
- **知乎/微信公众号**: 中文科普

### 5.4 后续版本（如需更新）

1. 登录 arXiv
2. 找到原论文，点击 **"Replace"** 或 **"Withdraw"**
3. 上传新版本文件
4. 填写更新说明

---

## ⚠️ 六、注意事项

### 6.1 版权注意事项

- ✅ 可以上传已投稿期刊的预印本（preprint）
- ✅ 大多数期刊允许arXiv预印本
- ⚠️ 如果期刊已接受，检查期刊的预印本政策
- ❌ 不要上传已发表文章的最终版本（如有版权限制）

**Pattern Recognition 期刊政策**:
- 通常允许预印本在arXiv发布
- 建议投稿前先上传到arXiv

### 6.2 与期刊投稿的关系

| 情况 | 建议 |
|------|------|
| 先传arXiv再投期刊 | ✅ 推荐，证明原创性 |
| 已投期刊再传arXiv | ✅ 通常允许，检查期刊政策 |
| 期刊已接受 | ⚠️ 确认期刊预印本政策 |

### 6.3 避免的问题

- ❌ 不要在arXiv上发布最终发表的版本（如排版后的PDF）
- ❌ 不要上传包含审稿人意见的文件
- ❌ 不要上传版权声明页（如Elsevier的版权页）
- ✅ 保持与投稿期刊版本基本一致

---

## 📧 七、联系支持

如遇问题：

| 问题类型 | 联系方式 |
|---------|---------|
| 技术问题 | help@arxiv.org |
| 类别咨询 | 联系相应领域的版主 |
| 账号问题 | 使用网站的help表单 |

---

## ✅ 八、上传检查清单

提交前确认：

- [ ] arXiv账号已注册并激活
- [ ] 已获得投稿权限（endorsement）
- [ ] 选择了合适的类别（cs.LG为主）
- [ ] 标题、作者、摘要正确填写
- [ ] 选择了合适的许可协议（推荐CC BY）
- [ ] 所有图片已包含在提交包中
- [ ] LaTeX文件编译无错误
- [ ] 预览PDF显示正常
- [ ] 确认了解期刊的预印本政策

---

## 📚 九、参考链接

- arXiv主页: https://arxiv.org/
- 投稿帮助: https://arxiv.org/help/submit
- 用户手册: https://arxiv.org/help/
- 类别说明: https://arxiv.org/category_taxonomy
- 许可协议: https://arxiv.org/help/license

---

**准备好后，访问 https://arxiv.org/submit 开始上传！**
