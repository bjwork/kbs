---
title: StatefulSet 三：MySQL 主从实践暴露有状态应用的「三座大山」
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, statefulset, reading]
status: raw
related_raw:
  - 2026-08-12-20_深入理解StatefulSet三_有状态应用实践.html
---

用 StatefulSet 部署 MySQL 主从集群，要翻「三座大山」：主从配置文件不同（ConfigMap+InitContainer 按 Pod 序号分发 master.cnf/slave.cnf）；备份文件传输（InitContainer 用 ncat 从上一个节点拉 XtraBackup 备份）；Slave 首次启动要执行 CHANGE MASTER TO 初始化 SQL（sidecar 容器等 MySQL ready 后注入）。三个坑里最反直觉的是「阅后即焚」——初始化文件用完必须改名删除，否则容器重启又跑一遍数据恢复。

**我的判断**：这一篇把「有状态服务上 K8s 难在哪」讲透了。MySQL 这种「原始」分布式项目（不像 ETCD 原生考虑分布式）上 K8s，要靠 ConfigMap、InitContainer、sidecar、PVC、Headless Service 拼出一套复杂协调逻辑，YAML 写得像在容器里硬造一个运维流程。我深有共鸣——Redis、MySQL 这类传统数据库上 K8s 的成本，往往比裸机部署还高，因为分布式协调逻辑（主从同步、故障切换、数据补齐）本应是应用自己的事，现在要靠容器编排重新表达一遍。张磊在结尾点出：StatefulSet 解决不了的应用（比如需要复杂故障恢复逻辑的），Operator 才是正解。Operator 本质就是把 DBA 的运维知识编码成控制器——这也是为什么后来 Prometheus、Redis Operator 这么火。对 AI 应用落地的启发：大模型推理服务（无状态）上 K8s 很顺，但训练任务（有状态、要保存 checkpoint）就得 Operator+PVC，直接套 Deployment 不行。
