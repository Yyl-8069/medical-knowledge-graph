# 验证记录

环境：Python 3.8.5、neo4j 5.28.2、pyahocorasick 2.1.0。使用当前已安装环境，未重新在线安装依赖或创建虚拟环境。

## 第 1 轮：2026-10-31，提取与运行修正

- 五项离线测试通过；当时根目录的六个 Python 模块和 tests/ 编译通过。
- 全量数据 8,808 条、8,807 个不同疾病名；四份词典与源文件哈希一致。
- 原项目十个来源文件的 SHA-256 与提取前一致。
- 数据库调用用 mock 验证；未执行真实数据库导入和问答。

## 第 2 轮：2026-10-31，重整模块与数据目录

- 从仓库根目录运行 `python -m unittest discover -s tests -v`：五项通过。
- 从外部工作目录运行 `python -m unittest discover -s E:\vscode\project3\medical-knowledge-graph\tests -v`：五项通过。
- `python -m compileall -q red_spider tests`：通过。
- 从外部工作目录调用 `MedicalGraph().read_nodes()`，成功通过迁移后的默认路径读取完整医疗数据，实体去重数量为 Drug 3,800、Food 4,506、Symptom 5,998、Disease 8,807。
- 八个无实际用途的占位目录已删除；核心代码、data/、dict/ 均位于 red_spider/ 下，符合项目模块与数据路径约定。
- 数据与四份词典哈希不变；原项目十个来源文件哈希不变。
- README 记录目录职责、数据统计、环境、运行与验证命令、原版本和两轮整理记录；来源清单新增提取后的 project_file 路径。
- 离线数量见 data_statistics.json；实际 Neo4j 写入、重复导入及真实问答仍未执行。

## 第 3 轮：2026-10-31，项目说明与固定集评估

- 重跑五项离线测试通过，原始输出见 test_output.txt。
- 新增 12 条人工固定冒烟问句，真实分类器和解析器的意图集合精确匹配为 11/12；详细结果见 evaluation_results.json。
- 保留未命中的食物问句改写案例，不将固定集分数视为医疗答案准确率。
- 运行图展示真实离线报告；Neo4j 集成、真实数据库问答和性能测试仍未执行。
