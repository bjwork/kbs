---
title: 日志系统：redo log 与 binlog 的两阶段提交
date: 2026-08-05
category: tech
tags: [architecture, reading]
status: raw
---

丁奇第 2 讲。更新语句比查询多两个日志模块：redo log（InnoDB 特有、物理日志、循环写，保证 crash-safe）和 binlog（Server 层、逻辑日志、追加写，用于归档和主从复制）。WAL = 先写日志再写磁盘。两阶段提交（redo prepare → 写 binlog → redo commit）是为了让两份日志的提交状态逻辑一致——否则崩溃恢复后，主库和用 binlog 搭出来的备库会数据不一致。

**对我的价值**：两个「双 1」参数（innodb_flush_log_at_trx_commit=1、sync_binlog=1）是数据不丢的前提，这个我在搭建生产库时直接照抄。更深一层是**为什么有两份日志**：MyISAM 没有 crash-safe，InnoDB 是插件引入自带 redo log——历史包袱造就了双日志架构，两阶段提交是给这个包袱打的补丁。理解了这个，就明白为什么 PolarDB/Aurora 这类重做的存储能砍掉一套。

**立场**：粉板/账本的比喻讲 WAL 很妙，但两阶段提交的反证法部分值得每个后端背下来——「先写 A 日志崩了会怎样、先写 B 日志崩了会怎样」，这是所有跨系统一致性问题的通用思考框架，不止 MySQL。我做分布式事务方案评审时就拿这套反证问候选人。
