# Overleaf 上传指南 - 解决图片找不到问题

## 问题
错误信息：
```
Package pdftex.def Error: File `figure3_moderation_effects.png' not found
```

这意味着Overleaf无法找到图片文件。

---

## ✅ 解决方案（推荐）

### 方法1：直接上传ZIP文件（最简单）

1. **下载准备好的ZIP文件**：
   ```
   PR_Paper_For_Overleaf.zip
   ```

2. **在Overleaf中**：
   - 点击 **"New Project"**（新建项目）
   - 选择 **"Upload Project"**（上传项目）
   - 选择 `PR_Paper_For_Overleaf.zip` 文件
   - 点击 **"Open"**

3. **等待上传完成**，然后点击 **"Recompile"**

---

### 方法2：手动上传文件

1. **在Overleaf中创建新项目**：
   - 点击 **"New Project"** → **"Blank Project"**
   - 输入项目名称，点击 **"Create"**

2. **上传主文件**：
   - 点击左侧 **"Upload"** 按钮
   - 选择 `Manuscript_PR_Ready.tex`

3. **上传图片文件**（必须逐个上传）：
   - 再次点击 **"Upload"**
   - 选择 `figure3_moderation_effects.png`
   - 再次点击 **"Upload"**
   - 选择 `supplementary_E2_sampling_distribution.png`

4. **确认文件结构**：
   ```
   项目根目录/
   ├── Manuscript_PR_Ready.tex
   ├── figure3_moderation_effects.png
   └── supplementary_E2_sampling_distribution.png
   ```

5. 点击 **"Recompile"**

---

## ⚠️ 常见错误及解决

### 错误1：文件名不匹配
**症状**：`File 'figure3_moderation_effects.png' not found`

**检查**：
- 文件名必须完全匹配（包括大小写）
- 确认没有多余的空格
- 确认扩展名是 `.png` 不是 `.PNG` 或 `.jpg`

### 错误2：图片在子文件夹
**症状**：图片找不到

**解决**：确保所有文件都在项目**根目录**，不是在子文件夹中。

### 错误3：文件未正确上传
**症状**：左侧文件列表中没有图片文件

**解决**：重新上传图片文件，检查文件大小是否正确（不是0KB）。

---

## ✅ 验证步骤

上传完成后，在Overleaf左侧文件列表中应该看到：

```
☰
📄 Manuscript_PR_Ready.tex
🖼️ figure3_moderation_effects.png
🖼️ supplementary_E2_sampling_distribution.png
```

然后点击 **"Recompile"**，图片应该正常显示。

---

## 📦 文件位置

所有需要的文件都在：
```
/Users/jiangyuwen/Research/不均衡样本/IJSmartGrid_Submission/PR_Submission_Materials/
```

包含：
- `Manuscript_PR_Ready.tex` (69 KB) - 主文件
- `figure3_moderation_effects.png` (414 KB) - 图3
- `supplementary_E2_sampling_distribution.png` (834 KB) - 图4
- `PR_Paper_For_Overleaf.zip` (1.1 MB) - 打包好的上传文件

---

## 🆘 如果仍然报错

1. 清除Overleaf缓存：
   - 点击菜单 **"Logs and output files"**
   - 点击 **"Clear cached files"**
   - 重新编译

2. 检查图片文件是否损坏：
   - 下载图片到本地查看能否正常打开

3. 尝试重命名文件：
   - 将图片重命名为简单的名字（如 `fig3.png`）
   - 同时修改LaTeX中的引用

---

## 📞 需要帮助？

如果以上方法都无法解决问题，请检查：
1. 网络连接是否正常
2. Overleaf账户是否有足够空间
3. 浏览器是否支持文件上传
