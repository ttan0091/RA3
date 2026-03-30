---
name: docx-py
description: "使用 python-docx 库快速创建 Word 文档的专业技能。支持创建空文档、添加文本内容、从文件导入内容等场景。用于处理 Word 文档创建任务，提供简洁的命令行解决方案。"
license: MIT
---

# Python-Docx 快速创建 Word

## 概述

这是一个专业的 Word 文档创建技能，使用 python-docx 库提供快速、简洁的 Word 文档创建解决方案。适用于需要批量创建 Word 文档、自动化文档生成等场景。

## 前置条件

确保已安装 python-docx 依赖库：

```bash
pip install python-docx
```

## 快速创建 Word

### 场景 1：创建空的 Word 文件

直接生成无任何内容的 .docx 文件：

```bash
python -c "from docx import Document; Document().save('empty.docx')"
```

### 场景 2：创建带文字内容的 Word

生成后直接包含指定文字：

```bash
python -c "from docx import Document; doc=Document(); doc.add_paragraph('这是Python单行命令创建的Word内容'); doc.save('content.docx')"
```

### 场景 3：从文件内容创建 Word

将文本文件内容写入 Word：

```python
from docx import Document
import pathlib

doc = Document()
content = pathlib.Path('input.txt').read_text(encoding='utf-8')
doc.add_paragraph(content)
doc.save('output.docx')
```

### 场景 4：创建格式化 Word 文档

```python
from docx import Document
from docx.shared import Pt, Inches

doc = Document()

# 添加标题
doc.add_heading('文档标题', level=1)

# 添加段落
doc.add_paragraph('这是一个段落。')

# 添加带格式的段落
paragraph = doc.add_paragraph('带格式的文本：')
run = paragraph.add_run('粗体文本')
run.bold = True
run = paragraph.add_run(' 和 ')
run = paragraph.add_run('斜体文本')
run.italic = True

# 添加表格
table = doc.add_table(rows=3, cols=3)
for i in range(3):
    for j in range(3):
        table.cell(i, j).text = f'单元格 {i+1}-{j+1}'

doc.save('formatted.docx')
```

## 关键参数说明

- `Document()`：创建一个空的 Word 文档对象
- `add_paragraph('文字内容')`：添加段落内容
- `add_heading('标题文本', level=1)`：添加标题，level=1-8
- `add_table(rows, cols)`：添加表格
- `save('文件名.docx')`：保存文档为 .docx 格式
- 仅支持 .docx 格式，不支持旧版 .doc 格式

## 使用场景

### 1. 批量文档生成
```bash
# 批量创建多个空文档
for i in {1..5}; do
    python -c "from docx import Document; Document().save('doc${i}.docx')"
done
```

### 2. 报告生成
```python
from docx import Document
from datetime import datetime

doc = Document()
doc.add_heading('月度报告', 0)
doc.add_paragraph(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
doc.add_paragraph('本月工作总结：...')
doc.save('月度报告.docx')
```

### 3. 模板填充
```python
from docx import Document
import json

# 从 JSON 数据填充文档
data = {
    'title': '项目进度报告',
    'date': '2024-01-01',
    'content': '项目进展顺利...'
}

doc = Document()
doc.add_heading(data['title'], 0)
doc.add_paragraph(f'日期：{data["date"]}')
doc.add_paragraph(data['content'])
doc.save('报告.docx')
```

## 最佳实践

### 性能优化
- 对于大量文档创建，建议使用函数封装重复逻辑
- 使用上下文管理器确保文件正确关闭
- 考虑文档缓存机制提高重复创建效率

### 错误处理
```python
from docx import Document
import os

try:
    if os.path.exists('output.docx'):
        os.remove('output.docx')
    
    doc = Document()
    doc.add_paragraph('内容')
    doc.save('output.docx')
    print('文档创建成功')
except Exception as e:
    print(f'文档创建失败：{e}')
```

### 代码结构优化
```python
class WordDocumentCreator:
    def __init__(self):
        self.doc = Document()
    
    def add_heading(self, text, level=1):
        self.doc.add_heading(text, level)
    
    def add_paragraph(self, text, bold=False, italic=False):
        p = self.doc.add_paragraph(text)
        if bold:
            p.runs[0].bold = True
        if italic:
            p.runs[0].italic = True
    
    def save(self, filename):
        self.doc.save(filename)

# 使用示例
creator = WordDocumentCreator()
creator.add_heading('测试文档')
creator.add_paragraph('这是一个测试段落', bold=True)
creator.save('test.docx')
```

## 总结

- **核心逻辑**：`Document()` → `add_paragraph()` → `save()` 三步完成 Word 创建
- **命令行执行**：使用 `python -c "包裹代码"` 进行单行命令执行
- **必装依赖**：`python-docx` 是必需的核心库
- **适用场景**：适合需要快速创建、批量生成 Word 文档的场景
- **扩展性**：支持复杂的文档格式设置，可根据需求扩展功能

## 注意事项

1. 确保 python-docx 库已正确安装
2. Word 文档版本：仅支持 .docx 格式
3. 编码问题：建议使用 UTF-8 编码
4. 文件路径：确保输出路径有写入权限
5. 依赖版本：推荐使用 python-docx 0.8.11+ 版本