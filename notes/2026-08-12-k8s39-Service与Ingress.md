---
title: Ingress 是七层入口，Nginx Ingress Controller 对比传统 Nginx+Keepalived 的取舍
date: 2026-08-12
category: tech
tags: [kubernetes, ingress, service, network, reading]
status: raw
url: /k8s_lesson_html/39_谈谈Service与Ingress.html
related:
  - 2026-08-12-k8s37-Service-DNS与服务发现.md
  - 2026-08-12-k8s38-连通Service与调试三板斧.md
---

Ingress 是「Service 的 Service」——全局负载均衡器，按域名+路径转发到不同 Service。Ingress 对象本质是对反向代理配置的抽象：host 是入口，path 对应后端 Service。Nginx Ingress Controller 是最常见实现：一个监听 Ingress 变化的控制器 Pod，根据 Ingress 对象生成 nginx.conf，通过 Lua 实现 Upstream 动态更新（Service 变化不 reload，只有 Ingress 规则变化才 reload）。Bare-metal 用 NodePort Service 暴露 Controller，公有云用 LoadBalancer。Ingress 只工作在七层，Service 只工作在四层，TLS 必须在 Ingress 做。Envoy/Traefik/HAProxy 都有对应 Controller，对中断敏感选 Traefik（热加载）。

**我的判断**：Ingress 的价值是把 Nginx 配置声明式化——传统 Nginx+Keepalived 方案要手动改 conf + reload + 维护 VIP，Ingress Controller 自动同步，这是云原生和传统运维的分水岭。但 Nginx Ingress 的坑也不少：ConfigMap 定制能力有限，复杂需求要写 snippet 甚至自定义模板；单副本 Controller 是单点，生产必须多副本+亲和反亲和；Bare-metal 下 NodePort 暴露 80/443 要么改 NodePort 范围要么用 MetalLB。对比传统方案：Keepalived 的 VIP 漂移比 K8s 的 NodePort 转发更直接，小规模稳定服务未必需要上 Ingress。对 Java 服务，Ingress 做七层路由+TLS 卸载，后端 Service 做四层负载，这是标准分层架构。
