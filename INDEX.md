# INDEX

> 自动生成，请勿手改。共 121 篇，更新于 2026-08-08

## 按分类

### ai-practice
- [[2026-08-05-ai-tagging.md]] 知识库的标签必须由 AI 打，人手打的没有语义 `knowledge-base` `llm` `workflow`
- [[2026-08-05-no-vector-kb.md]] 个人知识库不需要向量库，标签加打分就够用 `knowledge-base` `rag` `llm`

### misc
- [[2026-08-05-braised-pork.md]] 红烧肉先炒糖色还是先焯水 `cooking`
- [[2026-08-07-pr64-新书首发-从零开始学架构.md]] 新书首发《从零开始学架构》：专栏的纸质沉淀 `architecture` `reading`
- [[2026-08-07-pr65-致从0开始学架构订阅用户.md]] 致订阅用户：26000 份免费午餐 `architecture` `growth`
- [[2026-08-07-pr66-第二季回归-大厂晋升指南.md]] 第二季回归《大厂晋升指南》：晋升是个系统工程 `architecture` `growth`
- [[2026-08-07-pr69-加餐-业务架构实战营开营.md]] 业务架构实战营招生贴：用实战补专栏「理论派」的短板 `architecture`
- [[2026-08-07-pr72-结课测试-架构技能自测.md]] 结课测试入口页：20 道题自测架构技能掌握度 `architecture`

### reading
- [[2026-08-07-pr59-特别放送-华仔放学别走1期.md]] 华仔放学别走 1 期：写博客、知行合一、三本书 `architecture` `growth`
- [[2026-08-07-pr60-特别放送-华仔放学别走2期.md]] 华仔放学别走 2 期：学新技术的组合拳、架构师的沟通 `architecture` `growth`
- [[2026-08-07-pr62-特别放送-架构师成长之路.md]] 架构师成长之路：判断力/执行力/创新力，六阶段路径 `architecture` `growth`
- [[2026-08-07-pr63-特别放送-架构师必读书单.md]] 架构师必读书单：成长/技术/业务三类 `architecture` `reading`
- [[2026-08-07-pr71-结束语-坚持成就技术梦想.md]] 专栏收尾：坚持梦想、坚持学习、坚持输出三件事 `architecture` `growth`

### tech
- [[2026-08-05-mysql45-01-基础架构.md]] MySQL 基础架构：一条查询经过连接器、分析器、优化器、执行器 `architecture` `reading`
- [[2026-08-05-mysql45-02-日志系统-redo与binlog.md]] 日志系统：redo log 与 binlog 的两阶段提交 `architecture` `reading`
- [[2026-08-05-mysql45-03-事务隔离-MVCC与长事务.md]] 事务隔离：MVCC 多版本视图与长事务的坑 `transaction` `reading`
- [[2026-08-05-mysql45-04-索引上-B树与自增主键.md]] 索引（上）：B+ 树与自增主键的选择 `index` `reading`
- [[2026-08-05-mysql45-05-索引下-覆盖索引与最左前缀.md]] 索引（下）：覆盖索引、最左前缀、索引下推 `index` `reading`
- [[2026-08-05-mysql45-06-全局锁表锁与MDL.md]] 全局锁与表锁：MDL 是线上 DDL 事故的元凶 `lock` `reading`
- [[2026-08-05-mysql45-07-行锁与死锁.md]] 行锁：两阶段锁、死锁与减少锁冲突 `lock` `transaction` `reading`
- [[2026-08-05-mysql45-08-事务可见性与当前读.md]] 事务可见性：一致性视图 vs 当前读 `transaction` `reading`
- [[2026-08-05-mysql45-09-普通索引唯一索引与change-buffer.md]] 普通索引 vs 唯一索引：change buffer 的天平 `index` `reading`
- [[2026-08-05-mysql45-10-优化器选错索引.md]] 优化器选错索引：统计信息是个采样估算 `index` `optimizer` `reading`
- [[2026-08-05-mysql45-11-字符串前缀索引.md]] 字符串索引：前缀索引的四种权衡 `index` `reading`
- [[2026-08-05-mysql45-12-抖动与刷脏页.md]] MySQL 抖一下：WAL 的代价是刷脏页 `performance` `reading`
- [[2026-08-05-mysql45-13-删数据与表空间回收.md]] 删数据不收空间：delete 只标记，重建表才回收 `ops` `reading`
- [[2026-08-05-mysql45-14-count与计数方案.md]] count(*) 为什么慢：MVCC 的代价与计数的正确姿势 `performance` `transaction` `reading`
- [[2026-08-05-mysql45-15-答疑一-日志与索引.md]] 答疑一：日志与索引的边角问题 `index` `reading`
- [[2026-08-05-mysql45-16-order-by与filesort.md]] order by 怎么工作：filesort 的两种算法与排序优化 `performance` `optimizer` `reading`
- [[2026-08-05-mysql45-17-随机显示与order-by-rand.md]] 随机显示：order by rand() 为什么慢与三种替代方案 `performance` `reading`
- [[2026-08-05-mysql45-18-索引字段函数失效.md]] 逻辑相同性能迥异：索引字段上的函数是隐形杀手 `index` `performance` `reading`
- [[2026-08-05-mysql45-19-查一行也慢.md]] 查一行也慢：锁等待与一致性读的代价 `lock` `transaction` `reading`
- [[2026-08-05-mysql45-20-幻读与间隙锁.md]] 幻读与间隙锁：行锁锁不住的「新插入」 `transaction` `lock` `reading`
- [[2026-08-05-mysql45-21-加锁规则与next-key-lock.md]] InnoDB 加锁规则：next-key lock 的两原则两优化 `lock` `transaction` `reading`
- [[2026-08-05-mysql45-22-高峰期应急手段.md]] 高峰期续命手段：短连接风暴、慢查询与语句重写 `ops` `performance` `reading`
- [[2026-08-05-mysql45-23-数据不丢与组提交.md]] 数据不丢的保证：redo log/binlog 的三层缓冲与组提交 `architecture` `performance` `reading`
- [[2026-08-05-mysql45-24-主备一致与binlog格式.md]] 主备一致：binlog 三种格式与主备切换 `architecture` `ha` `reading`
- [[2026-08-05-mysql45-25-高可用与主备切换.md]] 高可用基础：主备延迟与两种切换策略 `ha` `architecture` `reading`
- [[2026-08-05-mysql45-26-备库延迟与并行复制.md]] 备库延迟数小时：并行复制的演进 `ha` `performance` `reading`
- [[2026-08-05-mysql45-27-主从切换与GTID.md]] 一主多从切换：GTID 解决位点找寻之痛 `ha` `ops` `reading`
- [[2026-08-05-mysql45-28-读写分离与过期读.md]] 读写分离的坑：过期读与四种应对 `ha` `architecture` `reading`
- [[2026-08-05-mysql45-29-数据库健康检查.md]] 判断数据库是否出问题：健康检查的演进 `ops` `ha` `reading`
- [[2026-08-05-mysql45-30-答疑二-动态看加锁.md]] 答疑二：动态视角看加锁——配合执行计划分析 `lock` `transaction` `reading`
- [[2026-08-05-mysql45-31-误删数据与预防体系.md]] 误删数据怎么办：预防体系比恢复手段重要 `ops` `security` `reading`
- [[2026-08-05-mysql45-32-kill不掉的语句.md]] kill 不掉的语句：终止是个协作式请求 `ops` `reading`
- [[2026-08-05-mysql45-33-大查询与内存管理.md]] 大查询会打爆内存吗：边算边发与 LRU 改进 `performance` `architecture` `reading`
- [[2026-08-05-mysql45-34-join算法与选择.md]] join 能用吗：NLJ 与 BNL 的分水岭 `index` `performance` `reading`
- [[2026-08-05-mysql45-35-join优化-BKA与临时表.md]] join 优化：BKA、临时表与应用层 hash join `performance` `optimizer` `reading`
- [[2026-08-05-mysql45-36-临时表与会话隔离.md]] 临时表为什么能重名：会话隔离的实现 `architecture` `reading`
- [[2026-08-05-mysql45-37-内部临时表与group-by.md]] 内部临时表：group by 什么时候要用它 `performance` `optimizer` `reading`
- [[2026-08-05-mysql45-38-Memory引擎的坑.md]] Memory 引擎还能用吗：生产别用，临时表是它的归宿 `architecture` `reading`
- [[2026-08-05-mysql45-39-自增主键空洞.md]] 自增主键为什么不连续：空洞的四个来源 `index` `reading`
- [[2026-08-05-mysql45-40-insert的锁.md]] insert 的锁：唯一键冲突的 S 锁与 insert...select `lock` `transaction` `reading`
- [[2026-08-05-mysql45-41-最快复制一张表.md]] 最快复制一张表：三种方式的取舍 `ops` `performance` `reading`
- [[2026-08-05-mysql45-42-grant与flush-privileges.md]] grant 后要 flush privileges 吗：权限的内存与磁盘 `security` `reading`
- [[2026-08-05-mysql45-43-分区表的取舍.md]] 要不要用分区表：两个绕不开的问题 `architecture` `reading`
- [[2026-08-05-mysql45-44-答疑三-好问题的价值.md]] 答疑三：好问题是知识网络的连接器 `learning` `reading`
- [[2026-08-05-mysql45-45-自增id上限.md]] 自增 id 用完怎么办：四种 id 的上限行为 `architecture` `reading`
- [[2026-08-07-pr00-旅程再启-架构师适应技术浪潮.md]] 旅程再启：架构师该如何适应新的技术浪潮 `architecture` `reading`
- [[2026-08-07-pr01-微服务接口类设计技巧.md]] 微服务接口类设计技巧：BFF、GraphQL、接口循环调用 `architecture` `microservice` `reading`
- [[2026-08-07-pr02-业务级分布式事务四模式.md]] 业务级分布式事务四模式：本地消息/MQ事务/TCC/SAGA `architecture` `microservice` `transaction` `reading`
- [[2026-08-07-pr03-全局幂等.md]] 全局幂等：事务级同步/异步、接口级自动、四种幂等判断手段 `architecture` `microservice` `transaction` `reading`
- [[2026-08-07-pr04-异地多活三种成熟模式.md]] 异地多活三种成熟模式：业务定制型/业务通用型/存储通用型 `architecture` `ha` `reading`
- [[2026-08-07-pr05-云原生时代架构师进化.md]] 云原生时代架构师的进化：云产品抹平技术层差 `architecture` `cloud-native` `reading`
- [[2026-08-07-pr06-AI时代架构师进化.md]] AI 时代架构师的进化：大模型无法取代架构师的两个本质原因 `architecture` `llm` `reading`
- [[2026-08-07-pr07-开篇词-照着做你也能成为架构师.md]] 开篇词：架构设计的思维是判断和取舍，不是逻辑和实现 `architecture` `learning` `reading`
- [[2026-08-07-pr08-架构到底是指什么-4R定义.md]] 架构到底是指什么：4R 架构定义（Rank/Role/Relation/Rule） `architecture` `reading`
- [[2026-08-07-pr09-架构设计的历史背景.md]] 架构设计的历史背景：模块/对象/组件的演进 `architecture` `reading`
- [[2026-08-07-pr10-架构设计的目的.md]] 架构设计的目的：只为解决复杂度 `architecture` `reading`
- [[2026-08-07-pr11-复杂度来源-高性能.md]] 复杂度来源-高性能：单机并发与集群任务分配/分解 `architecture` `reading`
- [[2026-08-07-pr12-复杂度来源-高可用.md]] 复杂度来源-高可用：冗余的代价是状态决策 `architecture` `reading`
- [[2026-08-07-pr13-复杂度来源-可扩展性.md]] 复杂度来源-可扩展性：2 年法则 + 1 写 2 抄 3 重构 `architecture` `reading`
- [[2026-08-07-pr14-复杂度来源-低成本安全规模.md]] 复杂度来源-低成本/安全/规模 `architecture` `reading`
- [[2026-08-07-pr15-架构设计三原则.md]] 架构设计三原则：合适/简单/演化 `architecture` `reading`
- [[2026-08-07-pr16-架构设计原则案例.md]] 架构原则案例：淘宝和手机 QQ 的演化史 `architecture` `reading`
- [[2026-08-07-pr17-架构设计流程-识别复杂度.md]] 架构流程-识别复杂度：排查法+优先级排序 `architecture` `reading`
- [[2026-08-07-pr18-架构设计流程-设计备选方案.md]] 架构流程-设计备选方案：3-5 个、差异明显、别太重细节 `architecture` `reading`
- [[2026-08-07-pr19-架构设计流程-评估备选方案.md]] 架构流程-评估备选方案：360 度环评 + 按优先级选 `architecture` `reading`
- [[2026-08-07-pr20-架构设计流程-详细方案设计.md]] 架构流程-详细方案设计：把选定方案落到地 `architecture` `reading`
- [[2026-08-07-pr21-高性能数据库-读写分离.md]] 高性能数据库集群-读写分离：复制延迟与分配机制 `architecture` `java`
- [[2026-08-07-pr22-高性能数据库-分库分表.md]] 高性能数据库集群-分库分表：代价清单 `architecture` `java`
- [[2026-08-07-pr23-高性能NoSQL-四类方案.md]] 高性能 NoSQL：四类方案对应关系型数据库的四个缺陷 `architecture` `java`
- [[2026-08-07-pr24-高性能缓存架构.md]] 高性能缓存架构：穿透/雪崩/热点三大坑 `architecture` `java`
- [[2026-08-07-pr25-单机高性能-PPC与TPC.md]] 单机高性能-PPC 与 TPC：每连接一进程/线程的局限 `architecture` `java`
- [[2026-08-07-pr26-单机高性能-Reactor与Proactor.md]] 单机高性能-Reactor 与 Proactor：I/O 多路复用的三种形态 `architecture` `java`
- [[2026-08-07-pr27-负载均衡分类.md]] 负载均衡分类：DNS/硬件/软件三层组合 `architecture` `java`
- [[2026-08-07-pr28-负载均衡算法.md]] 负载均衡算法：轮询/负载/性能/Hash 四大类 `architecture` `java`
- [[2026-08-07-pr29-CAP理论.md]] CAP 理论：三选二，且 P 必选 `architecture` `reading`
- [[2026-08-07-pr30-CAP细节.md]] CAP 细节：粒度是数据不是系统，CA 才是常态 `architecture` `reading`
- [[2026-08-07-pr31-FMEA方法.md]] FMEA 法：排除架构可用性隐患 `architecture` `workflow`
- [[2026-08-07-pr32-高可用存储-双机架构.md]] 高可用存储-双机架构：主备/主从/切换/主主 `architecture` `java`
- [[2026-08-07-pr33-高可用存储-集群与分区.md]] 高可用存储-集群与分区：数据集中 vs 分散 `architecture` `reading`
- [[2026-08-07-pr34-计算高可用.md]] 计算高可用：主备/主从/对称/非对称集群 `architecture` `reading`
- [[2026-08-07-pr35-异地多活三种模式.md]] 异地多活三种模式：同城异区/跨城/跨国 `architecture` `reading`
- [[2026-08-07-pr36-异地多活设计4技巧.md]] 异地多活设计 4 大技巧 `architecture` `reading`
- [[2026-08-07-pr37-异地多活设计4步走.md]] 异地多活设计 4 步走：业务分级→数据分类→同步→异常处理 `architecture` `reading`
- [[2026-08-07-pr38-接口级故障应对.md]] 接口级故障应对：降级/熔断/限流/排队 `architecture` `java`
- [[2026-08-07-pr39-可扩展架构基本思想.md]] 可扩展架构基本思想：一个「拆」字 `architecture` `reading`
- [[2026-08-07-pr40-分层架构与SOA.md]] 分层架构与 SOA：传统可扩展模式的优劣 `architecture` `reading`
- [[2026-08-07-pr41-微服务银弹或焦油坑.md]] 微服务：银弹还是焦油坑 `architecture` `reading`
- [[2026-08-07-pr42-微服务最佳实践-方法篇.md]] 微服务最佳实践-方法篇：三个火枪手+四种拆分 `architecture` `reading`
- [[2026-08-07-pr43-微服务最佳实践-基础设施篇.md]] 微服务最佳实践-基础设施篇：9 大组件 `architecture` `java`
- [[2026-08-07-pr44-微内核架构.md]] 微内核架构：核心系统+插件模块 `architecture` `java`
- [[2026-08-07-pr45-技术演进方向判断.md]] 技术演进方向：业务驱动，不是技术驱动 `architecture` `reading`
- [[2026-08-07-pr46-互联网技术演进模式.md]] 互联网技术演进模式：初创/发展/竞争/成熟 `architecture` `reading`
- [[2026-08-07-pr47-互联网架构-存储层.md]] 互联网架构模板-存储层：SQL/NoSQL/小文件/大文件 `architecture` `reading`
- [[2026-08-07-pr48-互联网架构-开发层服务层.md]] 互联网架构模板-开发层与服务层 `architecture` `java`
- [[2026-08-07-pr49-互联网架构-网络层.md]] 互联网架构模板-网络层：LB/CDN/多机房/多中心 `architecture` `reading`
- [[2026-08-07-pr50-互联网架构-用户层业务层.md]] 互联网架构模板-用户层与业务层 `architecture` `reading`
- [[2026-08-07-pr51-互联网架构-平台技术.md]] 互联网架构模板-平台技术：运维/测试/数据/管理 `architecture` `reading`
- [[2026-08-07-pr52-架构重构-有的放矢.md]] 架构重构第一式-有的放矢：只解核心问题 `architecture` `reading`
- [[2026-08-07-pr53-架构重构-合纵连横.md]] 架构重构第二式-合纵连横：沟通与推动 `architecture` `workflow`
- [[2026-08-07-pr54-架构重构-运筹帷幄.md]] 架构重构第三式-运筹帷幄：分段实施 `architecture` `workflow`
- [[2026-08-07-pr55-开源项目选择使用.md]] 开源项目选择/使用/二次开发 `architecture` `open-source`
- [[2026-08-07-pr56-App架构演进.md]] App 架构演进：Web→原生→Hybrid→组件化→跨平台 `architecture` `reading`
- [[2026-08-07-pr57-架构设计文档模板.md]] 架构设计文档模板：5W1H8C + 备选方案 + 详细设计 `architecture` `workflow`
- [[2026-08-07-pr58-如何画架构图.md]] 画架构图：用 4R 代替 4+1 视图 `architecture` `workflow`
- [[2026-08-07-pr61-特别放送-高效学习开源项目.md]] 高效学习开源项目：自顶向下五步法，源码放最后 `architecture` `open-source`
- [[2026-08-07-pr67-加餐-单服务器高性能性能对比.md]] 用真实压测数据补齐 PPC/TPC/Reactor 七种网络模式的性能对比 `architecture` `java`
- [[2026-08-07-pr68-加餐-扒一扒中台皇帝的外衣.md]] 从使用方视角拆穿中台神话：大业务优先、轮子常换、快是错觉 `architecture`
- [[2026-08-07-pr70-ChatGPT来临架构师何去何从.md]] ChatGPT 取代不了架构师，但会淘汰只背 API 的程序员 `architecture` `ai-native`

## 按标签

- `reading` × 87
- `architecture` × 84
- `java` × 14
- `performance` × 13
- `transaction` × 11
- `index` × 9
- `ha` × 7
- `lock` × 7
- `ops` × 7
- `growth` × 6
- `workflow` × 6
- `optimizer` × 4
- `llm` × 3
- `microservice` × 3
- `knowledge-base` × 2
- `learning` × 2
- `open-source` × 2
- `security` × 2
- `ai-native` × 1
- `cloud-native` × 1
- `cooking` × 1
- `rag` × 1
