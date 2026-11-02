// Neo4j Browser 中逐条执行；RETURN 节点与关系可显示 Graph 视图。
MATCH (d:Disease {name:'感冒'})-[r:command_drug|recommand_drug]->(n:Drug)
RETURN d,r,n LIMIT 30;

MATCH (d:Disease {name:'感冒'})-[r:has_symptom]->(n:Symptom)
RETURN d,r,n LIMIT 30;

MATCH (d:Disease)-[r:need_check]->(n:Check {name:'伸肘试验'})
RETURN d,r,n LIMIT 30;

// 只读核查重复疾病名，不删除或合并。
MATCH (d:Disease)
WITH d.name AS name,count(*) AS quantity
WHERE quantity > 1
RETURN name,quantity ORDER BY quantity DESC;
