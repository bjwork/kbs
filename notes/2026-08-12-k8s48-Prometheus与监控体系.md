---
title: Prometheus是云原生监控事实标准，Metrics Server只管K8s内部
date: 2026-08-12
category: tech
tags: [kubernetes, monitoring, architecture, reading]
status: raw
url: /k8s_lesson_html/48_Prometheus_Metrics_Server与Kubernetes监控体系.html
---

K8s 监控体系这篇要厘清两件事：Prometheus 和 Metrics Server 不是一回事，定位完全不同。Prometheus 是云原生监控事实标准，源自 Google BorgMon，Pull 模式抓 Metrics 存 TSDB，配 Pushgateway（允许 Push）、Alertmanager（报警）、Grafana（可视化）。三种 Metrics 源：Node Exporter（宿主机，DaemonSet 部署）、组件 /metrics API（apiserver/kubelet 的 Work Queue 长度/QPS/延迟）、K8s 核心监控数据（Pod/Node/容器/Service，容器数据来自 kubelet 内置 cAdvisor）。

Metrics Server 定位完全不同——它只管 K8s 内部核心监控数据（Pod/Node 资源使用），通过 Aggregator APIServer 机制以标准 K8s API（metrics.k8s.io）暴露，给 HPA/VPA 用，取代旧的 Heapster。数据从 kubelet Summary API 采集（含 cAdvisor + kubelet 自身汇总）。Aggregator 机制让 kube-aggregator 按 URL 路由到不同后端（kube-apiserver 是一个，Metrics Server 是另一个），是 K8s 扩展 API 的标准方式。

我的判断：Prometheus 取代 Zabbix/传统监控在云原生场景是必然——Pull 模型配合服务发现天然适合动态调度环境，Zabbix 那套 Agent+中心化配置在 Pod 频繁生灭的 K8s 里水土不服。但 Prometheus 也有坑：单机 TSDB 扩展性差（长期存储要接 Thanos/Cortex）、Pull 模式对短生命周期 Job 不友好（靠 Pushgateway 补）、PromQL 学习曲线陡。Metrics Server 别和 Prometheus 搞混——前者是 K8s 调度链路的一环（HPA 依赖），后者是运维监控的一环。USE 原则（资源：利用率/饱和度/错误率）和 RED 原则（服务：请求数/错误数/响应时间）是规划监控指标的好框架，落地时容器用 USE、服务用 RED 交叉覆盖。
