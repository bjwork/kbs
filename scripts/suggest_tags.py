#!/usr/bin/env python3
"""标签自动推荐：jieba 分词 + 已有标签关键词匹配。

从正文提取关键词，和已有标签做双向匹配（标签是关键词的子串，或关键词是标签的子串），
返回最相关的若干标签。纯本地、无 LLM、不创造新标签（只从已有体系里挑）。

用法：
    from suggest_tags import suggest
    suggest("正文文本", existing_tags=["index", "lock", ...], top_k=5)
"""
import re

import jieba.analyse

# 英文标签 → 中文/英文关键词的映射，用于中文正文匹配英文标签
TAG_KEYWORDS = {
    "index": ["索引", "B+树", "B树", "回表", "覆盖索引", "最左前缀", "index"],
    "lock": ["锁", "行锁", "表锁", "死锁", "间隙锁", "next-key", "lock"],
    "transaction": ["事务", "MVCC", "隔离级别", "一致性视图", "回滚", "transaction"],
    "performance": ["性能", "慢查询", "优化", "filesort", "抖动", "performance"],
    "architecture": ["架构", "连接器", "优化器", "执行器", "redo", "binlog", "architecture"],
    "ha": ["高可用", "主备", "主从", "读写分离", "GTID", "切换", "ha"],
    "ops": ["运维", "误删", "kill", "grant", "flush", "ops"],
    "optimizer": ["优化器", "统计信息", "采样", "cardinality", "执行计划", "optimizer"],
    "security": ["安全", "权限", "注入", "security"],
    "knowledge-base": ["知识库", "笔记", "标签", "关联", "knowledge-base"],
    "llm": ["LLM", "大模型", "Claude", "GPT", "prompt", "llm"],
    "workflow": ["工作流", "流程", "workflow"],
    "learning": ["学习", "认知", "方法", "learning"],
    "cooking": ["红烧肉", "烹饪", "食谱", "cooking"],
    "rag": ["RAG", "向量", "检索增强", "rag"],
    "reading": ["阅读", "书", "专栏", "教程", "课程", "reading"],
}

# 英文标签 → 中文展示名（前端显示用，后端存英文不变）
TAG_ZH = {
    "index": "索引", "lock": "锁", "transaction": "事务", "performance": "性能",
    "architecture": "架构", "ha": "高可用", "ops": "运维", "optimizer": "优化器",
    "security": "安全", "knowledge-base": "知识库", "llm": "大模型", "workflow": "工作流",
    "learning": "学习", "cooking": "美食", "rag": "检索增强", "reading": "阅读",
}


def suggest(text: str, existing_tags: list, top_k: int = 5) -> list:
    """从 existing_tags 里挑出和 text 最相关的标签，按相关度排序。"""
    if not text.strip():
        return []
    # jieba TF-IDF 提关键词（比全文本匹配准）
    keywords = set(jieba.analyse.extract_tags(text, topK=30))
    text_lower = text.lower()

    scored = []
    for tag in existing_tags:
        score = 0
        kws = TAG_KEYWORDS.get(tag, [tag])
        for kw in kws:
            kw_lower = kw.lower()
            # 关键词出现在 jieba 提取的关键词里：+2；出现在原文里：+1
            if any(kw_lower in k.lower() or k.lower() in kw_lower for k in keywords):
                score += 2
            elif kw_lower in text_lower:
                score += 1
        if score > 0:
            scored.append((score, tag))
    scored.sort(key=lambda x: -x[0])
    return [tag for _, tag in scored[:top_k]]


def suggest_category(text: str, tags: list) -> str:
    """根据推荐标签猜分类。标签→分类的映射是经验规则。"""
    tag_set = set(tags)
    if tag_set & {"index", "lock", "transaction", "performance", "architecture", "ha", "ops", "optimizer", "security"}:
        return "tech"
    if tag_set & {"knowledge-base", "llm", "workflow", "rag"}:
        return "ai-practice"
    if tag_set & {"reading"}:
        return "reading"
    if tag_set & {"cooking"}:
        return "misc"
    return "misc"


if __name__ == "__main__":
    # 自测
    sample = "丁奇第 4 讲。InnoDB 用 B+ 树做索引：叶子节点存数据。二级索引叶子存主键值，查二级索引要回表。"
    tags = ["index", "lock", "transaction", "reading", "performance"]
    print("推荐标签：", suggest(sample, tags))
    print("推荐分类：", suggest_category(sample, suggest(sample, tags)))
