# Markdown-to-PPTX Converter — 项目总结

## 项目概述

构建了一个可重用的 Python 工具，将带 YAML 元数据的 Markdown 文件自动转换为专业 PPTX 演示文稿。以 Boeing 品牌为参考，支持公司模板自定义（Logo、配色、字体），适用于项目汇报、立项材料、技术培训等场景。

**环境:** Python 3.10.12, python-pptx 1.0.2, PyYAML, Pillow

---

## 文件结构

```
pptx/
├── md2pptx.sh                  # 团队入口脚本（可执行，从任意目录调用）
├── md2pptx/                    # 转换库（单层目录）
│   ├── convert.py              # CLI 实现（单文件 + 批量）
│   ├── models.py               # 数据模型
│   ├── parser.py               # YAML + Markdown 解析器
│   ├── theme.py                # 主题管理器
│   ├── image_processor.py      # 图片处理
│   ├── slide_builder.py        # 布局检测
│   ├── presentation.py         # PPTX 生成器
│   ├── template.md             # Markdown 模板示例
│   └── requirements.txt
├── ex/                         # 测试数据
│   ├── microsoft.md
│   ├── mercedes-benz.md
│   └── assets/                 # md 同级 assets 目录
├── assets/                     # Boeing 品牌素材（示例）
├── PLAN.md
└── SUMMARY.md                  # 本文件
```

---

## 核心架构

```
Markdown 文件
    │
    ▼
┌──────────┐    ┌──────────┐
│  parser  │───▶│  theme   │
│ YAML+MD  │    │ 配色/字体 │
└────┬─────┘    └────┬─────┘
     │               │
     ▼               ▼
┌──────────────┐
│slide_builder │  布局检测
│ 1/2/3/4列   │  图文混排
└──────┬───────┘
       │
       ▼
┌──────────────┐  ┌──────────────┐
│ presentation │◀─│image_processor│
│  PPTX 生成   │  │ 透明度/缩放   │
└──────┬───────┘  └──────────────┘
       │
       ▼
    .pptx 文件
```

---

## 数据流

1. **parser.py** — 提取 YAML 前端 → `MetaInfo`，状态机解析 Markdown → `Section[]` + `Block[]`
2. **theme.py** — 从 MetaInfo 加载配色/字体/Logo，Boeing 风格默认值
3. **slide_builder.py** — `##` → 幻灯片，`###` → 列，连续 `-` → 列表组
4. **image_processor.py** — 解析 `{transparency,size}` 属性，Pillow LUT 快速透明度处理
5. **presentation.py** — python-pptx 渲染：首页、内容页（多列/图文/代码）、尾页

---

## 支持的 Markdown 特性

| Markdown 元素 | PPTX 映射 |
|--------------|----------|
| YAML frontmatter `---...---` | 文档元数据（标题/公司/作者/日期/字体/颜色） |
| `# 标题` | 首页主标题 |
| `## 章节` | 幻灯片标题 |
| `### 小节` | 列标题（数量决定列数 1-4） |
| `- 列表项` | 连续项目符号组（单文本框多段落） |
| `**粗体**` | 加粗文字 |
| `![alt](path){attrs}` | 图片（支持 transparency/size 属性） |
| `![First](path)` | 首页背景图 |
| `![last](path)` | 尾页背景图 |
| ` ```lang ` 代码块 | 代码块（等宽字体 + 灰底） |
| ` ```mermaid ` | Mermaid 占位框 |

---

## 图片扩展语法

```
![alt文本](图片路径){transparency:50,size:800*600,}
```

| 属性 | 说明 |
|------|------|
| `transparency` | 透明度 0-100（0=不透明，100=全透明），含拼写纠错 |
| `size` | 宽*高（像素），72 DPI 转换为英寸；单维度保持宽高比 |

---

## YAML 推荐格式

```yaml
---
Company:
  name: BOEING
  logo: ./assets/boeing-logo.png
Document:
  Title: 文档标题
  Font:
    48: "#880000"    # 文档标题色
    36: "#005566"    # section 标题色
    24: "#000088"    # subsection/列标题色
    16: "#660088"    # 正文色
  FontColor: "#333333"
  docCode: DOC0000001
  docRev: 1.0
  First Made Date: 6/1/2025
  First Made By (Author): 作者名
output: pptx
---
```

**注意:** 颜色值必须用引号包裹（`"#880000"`），否则 YAML 把 `#` 当注释。

---

## CLI 用法

```bash
# === 团队使用（推荐） ===
# 将工具目录加入 PATH 或直接调用入口脚本

# 单文件 — 输出到当前目录
./md2pptx.sh /path/to/report.md                    # → ./report.pptx

# 指定输出路径
./md2pptx.sh /path/to/report.md -o /path/to/out.pptx

# 批量处理目录
./md2pptx.sh /path/to/docs/ -o ./output/

# 递归批量
./md2pptx.sh /path/to/docs/ -o ./output/ -r

# 无页眉页脚
./md2pptx.sh report.md --no-header --no-footer

# === 直接调用 Python ===
python md2pptx/convert.py /path/to/report.md
```

**关键约定:**
- 输出默认保存到**当前工作目录**（`pwd`）
- 图片路径相对于 **Markdown 文件所在目录** 解析
- 推荐 assets 与 md 文件放在同一目录下：`报告.md` + `assets/图片.jpg`

---

## 已完成的修复记录

| 轮次 | 修复内容 |
|------|---------|
| 1 | 初始实现：models/parser/theme/image_processor/slide_builder/presentation/convert |
| 2 | 连续 bullet lists 合并为单文本框；YAML 缩进规范化 + hex color 自动加 `#`；图片 size 应用于 shape 尺寸；图片 transparency LUT 优化 |
| 3 | 首页背景传递 transparency/size；column 间距增大（0.4→0.45" heading, 0.45→0.55" gap）；bullet 行高估算（0.28→0.33"） |
| 4 | 裸 `#` 行不再生成文字 `#`；首页 author/date/company 间距修正（0.45→0.55" y_offset） |

---

## 后续优化方向

### 高优先级
- [ ] **Mermaid 图表渲染** — 集成 mmdc 或 Kroki API 将 mermaid 转为图片
- [ ] **文本自动换行** — 使用 `tf.auto_size` 或动态计算文本高度，消除长文本截断
- [ ] **Slide 内容溢出** — 当内容超出 slide 高度时自动分页
- [ ] **嵌套列表缩进** — 在 bullet group 内通过 `p.level` 实现多级缩进视觉

### 中优先级
- [ ] **表格支持** — Markdown table → PPTX 原生表格
- [ ] **多模板/主题系统** — 支持 JSON/YAML 模板文件切换不同企业风格
- [ ] **图片布局增强** — 支持更多位置控制（left/right/center/fill）
- [ ] **图表支持** — 数据驱动的柱状图/饼图/折线图
- [ ] **动画/过渡** — 支持配置幻灯片切换和元素动画

### 低优先级
- [ ] **PPTX 模板** — 基于现有 .pptx 模板文件生成（slide layouts）
- [ ] **Markdown 内联样式** — 支持 `<span style="...">` 局部样式
- [ ] **脚注/引用** — Markdown 脚注 → 幻灯片注释
- [ ] **导出 PDF** — 集成 LibreOffice 或直接生成 PDF
- [ ] **Web UI** — Flask/FastAPI 界面上传 Markdown 下载 PPTX

### 技术债务
- [ ] **单元测试** — pytest 覆盖 parser/slide_builder/presentation 核心逻辑
- [ ] **类型注解** — 全面添加 typing 注解
- [ ] **日志系统** — 用 logging 替代 print
- [ ] **配置文件** — 支持 .md2pptx.yaml 项目级配置
- [ ] **错误恢复** — 单个 slide 失败不影响整体生成

---

## Git 历史

```
dc5c3d3 Fix bare # title, title slide spacing, column overlap detection
b8edad7 Fix title bg transparency, column spacing, bullet height estimation
1b70fa2 Fix bullet groups, YAML parsing, image attributes + add ex/ test data
56d8820 Add markdown-to-PPTX converter implementation
0ee2471 Initial commit: Markdown-to-PPTX converter project
```
