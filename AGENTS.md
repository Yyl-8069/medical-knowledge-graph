# 开发约定

- 普通 Python + Neo4j 图谱构建与结构化查询项目，保留 qingnang/ 和 data/medical.json。
- 支持用户授权的单次图谱检索+模型回答；不添加多轮聊天或 Agent 架构；原始数据保持 SHA-256 不变。
- 数据值采用参数化 Cypher，密码从环境变量获取，不打印、不提交。
- 导入默认预览，--execute 才写入；普通模式遇同名节点停止；显式补齐模式固定端点且保留旧节点，不自动清理旧库。
- 必跑 python -m unittest discover -s tests -v，以及 python -m compileall -q qingnang tests。
- 写入应在专用空库验证首次与重复导入；未验证时明确记录。
- README 同步项目用途、架构、目录、数据、运行、真实验证与迭代，不虚构截图或性能。
