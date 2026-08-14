---
title: Service 是反向代理+负载均衡+固定IP，对比 Spring Cloud Eureka 的声明式服务发现
date: 2026-08-12
category: tech
tags: [kubernetes, service, dns, network, reading]
status: raw
url: /k8s_lesson_html/37_找到容器不容易_Service_DNS与服务发现.html
related:
  - 2026-08-12-k8s38-连通Service与调试三板斧.md
  - 2026-08-12-k8s39-Service与Ingress.md
---

Service 解决两个问题：Pod IP 不固定、一组 Pod 需要负载均衡。实现：kube-proxy 监听 Service/Endpoints 变化，在宿主机生成 iptables 规则——访问 VIP 的 IP 包经 KUBE-SERVICES 链 → KUBE-SVC 链（random 模式按概率分流，1/3、1/2、1）→ KUBE-SEP 链（DNAT 到具体 Pod IP:Port）。VIP 不是真实设备，ping 不通。iptables 模式在大规模集群是瓶颈（规则数随 Pod 线性增长，刷新占用 CPU），IPVS 模式用 kube-ipvs0 虚拟网卡 + 内核 IPVS 模块，负载均衡逻辑下沉内核态，规则数量不随 Pod 增加，大规模集群必选。DNS：ClusterIP Service 的 A 记录是 ..svc.cluster.local → VIP；Headless Service（clusterIP=None）的 A 记录返回所有 Pod IP 集合。

**我的判断**：Service 的设计哲学是「网络层透明代理」——应用无感知，不用改代码就能用，这点比 Spring Cloud Eureka 优雅。Eureka 是客户端服务发现：应用注册、客户端拉取列表、Ribbon 负载均衡，强耦合语言生态；K8s Service 是基础设施层：iptables/IPVS 在内核做 DNAT，任何语言透明接入。但 K8s Service 默认只有轮询（rr），没有权重、熔断、重试，这些能力要靠 Service Mesh（Istio）补——这也是为什么 Service Mesh 出现。Headless Service 是 StatefulSet 的基础，给每个 Pod 稳定的 DNS 名字，适合有状态服务（数据库主从、Zookeeper）。生产建议：大规模集群 kube-proxy 必须开 IPVS 模式，iptables 模式过千 Pod 就明显吃力。
