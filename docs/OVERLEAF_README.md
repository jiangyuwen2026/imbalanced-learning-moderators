# Overleaf / 在线LaTeX编译器使用说明

## 问题
在线LaTeX编译器（如Overleaf）无法访问本地绝对路径，需要将图片文件与.tex文件一起上传。

---

## 解决方案

### 方法1：使用当前目录（推荐）

当前配置已设置为从当前目录查找图片：

```latex
\includegraphics[width=0.95\linewidth]{figure3_moderation_effects.png}
\includegraphics[width=0.95\linewidth]{supplementary_E2_sampling_distribution.png}
```

**步骤：**
1. 打开在线LaTeX编辑器（Overleaf等）
2. 上传以下文件到同一项目：
   - `Manuscript_PR_Ready.tex`
   - `figure3_moderation_effects.png`
   - `supplementary_E2_sampling_distribution.png`
3. 编译即可

---

### 方法2：创建Figures文件夹

**步骤：**
1. 在Overleaf中创建一个名为 `Figures` 的文件夹
2. 将两个图片文件上传到 `Figures` 文件夹
3. 取消注释以下行（删除行首的 `%`）：
   ```latex
   \graphicspath{{./Figures/}}
   ```
4. 编译

---

## 文件清单

需要上传的文件：

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `Manuscript_PR_Ready.tex` | LaTeX源文件 | 主文件 |
| `figure3_moderation_effects.png` | PNG图片 | 图3：调节效应 |
| `supplementary_E2_sampling_distribution.png` | PNG图片 | 图4：边界可视化 |

---

## 图片文件位置

图片原始位置：
```
/Users/jiangyuwen/Research/不均衡样本/Paper/Figures/
├── figure3_moderation_effects.png
└── supplementary_E2_sampling_distribution.png
```

已复制到：
```
PR_Submission_Materials/
├── Manuscript_PR_Ready.tex
├── figure3_moderation_effects.png          ✅ 已复制
└── supplementary_E2_sampling_distribution.png ✅ 已复制
```

---

## 编译步骤

1. 打开 [Overleaf](https://www.overleaf.com/)
2. 创建新项目 → 上传项目
3. 选择以下文件一起上传：
   - `Manuscript_PR_Ready.tex`
   - `figure3_moderation_effects.png`
   - `supplementary_E2_sampling_distribution.png`
4. 点击 "Recompile"
5. 检查PDF中图片是否正确显示

---

## 故障排除

### 问题：图片仍然显示为黑框或文件名

**解决方案：**
1. 确认图片文件已正确上传（检查文件大小不为0）
2. 确认文件名完全匹配（包括大小写）
3. 尝试重新上传图片文件
4. 清除编译缓存后重新编译

### 问题：编译报错 "File not found"

**解决方案：**
1. 检查图片文件是否在项目根目录
2. 或创建 `Figures` 文件夹并启用 `\graphicspath{{./Figures/}}`

---

## 本地编译（Mac/Linux）

如果使用本地LaTeX环境：

```bash
cd /Users/jiangyuwen/Research/不均衡样本/IJSmartGrid_Submission/PR_Submission_Materials

# 编译
pdflatex Manuscript_PR_Ready.tex
pdflatex Manuscript_PR_Ready.tex
```

图片已从 `Paper/Figures/` 复制到当前目录，本地编译无需额外设置。
