"""Structured, read-only Neo4j queries. No dialogue or local answer fallback."""
import argparse
import json
from neo4j import GraphDatabase
from config import get_neo4j_config, get_database

QUERIES = {
    'companions': 'MATCH (d:Disease {name:$name})-[:acompany_with]->(n:Disease) RETURN DISTINCT d.name AS disease, n.name AS companion ORDER BY companion LIMIT $limit',
    'department-parent': 'MATCH (d:Department {name:$name})-[:belongs_to]->(n:Department) RETURN DISTINCT d.name AS department, n.name AS parent ORDER BY parent LIMIT $limit',
    'description': 'MATCH (d:Disease {name:$name}) RETURN d.name AS disease, d.desc AS description, d.cause AS cause, d.prevent AS prevention LIMIT $limit',
    'schema': 'MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS quantity ORDER BY quantity DESC LIMIT $limit',
    'relations': 'MATCH (a)-[r]->(b) RETURN labels(a) AS source, type(r) AS relation, labels(b) AS target, count(*) AS quantity ORDER BY quantity DESC LIMIT $limit',
    'neighbors': 'MATCH (n {name:$name})-[r]-(m) RETURN labels(n) AS entity_labels, n.name AS entity, type(r) AS relation, startNode(r).name AS source, endNode(r).name AS target, labels(m) AS neighbor_labels, m.name AS neighbor ORDER BY relation, neighbor LIMIT $limit',
    'drugs': 'MATCH (d:Disease {name:$name})-[r:command_drug|recommand_drug]->(n:Drug) RETURN DISTINCT d.name AS disease, type(r) AS relation, n.name AS drug ORDER BY relation, drug LIMIT $limit',
    'symptoms': 'MATCH (d:Disease {name:$name})-[:has_symptom]->(n:Symptom) RETURN DISTINCT d.name AS disease, n.name AS symptom ORDER BY symptom LIMIT $limit',
    'checks': 'MATCH (d:Disease {name:$name})-[:need_check]->(n:Check) RETURN DISTINCT d.name AS disease, n.name AS check ORDER BY check LIMIT $limit',
    'foods': 'MATCH (d:Disease {name:$name})-[r:recommand_eat|do_eat|no_eat]->(n:Food) RETURN DISTINCT d.name AS disease, type(r) AS relation, n.name AS food ORDER BY relation, food LIMIT $limit',
    'diseases': 'MATCH (d:Disease)-[:has_symptom]->(n:Symptom {name:$name}) RETURN DISTINCT n.name AS symptom, d.name AS disease ORDER BY disease LIMIT $limit',
    'departments': 'MATCH (d:Disease {name:$name})-[:belongs_to]->(n:Department) RETURN DISTINCT d.name AS disease, n.name AS department ORDER BY department LIMIT $limit',
    'producers': 'MATCH (p:Producer)-[:drugs_of]->(n:Drug {name:$name}) RETURN DISTINCT p.name AS producer, n.name AS drug ORDER BY producer LIMIT $limit',
}


def make_query(operation, name=None, limit=20):
    if operation not in QUERIES:
        raise ValueError('未知查询类型')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ValueError('limit 必须在 1 到 1000 之间')
    parameters = {'limit': limit}
    if operation not in ('schema', 'relations'):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('该查询需要 --name 实体名称')
        parameters['name'] = name.strip()
    return QUERIES[operation], parameters


def run_query(operation, name=None, limit=20):
    query, parameters = make_query(operation, name, limit)
    driver = GraphDatabase.driver(**get_neo4j_config())
    try:
        with driver.session(database=get_database(), default_access_mode='READ') as session:
            records = session.run(query, parameters).data()
        return {'operation': operation, 'cypher': query, 'parameters': parameters,
                'source': 'neo4j', 'returned_count': len(records), 'limit': limit,
                'records': records}
    finally:
        driver.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description='展示 Cypher、参数与真实 Neo4j 查询记录')
    parser.add_argument('operation', choices=QUERIES)
    parser.add_argument('--name')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--plan-only', action='store_true', help='只展示查询计划，不连接数据库')
    args = parser.parse_args(argv)
    try:
        if args.plan_only:
            query, parameters = make_query(args.operation, args.name, args.limit)
            result = {'mode':'plan_only', 'cypher':query, 'parameters':parameters}
        else:
            result = run_query(args.operation, args.name, args.limit)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
