# 项目开发约定

- 本项目是普通 Python 医疗知识图谱与规则问答项目，按实际功能维护目录。
- 目录职责：代码在 red_spider/，数据在 red_spider/data/，词典在 red_spider/dict/；仓库根目录保留文档、依赖和测试。
- 不创建 memory/、agents/、prompts/、context/、skills/、tools/、workflows/、evals/ 等无实际功能的占位目录。
- 维持构图、分类、解析、查询、命令行入口的现有边界，不引入无关框架。
- 原始医疗数据与词典不覆写；更新前核对来源、许可和哈希，并更新 docs/source_manifest.json。
- 所有 Neo4j 数据值使用参数；数据库密码只从环境变量读取，不输出、不提交。
- 必跑：python -m unittest discover -s tests -v；python -m compileall -q red_spider tests。
- 数据库写入变更需在专用空库验证首次导入、重复导入与查询；未执行时明确记录限制。
- README 必须同步目录、安装配置、运行、验证和数据说明；每轮迭代追加日期、范围、变化、实际验证结果及未完成项。
- 区分原项目版本与本提取项目整理轮次，不能把源目录存在写成版本已运行或已验收。

- 对外 README 围绕项目背景、架构、技术栈、功能、验证、运行和限制组织；仅记录真实实现与实测结果。

- versions/v1.1 与 versions/v2.0 保存后续版本；同名模块须分进程启动与测试，避免 sys.modules 混用。
- 所有版本改动必跑 python -m unittest discover -s tests -v 和 python -m compileall -q red_spider versions tests。
- 模型权重由 docs/model_assets.json 记录，保留原文件，不提交大型二进制或调用未经显式开启的外部模型服务。
