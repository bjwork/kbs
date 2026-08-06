---
title: order by 怎么工作：filesort 的两种算法与排序优化
date: 2026-08-05
category: tech
tags: [performance, optimizer, reading]
status: raw
related:
  - 2026-08-05-mysql45-35-join优化-BKA与临时表.md
  - 2026-08-05-mysql45-37-内部临时表与group-by.md
---

丁奇第 16 讲。无索引可用时 order by 走 filesort（不一定用磁盘文件！内存 sort_buffer 够就内存排）。两种算法：**全字段排序**（select 的列全放 sort_buffer，行太大则改用下面这种）；**rowid 排序**（只放排序字段+主键，排完再回表取整行，多一次随机读）。max_length_for_sort_data 决定走哪条。优化路径：联合索引直接按索引顺序取（免排序）→ 覆盖索引免回表 → 都不行才 filesort。city in ('杭州','苏州') order by name 这种**多值等值 + 排序**，联合索引 (city,name) 用不了排序有序性，得 UNION 拆开或应用层归并。

**对我的价值**：filesort 的「内存够就内存排」打破了我「filesort=磁盘排序=慢」的刻板印象——小结果集 filesort 根本不慢，真正要盯的是**排序字段让联合索引失序**的场景。思考题那个 city in 案例是经典陷阱：看起来 (city,name) 索引完美，实际上 in 展开成两个 city 后 name 全局无序，还是得 filesort。

**立场**：「看执行计划要看 Extra 里的 Using filesort / Using temporary」是 DBA 常识，但这篇的价值在于给了**filesort 内部的决策链**：buffer 大小 → 算法选择 → 是否回表。我给团队做慢查询培训时就用这条链：先问「能不能让索引直接给出有序结果」（最优），再问「能不能用覆盖索引让排序字段变轻」，最后才接受 filesort 并确认 sort_buffer 够。
