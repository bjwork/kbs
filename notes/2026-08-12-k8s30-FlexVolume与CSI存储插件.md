---
title: FlexVolume 是脚本式存储插件，CSI 把存储插件标准化并 gRPC 化
date: 2026-08-12
category: tech
tags: [kubernetes, storage, csi, architecture, reading]
status: raw
url: /k8s_lesson_html/30_编写自己的存储插件_FlexVolume与CSI.html
related:
  - 2026-08-12-k8s31-CSI插件编写指南.md
---

这篇讲两种存储插件开发方式。FlexVolume 是旧方案——kubelet 在 Mount 阶段调用宿主机上 /usr/libexec/kubernetes/kubelet-plugins/volume/exec/<vendor>~<driver>/<driver> 这个可执行文件（可以是 shell 脚本），传入 mount 和 JSON 参数，脚本执行 mount -t nfs 并返回 {"status":"Success"}。简单但局限大：每次调用独立进程无法保存状态、不支持 Dynamic Provisioning、可执行文件要手动放到每个节点。

CSI 是新方案，把存储插件从 K8s 主干剥离成独立 gRPC 服务，三个 External Components（Driver Registrar/External Provisioner/External Attacher）作为 sidecar 和插件同 Pod 部署。CSI 插件提供三个 gRPC 服务：Identity（插件信息）、Controller（CreateVolume/ControllerPublishVolume 等，由 External Provisioner/Attacher 调用）、Node（NodeStageVolume/NodePublishVolume，由 kubelet 直接调用）。CSI 把职责从「两阶段」扩展成 Provision（建磁盘）+ Attach（挂磁盘到虚拟机）+ Mount（格式化挂到目录）三阶段。

我的判断：CSI 把存储插件标准化是必然——FlexVolume 的脚本式方案在状态管理、Dynamic Provisioning、跨平台部署上都有硬伤。作为 Java 后端我类比成从 shell 脚本到 Spring Boot 的演进：FlexVolume 像 CGI 脚本每次 fork 进程，CSI 是常驻 gRPC 服务，能维护状态、支持流式调用。CSI 的设计哲学和 K8s 一致——核心保持简洁，能力通过外部组件扩展，External Components 由社区维护但独立部署，CSI 插件本身由厂商编写。这种「K8s 不直接调 CSI Controller，而是 External Components 监听 PVC/VolumeAttachment 对象再调」的间接调用模式，和 Informer+workQueue 的解耦思想一脉相承。
