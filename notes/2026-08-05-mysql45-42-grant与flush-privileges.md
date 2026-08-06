---
title: grant 后要 flush privileges 吗：权限的内存与磁盘
date: 2026-08-05
category: tech
tags: [security, reading]
status: raw
---

丁奇第 42 讲。**规范使用 grant/revoke 不需要 flush privileges**——grant 同时改磁盘（mysql.user 等系统表）和内存（权限缓存），判断权限看内存。flush privileges 的作用是用磁盘数据**重建**内存权限，只在「内存和磁盘不一致」时才需要——而不一致的根源是有人**直接用 DML 语句（insert/update user 表）改权限**，跳过了内存更新。结论：别用 DML 改系统表，grant 就够了，flush 是补救措施不是常规操作。

**对我的价值**：「flush privileges 神话」是运维圈流传最广的以讹传讹之一，根源是早期文档没讲清内存/磁盘两层结构。这篇的价值在于把「为什么」讲透了——**权限判断只信内存**，所以 flush 不是「让权限生效」，是「强制内存跟磁盘同步」。类比 Java 的 volatile 或 CPU 缓存一致性，同一个分层一致性问题的不同表现。

**立场**：这条经验我直接拿来教育团队：**凡是需要「补救命令」才能生效的操作，第一反应应该是怀疑自己的操作姿势错了，而不是怪系统**。grant 如此，很多框架的「refresh」「reload」也如此。规范操作覆盖 99% 场景，补救命令是给那 1% 的异常留的后路，别把后路当正门走。
