---
title: 三层方案（Calico BGP）避免 overlay 性能损耗，适合大规模集群
date: 2026-08-12
category: tech
tags: [kubernetes, network, cni, architecture, reading]
status: raw
related_raw:
  - 2026-08-12-35_解读Kubernetes三层网络方案.html
related:
  - 2026-08-12-k8s33-容器跨主机网络.md
  - 2026-08-12-k8s34-Kubernetes网络模型与CNI.md
---

Flannel host-gw 是最简单的三层方案：把每个子网的下一跳设为对应宿主机 IP，宿主机充当网关，无封包解包，性能损失约 10%（VXLAN 是 20%~30%），但要求宿主机二层连通。Calico 是三层方案的龙头，与 host-gw 原理一致，但用 BGP 协议自动分发路由信息（Flannel 用 Etcd+flanneld）。Calico 三组件：CNI 插件（对接 K8s）、Felix（DaemonSet，写路由规则）、BIRD（BGP 客户端，分发路由）。Calico 不用网桥，每个容器一个 Veth Pair（cali 前缀）+ 一条路由规则。Node-to-Node Mesh 模式 BGP 连接数 N² 增长，<100 节点用；>100 节点用 Route Reflector 模式，连接数降到 N。跨子网场景：host-gw 和 Calico 默认都要求二层连通，跨子网要么开 IPIP（封装，性能与 VXLAN 相当），要么把宿主机网关也拉进 BGP Mesh。

**我的判断**：三层方案 vs overlay 的取舍是 K8s 网络的核心决策。**overlay（VXLAN）通用但性能损耗 20%~30%，三层方案（host-gw/Calico BGP）性能好但要求二层连通或额外配置**。我的建议：公有云上宿主机通常二层连通，直接 Flannel host-gw 最简单；私有云大规模集群用 Calico BGP + Route Reflector，性能和可扩展性都好。跨子网是常见痛点：IPIP 模式退化到 overlay 性能，更好的方案是把物理网关拉进 BGP Mesh（RR 节点兼任），但要求网络团队配合。Calico 的路由规则数量远多于 Flannel（每个容器一条），大规模集群排错困难，路由冲突概率也大——这是三层方案的代价。对 AI 训练集群，网络性能敏感（参数同步、梯度传输），三层方案是更优选择。
