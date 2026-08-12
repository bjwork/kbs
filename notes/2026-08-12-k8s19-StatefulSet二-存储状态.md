---
title: StatefulSet 二：PVC/PV 解耦存储细节，volumeClaimTemplate 绑定 Pod
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, statefulset, reading]
status: raw
related_raw:
  - 2026-08-12-19_深入理解StatefulSet二_存储状态.html
related:
  - 2026-08-12-k8s18-StatefulSet一-拓扑状态.md
---

存储状态靠 PVC/PV 机制解决。PVC 是开发者声明的「我要什么」（1Gi、ReadWriteOnce），PV 是运维准备好的「有什么」（Ceph RBD、NFS 等具体存储），K8s 自动匹配绑定。这本质是「接口与实现分离」——开发者不接触 Ceph 地址、密钥这些基础设施细节。StatefulSet 用 volumeClaimTemplates 给每个 Pod 生成同编号的 PVC（www-web-0、www-web-1），Pod 删除后 PVC 和 PV 保留，重建时按编号找回原 PV，数据不丢。

**我的判断**：PVC/PV 这层抽象是 K8s 把存储从「运维私域」拉进「开发可声明」的关键。我见过太多 Java 项目里 application.yml 写死 NFS 路径、甚至 Ceph monitor IP，运维改存储方案要改一堆配置文件推全量发布。PVC 把存储变成可声明、可迁移的 API 对象，这是正确的解耦方向。但我要点出有状态服务上 K8s 的真实难点：StatefulSet 只保证 Pod 重建后能找回原 PV，它不管应用层的数据恢复逻辑——MySQL 主从重建后怎么追同步位点、Redis 节点怎么加入集群，这些业务逻辑 StatefulSet 帮不了，得靠 InitContainer 或 Operator。所以「有状态应用上 K8s」的真正门槛不在 StatefulSet 本身，而在怎么把应用的分布式协调逻辑容器化。下一篇的 MySQL 实践会把这个问题暴露得很彻底。
