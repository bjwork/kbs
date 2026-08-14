---
title: 安全容器：轻量VM做隔离，弥补namespace共享内核的软隔离
date: 2026-08-12
category: tech
tags: [kubernetes, security, runtime, container, reading]
status: raw
url: /k8s_lesson_html/47_绝不仅仅是安全_Kata_Containers与gVisor.html
related:
  - 2026-08-12-k8s06-白话容器基础二-隔离与限制.md
  - 2026-08-12-k8s36-Kubernetes只有soft-multi-tenancy.md
---

这篇讲安全容器，对多租户/不可信负载场景关键。问题根源：Linux 容器靠 namespace+cgroups 隔离，但共享宿主机内核——一旦容器逃逸（内核漏洞），整个宿主机沦陷。解法殊途同归：给容器进程一个独立内核。Kata Containers 是轻量 VM（Qemu 做 VMM），虚拟机即 Pod，用户容器是 VM 里的进程，原生只开 Mount Namespace 共享 Network；用 vhost 和 PCI Passthrough 优化 I/O。gVisor 更激进，用 Go 写个运行在用户态的 Sentry 进程冒充内核，拦截系统调用——Ptrace 实现性能太差只能 Demo，KVM 拦截性能可用，Google 内部用自己的 Hypervisor 比 KVM 还快。AWS Firecracker（Rust 写的 VMM）和 Kata 本质一样，只是 VMM 换了。

我的判断：安全容器的意义确实不止安全——内核版本解耦（宿主 3.6 跑要求 4.0 的应用）这个场景很实用，传统容器做不到。性能上 Kata 和 KVM 版 gVisor 半斤八两，gVisor 启动快资源省但系统调用密集的重 I/O 应用性能崩，且只支持 Linux 系统调用子集。gVisor 用 Go 重写内核子集是工程负债，长期看 Kata 团队的 Linuxd（用户态跑真 Linux Kernel via UML）思路更靠谱——别重写内核，复用。实战选择：多租户 PaaS、跑不可信代码（CI/CD、用户上传容器）、强合规场景上 Kata；gVisor 适合 Google 自家生态或轻量隔离需求。对一般业务，namespace 隔离 + seccomp + PodSecurityPolicy 够用，别为了安全上 VM 牺牲性能。安全容器不是银弹，是特定场景的权衡。
