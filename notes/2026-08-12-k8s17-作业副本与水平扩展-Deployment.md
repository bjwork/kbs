---
title: Deployment 双层控制器：ReplicaSet 管副本，滚动更新+回滚降维打击
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, deployment, reading]
status: raw
url: /k8s_lesson_html/17_经典PaaS的记忆_作业副本与水平扩展.html
---

Deployment 的本质是个双层控制器：它不直接管 Pod，而是管 ReplicaSet；每个 ReplicaSet 对应一个应用版本，再由 ReplicaSet 管具体的 Pod 副本数。滚动更新的实现就是把新 ReplicaSet 扩上去、旧 ReplicaSet 缩下来，交替推进；回滚就是把旧 ReplicaSet 再扩回来。revisionHistoryLimit 控制留几个历史版本，pause/resume 让多次修改合并成一次滚动。

**我的判断**：滚动更新+一键回滚是 K8s 对传统部署的降维打击。做 Java 后端时，Spring Boot 发版要么停机重启、要么挂个 Nginx 手动切流，回滚等于重新打包发版，半夜出问题能折腾到天亮。Deployment 把「版本」变成 Etcd 里可枚举、可切换的对象，`kubectl rollout undo --to-revision=N` 一条命令回到任意历史版本，这才是「应用」该有的抽象。但有个前提必须强调：Health Check 配不对，滚动更新就是个坑——容器 Running 不等于服务 Ready，没配 readinessProbe，新 Pod 还没起好就把旧 Pod 杀了，流量直接 502。maxSurge/maxUnavailable 默认 25% 在生产偏激进，核心服务我会调成更保守的值。Deployment 假设所有 Pod 完全对等，会话黏连场景它就无能为力，得靠自定义控制器或 Service Mesh。
