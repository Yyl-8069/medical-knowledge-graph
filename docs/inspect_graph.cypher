// 逐条在 Neo4j Browser 执行，只读查询。
// 1. 当前库中的节点标签及数量
MATCH (n) UNWIND labels(n) AS label
RETURN label, count(*) AS node_count ORDER BY node_count DESC;

// 2. 实际关系的方向、端点标签和数量
MATCH (a)-[r]->(b)
RETURN labels(a) AS source_labels, type(r) AS relation,
       labels(b) AS target_labels, count(*) AS edge_count
ORDER BY edge_count DESC;

// 3. 发烧/发热到底是什么节点，直接连向哪些节点（双向检查）
MATCH (n) WHERE n.name IN ['发烧', '发热']
OPTIONAL MATCH (n)-[r]-(m)
RETURN n.name AS entity, labels(n) AS entity_labels,
       type(r) AS relation, labels(m) AS neighbor_labels,
       count(r) AS edge_count;

// 4. 验证感冒到药品的实际关系名称
MATCH (d:Disease {name:'感冒'})-[r]->(drug:Drug)
RETURN type(r) AS relation, drug.name AS drug_name LIMIT 20;
