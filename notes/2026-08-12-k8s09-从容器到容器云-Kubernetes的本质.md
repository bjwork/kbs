---
title: K8s 本质是声明式 API，不是更高级的调度器
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, reading]
status: raw
related_raw:
  - 2026-08-12-09_从容器到容器云_谈谈Kubernetes的本质.html
---

张磊这篇把 K8s 的「出身」和「野心」讲清楚了：容器拆成「镜像（静态视图）+ 运行时（动态视图）」两半，真正值钱的不是容器本身，而是容器编排。K8s 脱胎于 Borg 论文，一开始就站在「编排大规模任务关系」的高度，而不是 Docker Swarm 那种「把容器放到合适节点」的调度层。

核心设计是声明式 API：用「编排对象」（Pod/Job/CronJob）描述应用，用「服务对象」（Service/Secret/HPA）描述平台能力，统一处理容器间的访问关系、紧密协作关系、凭证关系，而不是为每种关系造一个指令。调度（placement）和编排（orchestration）的区别就在这里——编排要处理关系，调度只管放置。

**我的判断**：作为用 K8s 部署过服务的后端，最直接的启发是把视角从「K8s 是更高级的 Docker」切换到「K8s 是云时代的操作系统」。容器是进程，Pod 是进程组，K8s 是内核。这个类比比「Docker 升级版」准确得多，也解释了为什么 K8s 能成为云原生的事实标准——它定义的不是工具，是分布式系统的基础设施语义。AI 应用落地时，训练任务（Job）、推理服务（Deployment+HPA）、模型文件（PVC）都能映射成 API 对象，这套抽象的覆盖力远超 docker run。
