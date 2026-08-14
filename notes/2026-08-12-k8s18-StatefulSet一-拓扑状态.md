---
title: StatefulSet 一：靠 Headless Service+Pod 编号固定拓扑状态
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, statefulset, reading]
status: raw
url: /k8s_lesson_html/18_深入理解StatefulSet一_拓扑状态.html
related:
  - 2026-08-12-k8s19-StatefulSet二-存储状态.md
---

Deployment 假设所有 Pod 完全对等，但分布式应用有主从、主备，实例间不对等——这就是「有状态应用」。StatefulSet 把状态抽象成两类：拓扑状态（启动顺序、网络标识）和存储状态（绑定的数据）。拓扑状态靠两件事固定：一是给 Pod 按序编号（web-0、web-1），严格按序创建删除；二是配 Headless Service（clusterIP: None），不分配 VIP，而是给每个 Pod 一条 DNS 记录 `<pod-name>.<svc-name>`，Pod 删了重建名字和 DNS 都不变。

**我的判断**：StatefulSet 解决有状态应用的核心是「固定网络标识+独立存储」，这一篇先把网络标识讲透了。我部署过 Redis 主从和 ETCD，深知有状态服务上 K8s 难在哪——传统运维里主从靠配置文件写死 IP，迁到容器后 IP 每次重建都变，主从关系就乱了。Headless Service+Pod 编号这套机制让「mysql-0.mysql 永远是主」这件事成立，应用代码不用改就能用 DNS 寻址。但要注意一个反直觉点：DNS 记录不变，解析出的 IP 是会变的，所以有状态应用必须用 DNS 或 hostname 访问，不能写死 IP。StatefulSet 本质是 Deployment 的改良——给 Pod 加了编号，但正是这个编号让主从、主备这类拓扑能在 K8s 里表达。
