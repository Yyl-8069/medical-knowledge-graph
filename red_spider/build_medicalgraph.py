import json
from pathlib import Path
from neo4j import GraphDatabase
from config import get_neo4j_config


class MedicalGraph:
    def __init__(self, data_path=None):
        self.data_path = Path(data_path) if data_path else Path(__file__).resolve().parent / 'data' / 'medical.json'

    # 读取⽂件
    def read_nodes(self):
        # 共4类节点
        drugs = [] # 药品
        foods = [] # ⻝物
        diseases = [] # 疾病
        symptoms = [] # 症状
        
        # 构建节点实体关系
        rels_recommandeat = [] # 疾病-推荐吃⻝物关系
        rels_recommanddrug = [] # 疾病-推荐药品关系
        rels_symptom = [] # 疾病-症状关系
        
        count = 0
        for data in self.data_path.read_text(encoding='utf-8').splitlines():
            count += 1
            if count % 1000 == 0:
                print('count = ', count)
                
            data_json = json.loads(data)
            disease = data_json['name']
            diseases.append(disease)
            
            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])
                    
            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])
            if 'recommand_eat' in data_json:
                recommand_eat = data_json['recommand_eat']
                
                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])
                foods += recommand_eat
                
        return set(drugs), set(foods), set(symptoms), set(diseases), rels_recommandeat, rels_recommanddrug, rels_symptom

    def create_graphnodes_and_graphrels(self):
        drugs, foods, symptoms, diseases, food_edges, drug_edges, symptom_edges = self.read_nodes()
        with GraphDatabase.driver(**get_neo4j_config()) as driver:
            driver.verify_connectivity()
            with driver.session() as session:
                for label, names in [('Disease', diseases), ('Drug', drugs), ('Food', foods), ('Symptom', symptoms)]:
                    # Labels are fixed by this script; all data values are parameters.
                    session.run(f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.name IS UNIQUE').consume()
                    session.run(f'UNWIND $names AS name MERGE (n:{label} {{name: name}})', names=sorted(names)).consume()
                    print(f'{label}: {len(names)}')
                for target, edges, relation, title in [
                    ('Food', food_edges, 'recommand_eat', '推荐食谱'),
                    ('Drug', drug_edges, 'recommand_drug', '推荐药品'),
                    ('Symptom', symptom_edges, 'has_symptom', '症状'),
                ]:
                    rows = [list(edge) for edge in sorted({tuple(edge) for edge in edges})]
                    for offset in range(0, len(rows), 1000):
                        session.run(
                            f'UNWIND $edges AS edge MATCH (a:Disease {{name: edge[0]}}) '
                            f'MATCH (b:{target} {{name: edge[1]}}) '
                            f'MERGE (a)-[r:{relation}]->(b) SET r.name = $title',
                            edges=rows[offset:offset + 1000], title=title,
                        ).consume()
                    print(f'{relation}: {len(rows)}')


if __name__ == '__main__':
    MedicalGraph().create_graphnodes_and_graphrels()
