---
title: Job/CronJob：离线批处理进 K8s，parallelism+completions 控并行
date: 2026-08-12
category: tech
tags: [kubernetes, container, architecture, job, reading]
status: raw
related_raw:
  - 2026-08-12-22_撬动离线业务_Job与CronJob.html
---

Deployment 管长作业（Long Running），Job 管离线批处理（Batch Job）。Pod 计算完退出算成功，restartPolicy 只能 Never 或 OnFailure。两个核心参数：parallelism（并发数）、completions（总任务数）。Job Controller 按公式「需要创建数 = completions - Running - 已成功」计算，再被 parallelism 截断。CronJob 是 Job 的控制器，schedule 字段写 Unix Cron 表达式，concurrencyPolicy 控制任务重叠策略（Allow/Forbid/Replace）。

**我的判断**：离线批处理进 K8s 后，资源池化和定时任务统一了。传统方案里 crontab 散落在每台机器、xxl-job 要单独搭调度中心，任务一多就难管——任务跑在哪台机器、资源够不够、失败了重试几次，全靠脚本和运维经验。Job 对象把「并行度、完成数、重试、超时」变成可声明字段，CronJob 再包一层定时，整个离线任务体系进了 K8s 调度域，资源和在线业务共享一个池子，这才是「混合调度」的价值。但我要点出一个实际取舍：简单 ETL 用 Job 够了，复杂依赖（任务间有 DAG、输出喂给下一个任务）Job 表达不了，得 Airflow 或 Argo Workflows 这类上层编排，Job 只当执行单元。对 AI 场景特别相关——模型训练就是个 Batch Job，Kubeflow 的 TFJob 底层就是 Job 加 Operator。concurrencyPolicy=Forbid 这个细节也实用，避免上次训练没跑完又起一个把显存打爆。
