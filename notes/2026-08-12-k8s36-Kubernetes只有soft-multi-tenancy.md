---
title: K8s 的 namespace 隔离是软隔离，强隔离要靠 VM 或虚拟集群
date: 2026-08-12
category: tech
tags: [kubernetes, network, security, architecture, reading]
status: raw
url: /k8s_lesson_html/36_为什么说Kubernetes只有soft_multi-tenancy.html
related:
  - 2026-08-12-k8s47-Kata-Containers与gVisor.md
---

NetworkPolicy 是 K8s 的网络隔离手段，本质是宿主机上的 iptables 规则。Pod 默认「允许所有」，NetworkPolicy 选中后变「拒绝所有」，再通过白名单（ipBlock/namespaceSelector/podSelector）放行。白名单语义易错：from 字段下多个 selector 是 OR，同一 from 元素内 namespaceSelector 和 podSelector 并列是 AND。NetworkPolicy 只在支持它的 CNI 插件上生效（Calico、Weave、kube-router），Flannel 不支持，需额外装 Calico。底层实现：FORWARD 链拦截发往被隔离 Pod 的包 → KUBE-POD-SPECIFIC-FW-CHAIN → KUBE-NWPLCY-CHAIN 匹配白名单，不匹配则 REJECT。K8s 网络模型只关注「连通」不关注「隔离」，与 IaaS 的安全组类似但更弱。

**我的判断**：这篇的安全警示很关键——**K8s 从设计上就是 soft multi-tenancy，不是强隔离**。namespace 只是逻辑分组，不是安全边界；NetworkPolicy 是 iptables 规则，不是硬件防火墙。对安全要求高的场景（多团队共用集群、对外提供 PaaS），纯 K8s 隔离不够，要么用虚拟集群（vcluster、KubeVirt），要么用 Kata Containers/gVisor 做沙箱运行时，最彻底的是每个租户独立集群。NetworkPolicy 的白名单语义是排坑重灾区，AND/OR 写错一个缩进就导致隔离失效，生产环境必须用工具验证规则（如 kubectl-npolicy 工具）。Flannel 不支持 NetworkPolicy 是个硬伤，生产环境直接上 Calico 更省心。对 AI 平台，多租户训练任务的隔离不能只靠 NetworkPolicy，GPU 资源隔离（nvidia.com/gpu）和 namespace 配额要一起上。
