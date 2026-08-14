---
title: CNI 是 K8s 网络插件标准，Flannel/Calico/Cilium 各有取舍
date: 2026-08-12
category: tech
tags: [kubernetes, cni, network, architecture, reading]
status: raw
url: /k8s_lesson_html/34_Kubernetes网络模型与CNI网络插件.html
related:
  - 2026-08-12-k8s33-容器跨主机网络.md
  - 2026-08-12-k8s35-Kubernetes三层网络方案.md
---

K8s 用 cni0 网桥替代 docker0，因为 K8s 不用 Docker 的 CNM 模型。CNI 插件分三类：Main（bridge/ptp/macvlan 等创建网络设备）、IPAM（dhcp/host-local 分配 IP）、内置（flannel/portmap/bandwidth）。CNI 接口极简：只有 ADD（把容器加入 CNI 网络）和 DEL（移除）两个方法。kubelet 创建 Pod 时先起 Infra 容器 hold 住 Network Namespace，dockershim 调用 CNI 插件配置网络栈。Flannel CNI 插件用 delegate 机制调用 bridge 插件：创建 Veth Pair（一端容器 eth0，一端宿主机 vethxxx）、连到 cni0、设 hairpin mode（让 Pod 能通过 Service 访问自己）、调 IPAM 分配 IP、设默认路由。K8s 网络模型三要求：容器间无 NAT、宿主机与容器间无 NAT、容器看到的自己 IP 与外界看到的一致——一个字「通」。

**我的判断**：CNI 的设计是「最小接口+最大自由」——K8s 不实现网络，只定标准，把具体方案交给生态，这跟 CSI（存储）、CRI（运行时）一脉相承，是 K8s 可扩展性的核心。CNI 插件选型是生产环境的关键决策：Flannel 简单稳定但功能少（不支持 NetworkPolicy、不支持网络策略），适合小集群；Calico 功能全（BGP、NetworkPolicy、IPIP）但复杂度高，适合中大集群；Cilium 基于 eBPF，性能好且能做 L7 网络策略，是新趋势，但内核版本要求高（4.10+）。CNI 配置文件 /etc/cni/net.d/ 按字母序加载第一个，多个插件不能混用但可在一个配置文件里 plugins 字段协作（如 flannel+portmap）。delegate 机制让 Flannel 自己不做事只补充配置再调 bridge 插件，这种「薄封装」设计值得学习。
