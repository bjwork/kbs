---
title: Device Plugin：K8s管理扩展资源（GPU/网卡）的机制，可用但不好用
date: 2026-08-12
category: tech
tags: [kubernetes, gpu, scheduling, runtime, reading]
status: raw
related_raw:
  - 2026-08-12-44_Kubernetes_GPU管理与Device_Plugin机制.html
---

这篇对我做 AI 训练推理集群直接相关。核心机制：GPU 不走专门资源类型，走 Extended Resource（如 nvidia.com/gpu: 1），调度器只认数字不认含义。Device Plugin 是个 gRPC 服务，两个核心 API：ListAndWatch 向 kubelet 汇报本机设备 ID 列表（kubelet 再以 Extended Resource 上报 APIServer）、Allocate 根据设备 ID 返回设备路径和驱动目录。分配流程：Pod 声明 nvidia.com/gpu:1 → 调度器找数量够的节点 → kubelet 从本地设备列表选一个 → 调 Device Plugin Allocate 拿设备路径/驱动目录 → 追加到 CRI 请求 → 容器启动后 /dev/nvidia0 和 /usr/local/nvidia/* 就位。

我的判断：这套设计最大问题是调度器只管"个数"，kubelet 负责具体设备挑选——这是个架构错位。调度器没有全局设备视图，无法做"把训练任务调到 GPU 互联最好的节点"这种决策。异构 GPU（V100/A100/H100 混部）、按拓扑亲和调度（NVLink/PCIe 路径）、GPU 显存细粒度切分（MIG）全部不支持。NVIDIA 自己 fork 改动是不得已，RedHat 推 ResourceClass 想把设备管理上浮到 API/调度层被否了，说明这是社区政治问题不是纯技术问题。对 AI 集群实战：要么用 NVIDIA 的 device plugin fork（支持 GPU 共享、拓扑感知），要么上 Volcano/Zeus 做细粒度 GPU 调度，原生 Device Plugin 只适合"一 Pod 一 GPU"的简单场景。这也解释了为什么 K8s 在 AI 训练调度上长期被 Slurm/Yarn 按在地上摩擦——调度器抽象层太薄。
