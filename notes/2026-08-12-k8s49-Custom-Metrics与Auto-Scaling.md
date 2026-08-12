---
title: Custom Metrics：让 HPA 真正可用的自定义指标扩缩容
date: 2026-08-12
category: tech
tags: [kubernetes, autoscaling, monitoring, reading]
status: raw
related_raw:
  - 2026-08-12-49_Custom_Metrics_让Auto_Scaling不再食之无味.html
---

HPA 默认只能按 CPU/Memory 扩缩容，这是传统 PaaS 的水平，生产里基本是鸡肋——等 CPU 飙高时请求早已堆积，扩容严重滞后。真实业务要按 QPS、队列长度、消息堆积这些业务指标前置扩缩，才是生产级 HPA。

机制上，K8s 用 Aggregator APIServer 扩展出 `custom.metrics.k8s.io`，Custom Metrics APIServer 本质是 Prometheus 的 Adaptor：应用在 `/metrics` 暴露指标（如 `http_requests_total` counter），Prometheus 采集，Adaptor 把 counter 折算成毫秒级请求率（milli-requests）返回给 HPA，开发者不用自己算 QPS。ServiceMonitor 用 Label Selector 选目标 Pod，整套链路天然闭环。

我的判断：这套设计最精妙的地方是复用了 Aggregator——自定义指标像原生 API 一样可 `curl` 查询，HPA 不用改一行代码就能消费。对比传统 PaaS 把扩缩逻辑硬编码进平台，K8s 把「定义什么指标」还给应用、「如何扩缩」留给平台，这是 API 扩展性落到运维场景的典范。AI 场景下，按 GPU 利用率或推理队列长度扩缩 inference Pod，比按 CPU 靠谱得多。
