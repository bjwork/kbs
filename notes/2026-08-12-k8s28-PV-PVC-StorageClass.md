---
title: PV/PVC/StorageClass 把存储拆成接口与实现，两阶段处理是落盘骨架
date: 2026-08-12
category: tech
tags: [kubernetes, storage, pv, pvc, reading]
status: raw
related_raw:
  - 2026-08-12-28_PV_PVC_StorageClass这些到底在说啥.html
related:
  - 2026-08-12-k8s29-本地持久化卷与PV-PVC.md
---

这篇是 K8s 存储体系总览。PV 描述具体存储实现（NFS 目录、云磁盘），PVC 描述 Pod 想要的存储属性（大小、读写权限），StorageClass 是 PV 模板+Provisioner，三者构成「接口与实现分离」的设计。PVC 和 PV 的绑定由 PersistentVolumeController 这个「红娘」控制循环撮合，绑定就是把 PV 名字填进 PVC 的 volumeName。真正的持久化靠「两阶段处理」：Attach（挂远程磁盘到宿主机，由 AttachDetachController 在 Master 执行）+ Mount（格式化并挂到 Volume 目录，由 kubelet 的 VolumeManagerReconciler 在节点执行）。Dynamic Provisioning 让 StorageClass 根据 PVC 自动创建 PV，省去人工建 PV。

我的判断：这套体系看似过度设计（直接在 Pod YAML 写 Volumes 不行吗），实则是为了可扩展性——存储插件可以无限扩展而不改 Pod/PVC 的用法。作为 Java 后端我类比成 JDBC：PVC 是接口，PV 是实现，StorageClass 是 DataSource 工厂。两阶段处理把耗时远程挂载从 kubelet 主循环解耦，避免拖慢 Pod 创建，这个设计思想和 Informer+workQueue 一脉相承。结合 MySQL/Redis 痛点理解：MySQL 的 data 目录必须用 PVC 挂持久卷，否则 Pod 重建数据就没了；Redis 的 RDB/AOF 同理。但 K8s 存储体系不依赖 docker volume，自己一套，比 docker volume 诞生还早，这说明 K8s 从一开始就把存储当作一等公民设计。
