# fuxi KBS

一个给个人使用的 AI Native 本地知识库。资料以 Markdown 文件为数据本体，AI 负责摘要、判断、标签和关联；本地网页负责检索、阅读、编辑与上传。

它不依赖 Obsidian，也不需要数据库保存原始笔记。Obsidian 可以作为可选的 Markdown 阅读器使用。

## 当前能力

- PC 三栏工作台和移动端独立页面
- 中文全文检索、分类/标签筛选和分页
- 笔记新建、编辑、删除与关联跳转
- Markdown 实时预览
- 本地文件上传与文本提取
- AI 驱动的摘要、标签、关联和索引工作流
- MySQL、Kubernetes、软件架构三个专栏的笔记与 HTML 原文跳转

当前没有实现粘贴 URL 后自动抓取正文；链接可以先记录到笔记，抓取流程由 Claude Code 或 Codex 按 `CLAUDE.md` 执行。

## 数据规模

当前仓库包含：

- 178 篇加工后的知识笔记
- 175 篇 Markdown 原料
- MySQL 45 讲：45 篇 HTML 原文
- 深入剖析 Kubernetes：57 篇 HTML 原文
- 从 0 开始学架构：73 篇 HTML 原文

## 目录结构

```text
.
├── notes/                 # 带摘要、立场、标签和关联的知识笔记
├── raw/                   # 供 AI 读取的 Markdown 原料
├── mysql45lesson_html/    # MySQL 45 讲 HTML 原文
├── k8s_lesson_html/       # Kubernetes 专栏 HTML 原文
├── pr_lesson_html/        # 软件架构专栏 HTML 原文
├── wiki/                  # 主题页、实体页（预留）
├── briefs/                # 选题清单（预留）
├── scripts/               # 索引、关联打分、转换和标签脚本
├── server/                # FastAPI 服务与 SQLite FTS5 索引
├── web/                   # PC/移动网页和本地前端依赖
├── INDEX.md               # 自动生成的 Markdown 总索引
├── CLAUDE.md              # AI 入库和问答工作流
└── ROADMAP.md             # 当前进度与后续计划
```

## 本地运行

需要 Python 3.9 或更高版本。

```bash
python3 -m pip install fastapi uvicorn python-multipart jieba
python3 server/main.py
```

浏览器访问：

```text
http://127.0.0.1:8000
```

同一局域网内可使用电脑 IP 从手机访问，服务会根据浏览器自动切换移动页面。

可选的文件转换依赖：

- PDF 上传需要 `pdftotext`；macOS 可通过 `brew install poppler` 安装。
- DOCX 转换使用 macOS 自带的 `textutil`。

## 知识库工作流

向 Claude Code 或 Codex 提供链接、想法或本地文件后，AI 按 `CLAUDE.md` 完成：

1. 保留原料或原文链接。
2. 生成带个人判断的原子笔记。
3. 从标签体系中选择标签。
4. 计算笔记关联并双向写入 `related`。
5. 重建 `INDEX.md`。

常用维护命令：

```bash
# 为一篇新笔记计算关联
python3 scripts/rel_score.py notes/<笔记文件名>.md

# 全量重算关联
python3 scripts/rel_score.py --all

# 重建 Markdown 索引
python3 scripts/build_index.py
```

## 数据原则

- `notes/*.md` 和 `raw/*.md` 是可读、可迁移、可 Git diff 的数据本体。
- `server/data/kbs.db` 只是可随时重建的全文检索索引，不提交到 Git。
- 专栏 HTML 原文集中保存在对应的 `*_lesson_html/` 目录，避免在 `raw/` 重复保存。
- `raw/` 中的 PDF、DOCX、HTML 等二进制或原始文件默认不提交，只保留转换后的 Markdown。
- `INDEX.md` 由脚本生成，不应手工编辑。

## 设计与进度

- 产品和架构设计：`AI-KB-产品设计文档.md`
- 当前实现进度：`ROADMAP.md`
- AI 操作规范：`CLAUDE.md`
