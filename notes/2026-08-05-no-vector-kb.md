---
title: 个人知识库不需要向量库，标签加打分就够用
date: 2026-08-05
category: ai-practice
tags: [knowledge-base, rag, llm]
status: raw
related:
  - 2026-08-05-ai-tagging.md
---

向量库对个人知识库是大炮打蚊子。AI 打的标签本身就是语义压缩，两两比较标签重叠再加标题关键词重叠，土办法打分比向量召回更可解释，还能 git diff 追踪每次 ingest 改了哪些关联。十万篇以下规模没必要上 embedding 和 RAG 链路。
