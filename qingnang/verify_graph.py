"""Read-only verification of every source entity and relationship name pair."""
import json
from neo4j import GraphDatabase
from config import get_neo4j_config, get_database
from build_medicalgraph import MedicalGraph


def verify_graph(graph=None):
    graph=graph or MedicalGraph()
    values=graph.read_nodes()
    report={'nodes':[],'relations':[],'complete':True,
            'scope':'source entity names and relation endpoint names; duplicates and property equality not checked'}
    with GraphDatabase.driver(**get_neo4j_config()) as driver:
        with driver.session(database=get_database(),default_access_mode='READ') as session:
            for label,names in zip(('Drug','Food','Check','Department','Producer','Symptom','Disease'),values[:7]):
                missing=0
                rows=sorted(names)
                for offset in range(0,len(rows),1000):
                    row=session.run(f'UNWIND $names AS name WITH name WHERE NOT EXISTS {{ MATCH (n:{label} {{name:name}}) }} RETURN count(*) AS missing',names=rows[offset:offset+1000]).single()
                    missing+=row['missing']
                report['nodes'].append({'label':label,'expected':len(names),'missing':missing})
                report['complete']=report['complete'] and missing==0
            for start,end,index,relation in graph.RELATIONS:
                rows=[list(edge) for edge in sorted({tuple(edge) for edge in values[index]})]
                missing=0
                for offset in range(0,len(rows),1000):
                    row=session.run(f'UNWIND $edges AS edge WITH edge WHERE NOT EXISTS {{ MATCH (a:{start} {{name:edge[0]}})-[:{relation}]->(b:{end} {{name:edge[1]}}) }} RETURN count(*) AS missing',edges=rows[offset:offset+1000]).single()
                    missing+=row['missing']
                report['relations'].append({'start':start,'relation':relation,'end':end,'expected':len(rows),'missing':missing})
                report['complete']=report['complete'] and missing==0
    return report


if __name__=='__main__':
    report=verify_graph()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['complete'] else 1)
