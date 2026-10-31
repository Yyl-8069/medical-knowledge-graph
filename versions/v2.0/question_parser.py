class QuestionParser:
    # 构建实体节点
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)
                    
        return entity_dict
    
    # 解析主函数并组装Cypher语句
        # 解析主函数
    def parser_main(self, res_classify):
        args = res_classify.get('args', {})
        entity_dict = self.build_entitydict(args)
        question_types = res_classify.get('question_types', [])
        
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            
            # 按照不同的分类结果, 组装不同的cypher查询语句
            if question_type == 'disease_symptom':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'symptom_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('symptom'))
            
            elif question_type == 'disease_cause':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_acompany':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_not_food':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_do_food':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'food_not_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('food'))
            
            elif question_type == 'food_do_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('food'))
            
            elif question_type == 'disease_food':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_drug':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'drug_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('drug'))
            
            elif question_type == 'disease_check':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'check_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('check'))
            
            elif question_type == 'disease_prevent':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_lasttime':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_cureway':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_cureprob':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
           
            elif question_type == 'disease_easyget':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            elif question_type == 'disease_desc':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            
            if question_type == 'disease_belong':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))
            if sql:
                sql_['sql'] = sql
                sqls.append(sql_)
                
        return sqls
    
    # 针对不同的问题, 分开进行处理
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []
        
        # 查询问句
        sql = []
        
        # 查询疾病有哪些症状
        if question_type == 'disease_symptom':
            sql = [{'query': 'MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            
            # 查询疾病建议吃的东⻄
        elif question_type == 'disease_food':
            sql = [{'query': 'MATCH (m:Disease)-[r:recommand_eat]->(n:Food) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病常⽤药品

        # 查询疾病的防御措施
        elif question_type == 'disease_prevent':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.prevent', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的原因
        elif question_type == 'disease_cause':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.cause', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的持续时间
        elif question_type == 'disease_lasttime':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.cure_lasttime', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的治愈概率
        elif question_type == 'disease_cureprob':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.cured_prob', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的治疗⽅式
        elif question_type == 'disease_cureway':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.cure_way', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的易发⼈群
        elif question_type == 'disease_easyget':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.easy_get', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的相关介绍
        elif question_type == 'disease_desc':
            sql = [{'query': 'MATCH (m:Disease) where m.name = $name return m.name, m.desc', 'parameters': {'name': i}} for i in entities]
        
        # 查询症状会导致哪些疾病
        elif question_type == 'symptom_disease':
            sql = [{'query': 'MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病的并发症
        elif question_type == 'disease_acompany':
            sql1 = [{'query': 'MATCH (m:Disease)-[r:acompany_with]->(n:Disease) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql2 = [{'query': 'MATCH (m:Disease)-[r:acompany_with]->(n:Disease) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql = sql1 + sql2
        
        # 查询疾病的忌⼝
        elif question_type == 'disease_not_food':
            sql = [{'query': 'MATCH (m:Disease)-[r:no_eat]->(n:Food) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病建议吃的东⻄
        elif question_type == 'disease_do_food':
            sql = [{'query': 'MATCH (m:Disease)-[r:do_eat]->(n:Food) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 已知忌⼝查疾病
        elif question_type == 'food_not_disease':
            sql = [{'query': 'MATCH (m:Disease)-[r:no_eat]->(n:Food) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 已知推荐查疾病
        elif question_type == 'food_do_disease':
            sql = [{'query': 'MATCH (m:Disease)-[r:do_eat]->(n:Food) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 查询疾病常⽤药品
        elif question_type == 'disease_drug':
            sql1 = [{'query': 'MATCH (m:Disease)-[r:command_drug]->(n:Drug) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql2 = [{'query': 'MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql = sql1 + sql2
        
        # 已知药品查询能够治疗的疾病
        elif question_type == 'drug_disease':
            sql1 = [{'query': 'MATCH (m:Disease)-[r:command_drug]->(n:Drug) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql2 = [{'query': 'MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            sql = sql1 + sql2
        
        # 查询疾病应该进⾏的检查
        elif question_type == 'disease_check':
            sql = [{'query': 'MATCH (m:Disease)-[r:need_check]->(n:Check) where m.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        
        # 已知检查查询疾病
        elif question_type == 'check_disease':
            sql = [{'query': 'MATCH (m:Disease)-[r:need_check]->(n:Check) where n.name = $name                 return m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
            
        if question_type == 'disease_belong':
            sql = [{'query': 'MATCH (m:Disease)-[r:belongs_to]->(n:Department) WHERE m.name=$name RETURN m.name, r.name, n.name', 'parameters': {'name': i}} for i in entities]
        return sql
    
if __name__ == '__main__':
    qp = QuestionParser()
    print(qp)