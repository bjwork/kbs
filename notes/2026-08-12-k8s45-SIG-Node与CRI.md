---
title: SIG-Node与kubelet：CRI解耦运行时，docker-shim被弃是必然
date: 2026-08-12
category: tech
tags: [kubernetes, runtime, cri, architecture, reading]
status: raw
url: /k8s_lesson_html/45_幕后英雄_SIG-Node与CRI.html
related:
  - 2026-08-12-k8s46-CRI与容器运行时.md
---

CRI/SIG-Node 上篇，讲 kubelet 工作原理和 CRI 由来。kubelet 是 K8s 第二个不可替代组件（第一个是 apiserver），别改它的代码。核心是 SyncLoop 控制循环，四种事件驱动：Pod 更新、Pod 生命周期变化、kubelet 执行周期、定时清理。下面挂一堆子 Manager（Volume/Image/Node Status/CPU Manager），都是控制器模式。Pod 调度到节点后触发 HandlePods 的 ADD 事件，起 Pod Update Worker 独立 Goroutine 处理。关键设计：SyncLoop 绝对不能阻塞，耗时操作（准备 Volume、拉镜像）必须起独立 Goroutine。

CRI 诞生背景是教训驱动的：1.6 之前 kubelet 直接调 Docker API，CoreOS 靠和 Google 关系硬把 rkt 支持塞进 kubelet 主干，结果 rkt 太小众、改 kubelet 必须靠 CoreOS 员工，拖慢开发还埋隐患。Kata Containers/runV 这类虚拟化容器又快成熟，再硬塞 kubelet 就废了。所以 SIG-Node 2016 年把容器操作抽象成 CRI gRPC 接口，kubelet 只跟接口打交道，容器项目自己实现 shim。

我的判断：dockershim 被废弃是必然。它长期内嵌在 kubelet 代码里是历史包袱——为支持 Docker 单独维护一套，而 containerd/CRI-O 这些原生 CRI 实现更干净。Docker 作为一个产品而非运行时标准被淘汰是早晚的事，containerd 才是正道。理解 CRI 才能懂为什么 K8s 1.24 彻底移除 dockershim：不是 Docker 公司做错了什么，是 kubelet 不该背着别人的兼容层跑。实战上直接上 containerd，别再纠结 Docker。
