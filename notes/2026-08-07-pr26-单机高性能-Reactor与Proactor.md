---
title: 单机高性能-Reactor 与 Proactor：I/O 多路复用的三种形态
date: 2026-08-07
category: tech
tags: [architecture, java]
status: raw
related_raw:
  - 2026-08-07-26_19_单服务器高性能模式_Reactor与Proactor.html
---

PPC/TPC 卡在「一连接一资源」，Reactor 用**资源池 + I/O 多路复用**破题——一个进程管多个连接，**只在连接有数据时才处理**，靠 select/epoll/kqueue 让进程阻塞在一个对象上而不是轮询所有连接。

Reactor 中文叫「反应堆」其实误导——是「事件反应」（来了事件我有反应），也叫 Dispatcher 模式。核心组件：**Reactor（监听+分发）+ 资源池（处理业务）**。理论 4 种组合实际只用 3 种：

- **单 Reactor 单进程/线程**：Redis 就是这种。简单，无进程间通信无竞争，但**只吃一个核**，且 Handler 处理业务时无法响应其他连接——只适合业务处理极快的场景。C 系统用单进程，Java 用单线程（JVM 本身是进程）。
- **单 Reactor 多线程**：Handler 只负责事件响应，业务处理交给 Processor 子线程。能用多核，但引入线程同步复杂度（例如 Java NIO 的 Selector.selectedKeys() 非线程安全）。**单 Reactor 多进程不实用**——子进程处理完要把结果回传给父进程发送，但父子的通信不是 Reactor 监听的连接，硬要塞进 Reactor 就很别扭。
- **多 Reactor 多进程/线程**：mainReactor 只 accept，分给 subReactor，后者完整处理 read→业务→send。看似复杂其实**实现最简单**——职责清晰、子进程独立无共享。Nginx（多变体：子进程自己 accept，用锁防惊群）、Memcache、Netty 都是这种。

**Proactor**（真异步 I/O）：Reactor 是「事件来了我通知你，你自己 read/send」；Proactor 是「事件来了操作系统做完 I/O 再通知你」。**Linux 的 AIO 不完善，Linux 下实际都是 Reactor**；Windows 的 IOCP 才是真 Proactor。Boost.Asio 号称 Proactor，在 Linux 下其实是 epoll 模拟。

**立场**：这篇把 Reactor 三种形态和对应的开源实现讲得很清楚——Redis 单 Reactor 单进程、Nginx 多 Reactor 多进程、Netty 多 Reactor 多线程，记这三对关系面试就够用了。Proactor 那段打破「Linux 有 AIO 所以能真异步」的迷思——Linux 高并发就是 Reactor 的天下，不用挣扎。
