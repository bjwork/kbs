# INDEX

> 自动生成，请勿手改。共 48 篇，更新于 2026-08-06

## 按分类

### ai-practice
- [[2026-08-05-ai-tagging.md]] 知识库的标签必须由 AI 打，人手打的没有语义 `knowledge-base` `llm` `workflow`
- [[2026-08-05-no-vector-kb.md]] 个人知识库不需要向量库，标签加打分就够用 `knowledge-base` `rag` `llm`

### misc
- [[2026-08-05-braised-pork.md]] 红烧肉先炒糖色还是先焯水 `cooking`

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

## 按标签

- `reading` × 45
- `performance` × 13
- `architecture` × 11
- `index` × 9
- `transaction` × 9
- `lock` × 7
- `ops` × 7
- `ha` × 6
- `optimizer` × 4
- `knowledge-base` × 2
- `llm` × 2
- `security` × 2
- `cooking` × 1
- `learning` × 1
- `rag` × 1
- `workflow` × 1
