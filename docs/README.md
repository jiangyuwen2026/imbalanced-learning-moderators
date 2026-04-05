# Pattern Recognition 投稿材料包

## 📦 文件夹内容

此文件夹包含投稿至 **Pattern Recognition** 期刊（IF: 7.6, Q1）的所有必要材料。

---

## 🚀 快速开始

### 1️⃣ 阅读检查清单
👉 **首先阅读**: `00_SUBMISSION_CHECKLIST.md`  
这是投稿的完整指南，包含详细步骤。

### 2️⃣ 准备主文件
主要投稿文件：
- `Manuscript_PR.tex` - LaTeX源文件（推荐）
- `Manuscript_PR_SingleColumn.docx` - Word版本（备用）

**建议使用LaTeX版本**，编译为PDF后提交。

### 3️⃣ 收集辅助文件
必须上传的文件：
- ✅ `highlights.txt` - 文章亮点
- ✅ `declarations.docx` - 声明文件
- ✅ `title_page.docx` - 标题页
- ✅ `cover_letter_PR.docx` - 投稿信

### 4️⃣ 准备图表
**需要您补充**（从原论文导出）：
- Figure_1.pdf/png - 理论框架图
- Figure_2.pdf/png - 算法流程图
- Figure_3.pdf/png - 实验结果图

**图表要求**:
- 格式: TIFF, EPS, PDF, 或 PNG
- 分辨率: 最低300 dpi（照片），1000 dpi（线图）
- 尺寸: 单栏最小1063像素宽

---

## 📄 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `Manuscript_PR.tex` | 论文主文件（LaTeX，单栏双倍行距） |
| `Manuscript_PR_SingleColumn.docx` | Word版本（备用） |
| `PR_format_preamble.tex` | LaTeX格式设置参考 |

### 投稿辅助文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `highlights.txt` | 5条要点，每条≤85字符 | ✅ 就绪 |
| `declarations.docx` | 利益冲突+CRediT+数据声明 | ✅ 就绪 |
| `title_page.docx` | 完整作者信息 | ✅ 就绪 |
| `cover_letter_PR.docx` | PR期刊定制投稿信 | ✅ 就绪 |

### 文档和报告

| 文件 | 说明 |
|------|------|
| `00_SUBMISSION_CHECKLIST.md` | 投稿检查清单和步骤 |
| `PR_SUBMISSION_EXECUTION_REPORT.md` | 执行报告（详细修改记录） |
| `README.md` | 本文件 |

---

## 📊 论文统计

```
标题: Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection

统计信息:
├── 总词数: ~7,800 words
├── 参考文献: 46条 (要求35-55) ✅
├── PR期刊引用: 6篇 (要求≥5) ✅
├── 页数估算: ~28页 (要求20-35) ✅
├── 图表: 3图5表
└── Highlights: 5条 (符合要求) ✅
```

---

## ⚡ 快速提交指南

### 步骤1: 编译论文
```bash
# 使用LaTeX编译
pdflatex Manuscript_PR.tex
bibtex Manuscript_PR
pdflatex Manuscript_PR.tex
pdflatex Manuscript_PR.tex

# 生成: Manuscript_PR.pdf
```

### 步骤2: 访问投稿系统
```
https://www.editorialmanager.com/pr/default.aspx
```

### 步骤3: 填写信息
- **Article Type**: Research Paper
- **Title**: Beyond Imbalance Ratio: Data Characteristics as Critical Moderators of Oversampling Method Selection
- **Abstract**: 从Manuscript_PR.tex复制
- **Keywords**: class imbalance, oversampling method selection, imbalance ratio, data characteristics, class separability

### 步骤4: 上传文件
按系统提示顺序上传：
1. Manuscript (PDF)
2. Highlights
3. Title Page
4. Figures (1-3)
5. Declarations
6. Cover Letter

### 步骤5: 推荐审稿人
建议推荐（详细信息见Cover Letter）：
1. Dr. Bartosz Krawczyk (NJIT)
2. Dr. Mikel Galar (UPNA)
3. Dr. Alberto Fernandez (UGR)
4. Dr. Michał Koziarski (WUST)
5. Dr. Nitesh V. Chawla (Notre Dame)

---

## ✅ 提交前确认

- [ ] 所有作者同意投稿
- [ ] 论文格式符合要求（单栏双倍行距）
- [ ] 参考文献46条（含6篇PR期刊）
- [ ] Highlights 5条，每条≤85字符
- [ ] 所有图表分辨率≥300 dpi
- [ ] 数据可用性声明已添加
- [ ] 利益冲突声明已准备
- [ ] Cover Letter已润色
- [ ] 推荐审稿人已确定

---

## 📞 有用链接

| 资源 | 链接 |
|------|------|
| 投稿系统 | https://www.editorialmanager.com/pr/default.aspx |
| 作者指南 | https://www.sciencedirect.com/journal/pattern-recognition/publish/guide-for-authors |
| 期刊主页 | https://www.sciencedirect.com/journal/pattern-recognition |

---

## 📅 时间线预期

| 阶段 | 时间 |
|------|------|
| 初审决定 | ~18天 |
| 审稿后决定 | ~110天 |
| 接受到在线发表 | ~5天 |

---

## 🎯 期刊信息

```
期刊: Pattern Recognition
出版商: Elsevier
影响因子: 7.6 (2024)
JCR分区: Q1 (计算机科学AI)
CiteScore: 15.0
审稿类型: 单匿名评审
```

---

**准备就绪！祝您投稿顺利！** 🚀

---

*材料包生成时间: 2025年4月*
