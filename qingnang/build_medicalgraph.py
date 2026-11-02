import json
from neo4j import GraphDatabase
from pathlib import Path
import argparse
from config import get_neo4j_config, get_database

class MedicalGraph:
    RELATIONS = [
            ('Disease','Check',8,'need_check'), ('Disease','Food',9,'recommand_eat'),
            ('Disease','Food',10,'no_eat'), ('Disease','Food',11,'do_eat'),
            ('Department','Department',12,'belongs_to'), ('Disease','Drug',13,'command_drug'),
            ('Producer','Drug',14,'drugs_of'), ('Disease','Drug',15,'recommand_drug'),
            ('Disease','Symptom',16,'has_symptom'), ('Disease','Disease',17,'acompany_with'),
            ('Disease','Department',18,'belongs_to'),
        ]

    def __init__(self, data_path=None):
        self.data_path = Path(data_path) if data_path else Path(__file__).resolve().parent / 'data/medical.json'

    # 读取文件的函数操作
    def read_nodes(self):
        # 七类节点，疾病详情保存为属性。
        drugs = []  # 药品
        foods = []  # 食物
        diseases = []  # 疾病
        symptoms = []  # 症状
        checks = []  # 检查
        departments = []  # 科室
        producers = []  # 药品⼤类
        disease_infos = []  # 疾病信息
        
        # 创建节点关系
        rels_recommandeat = []
        rels_recommanddrug = []
        rels_symptom = []
        rels_department = []
        rels_noteat = []
        rels_doeat = []
        rels_commanddrug = []
        rels_check = []
        rels_drug_producer = []
        rels_acompany = []
        rels_category = []
        
        count = 0
        for data in self.data_path.read_text(encoding='utf-8').splitlines():
            disease_dict = {}
            count += 1

            data_json = json.loads(data)
            disease = data_json['name']
            diseases.append(disease)
            disease_dict['name'] = disease
            disease_dict['desc'] = ''
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''
            
            # 症状名
            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])
                    
            # 公司名
            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])
                    
            # 描述
            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']
                
            # 预防措施
            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']
            
            # 病因    
            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']
            
            # 易得概率
            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']
            
            # 易得人群
            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']
            
            # 科室   
            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                # 当列表中科室名为1
                if len(cure_department) == 1:
                    rels_category.append([disease, cure_department[0]])
                # 当列表中科室名为2（大小包含关系）
                if len(cure_department) == 2:
                    big = cure_department[0]
                    small = cure_department[1]
                    
                    rels_department.append([small, big])
                    rels_category.append([disease, small])
                    
                disease_dict['cure_department'] = cure_department
                departments += cure_department
             
            # 治疗方法
            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']
            
            # 治疗周期
            if 'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']
            
            # 治疗概率
            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']
            
            # 常见药品
            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    rels_commanddrug.append([disease, drug])
                drugs += common_drug
            
            # 推荐药品
            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])
                    
            # 不可以吃的食物, 一定要吃的食物, 推荐吃的食物
            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for _not in not_eat:
                    rels_noteat.append([disease, _not])
                
                foods += not_eat
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do])
                
                foods += do_eat
                recommand_eat = data_json['recommand_eat']
                
                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])
                foods += recommand_eat
                
            # 检查
            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])
                checks += check
                
            # 药品详情
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer
                
            disease_infos.append(disease_dict)
            
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), \
            disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commanddrug, \
                rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category
            

    def create_graphnodes_and_graphrels(self, complete_existing=False):
        values = self.read_nodes()
        drugs, foods, checks, departments, producers, symptoms, diseases = values[:7]
        groups = [('Drug', drugs), ('Food', foods), ('Check', checks), ('Department', departments), ('Producer', producers), ('Symptom', symptoms), ('Disease', diseases)]
        relations = self.RELATIONS
        with GraphDatabase.driver(**get_neo4j_config()) as driver:
            driver.verify_connectivity()
            with driver.session(database=get_database()) as session:
                duplicate_labels = set()
                for label, _ in groups:
                    duplicates = session.run(
                        f'MATCH (n:{label}) WITH n.name AS name, count(*) AS total '
                        'WHERE name IS NOT NULL AND total > 1 RETURN name, total LIMIT 5'
                    ).data()
                    if duplicates and complete_existing:
                        duplicate_labels.add(label)
                        print(f'{label}: 保留已有同名节点，新关系使用固定端点')
                    elif duplicates:
                        raise ValueError(f'{label} 存在同名重复节点，停止导入，未开始写入：{duplicates}')
                for label,names in groups:
                    if label not in duplicate_labels:
                        session.run(f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.name IS UNIQUE').consume()
                    session.run(f'UNWIND $names AS name MERGE (n:{label} {{name:name}})', names=sorted(names)).consume()
                    print(label,len(names))
                # Existing duplicate nodes stay; completion updates one fixed endpoint per name.
                for offset in range(0,len(values[7]),500):
                    property_query = 'UNWIND $rows AS row '
                    if complete_existing:
                        property_query += 'CALL { WITH row MATCH (n:Disease {name:row.name}) RETURN n ORDER BY elementId(n) LIMIT 1 } SET n += row'
                    else:
                        property_query += 'MATCH (n:Disease {name:row.name}) SET n += row'
                    session.run(property_query,rows=values[7][offset:offset+500]).consume()
                for start,end,index,relation in relations:
                    edges=[list(edge) for edge in sorted({tuple(edge) for edge in values[index]})]
                    for offset in range(0,len(edges),1000):
                        query = 'UNWIND $edges AS edge '
                        if complete_existing:
                            query += (f'CALL {{ WITH edge MATCH (a:{start} {{name:edge[0]}}) RETURN a ORDER BY elementId(a) LIMIT 1 }} '
                                      f'CALL {{ WITH edge MATCH (b:{end} {{name:edge[1]}}) RETURN b ORDER BY elementId(b) LIMIT 1 }} ')
                        else:
                            query += f'MATCH (a:{start} {{name:edge[0]}}) MATCH (b:{end} {{name:edge[1]}}) '
                        query += f'MERGE (a)-[r:{relation}]->(b) SET r.name=$title'
                        session.run(query,edges=edges[offset:offset+1000],title=relation).consume()
                    print(start,relation,end,len(edges),'candidate edges')

def main(argv=None):
    parser = argparse.ArgumentParser(description='七类节点、十一组关系：默认仅预览数据')
    parser.add_argument('--execute', action='store_true', help='显式启用写入')
    parser.add_argument('--data', type=Path)
    parser.add_argument('--complete-existing', action='store_true', help='保留旧库同名节点，固定端点补齐全量数据；需同时指定 --execute')
    args = parser.parse_args(argv)
    if args.complete_existing and not args.execute:
        parser.error('--complete-existing 需要同时指定 --execute')
    graph = MedicalGraph(args.data)
    if args.execute:
        graph.create_graphnodes_and_graphrels(complete_existing=args.complete_existing)
    else:
        values = graph.read_nodes()
        nodes = dict(zip(('Drug','Food','Check','Department','Producer','Symptom','Disease'), map(len, values[:7])))
        edges = [{'start': start, 'relation': relation, 'end': end,
                  'unique_candidates': len({tuple(edge) for edge in values[index]})}
                 for start, end, index, relation in graph.RELATIONS]
        print(json.dumps({'mode': 'preview_only', 'nodes': nodes, 'relations': edges}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
