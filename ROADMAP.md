# ROADMAP

## 当前阶段

**v1.5 离线服务版已完成**（2026-08-07）：PC 三栏 + 安卓移动端独立页面，双端检索/录入/上传/管理全通。继续 14 天自用验证（至 2026-08-19）。

验证标准（来自 `AI-KB-产品设计文档.md` 第八章）：
- 正向：主动想用、有推荐冲动、有「再加 XX 功能」冲动
- 负向：使用频率持续走低、觉得不如直接搜

## 已完成

### v1（Claude 驱动期）
- 目录结构：`raw/ notes/ wiki/ briefs/ scripts/`（wiki/briefs 预留，v2 启用）
- `CLAUDE.md` 知识库工作流章节
- `scripts/build_index.py` + `scripts/rel_score.py`：索引生成 + 关联打分
- MySQL 45 讲入库：45 篇 PDF + 45 篇带立场笔记，共 48 篇
- **李运华「从 0 开始学架构」入库（2026-08-07）**：73 篇 HTML 原文（raw/ 含同名 .md 转换版）+ 73 篇带立场笔记（pr00-pr72），覆盖 4R 定义、复杂度来源、架构流程、高性能/高可用/可扩展模式、异地多活、微服务、互联网架构模板、架构重构、特别放送与加餐
- **张磊「深入剖析 Kubernetes」入库（2026-08-12）**：57 篇 HTML 原文 + 57 篇带立场笔记（k8s00-k8s56），覆盖容器原理（Namespace/Cgroups/镜像分层）、K8s 本质、Pod/Deployment/StatefulSet/DaemonSet/Job、声明式 API + 控制器 + Operator、PV/PVC/CSI 存储、CNI/Service/Ingress 网络、调度器、CRI/容器运行时、监控日志、开源社区。新增 `scripts/html_to_md.py` 沉淀极客时间 slate editor HTML→md 转换（机械活归脚本），新增 `kubernetes`/`container` 等标签
- **标签中文备注持久化（2026-08-12）**：`TAG_ZH` 从硬编码改为 `scripts/tags_meta.json`（数据本体，可 git 跟踪），一次性补全 37 个无备注标签（库里 53 个标签全量有中文）；新增 `upsert_tag_zh()` 原子写回。前端录入新标签弹 prompt 填备注，`POST /api/notes` 自动持久化；Claude ingest 走 `upsert_tag_zh` 脚本同步备注（约定写入 CLAUDE.md）。双端（PC + 移动）addTag 均改造

### v1.5（离线服务版，2026-08-06 至 2026-08-07）
- **服务端 `server/`**（FastAPI + SQLite FTS5）：检索（全文 bm25 + 筛选 + 分页）、详情+related、笔记 CRUD（删除移 trash/）、多文件上传转换管线（pdf/docx/html/md/txt/代码文件）、raw 原文下载
- **前端 PC 端 `web/index.html`**：Vue3 三栏工作台（左导航/中列表/右阅读），markdown 渲染（marked+DOMPurify），编辑器实时预览
- **前端移动端 `web/mobile.html`**：独立页面，全 ES5 兼容语法（老内核浏览器可用），UA 识别自动分流，列表/详情/编辑单页切换
- **数据能力**：
  - raw/ 二进制与 git 脱钩（pdf/docx/html 不进 git）
  - rel_score 增量打分（倒排预筛，模拟 3000 篇单篇 21ms）
  - 笔记支持原文链接 url + 多原始文件 related_raw（向后兼容单值老数据）
  - 45 篇 mysql45 补挂原始 PDF
- **踩过的坑（已修）**：FTS5 trigram 中文检索失效（改 unicode61+插空格+短语查询）、SQLite 孤儿清理解包 bug、编辑器布局溢出、前端 CDN 安卓不可达（改本地 vendor/）、ES2020/ES2015 语法老内核白屏、UA 分流缓存

## 进行中

- 14 天自用验证：日常往库里丢链接和想法，观察使用频率（至 2026-08-19）

## 待办

- 真实抓取一次链接，端到端走一遍 CLAUDE.md 里的 ingest 流程（抓取管线代码化：粘贴 URL → 自动抓正文 → 预填编辑器）
- 真实 docx 文件（含表格/图片/多级标题）转换质量待验证
- **关联打分 TAG_DF_THRESHOLD=20 是绝对阈值**：库涨到几千篇时需要重校
- **手机离线缓存（二期）**：按「主题包 + 收藏 + 最近访问」缓存
- **PWA 完整化（二期）**：manifest.json + service worker（需 HTTPS）
- **jieba 标签推荐（二期）**：录入时从已有标签体系推荐候选
- v2 编译层：主题页/实体页（mysql45 系列是天然第一个编译对象）
- v2 选题流；v3 周报流、更多抓取渠道

## 阻塞

无。

## 最近验证

- 2026-08-12：标签中文备注持久化功能完成。`scripts/tags_meta.json` 全量 53 个标签有中文备注；`upsert_tag_zh()` 原子写回验证通过（POST /api/notes 带 tag_zh → json 落盘 → /api/tags 返回完整映射）。删除自测笔记后标签列表正确同步。双端编辑器 addTag 改造完成。
- 2026-08-12：K8s 专栏 57 篇全量入库完成。`scripts/html_to_md.py` 批量转 57 个 slate HTML→md，`rel_score.py --all` 全量重算 + `build_index.py` 重建索引（178 篇），笔记间建立起关联（k8s 系列内部调度器三连、网络四连、存储四连、CRI 二连等，k8s47 与 k8s06 跨篇章安全容器↔隔离）。
- 2026-08-07：架构专栏 73 篇全量入库完成。`rel_score.py --all` 全量重算 + `build_index.py` 重建索引（121 篇），笔记间建立起跨系列关联（pr 系列内部、pr 与 mysql45 之间）。
- 2026-08-07：移动端独立页面上线。X 浏览器/小米浏览器/夸克实测可用（全 ES5 语法修复老内核白屏）；UA 分流（桌面→三栏，移动→单页）。
- 2026-08-07：修复 SQLite 孤儿清理 bug（集合推导解包错误），删除笔记后索引正确同步。
- 2026-08-06：v1.5 一期端到端跑通——检索/新建/编辑/删除/上传全链路。
