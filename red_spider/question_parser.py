class QuestionPaser:
    RELATIONS = {
        'disease_symptom': ('has_symptom', 'Symptom'),
        'disease_food': ('recommand_eat', 'Food'),
        'disease_drug': ('recommand_drug', 'Drug'),
    }

    def build_entitydict(self, args):
        result = {}
        for name, types in args.items():
            for type_ in types:
                result.setdefault(type_, []).append(name)
        return result

    def parser_main(self, res_classify):
        entities = self.build_entitydict(res_classify.get('args', {}))
        result = []
        for question_type in res_classify.get('question_types', []):
            queries = self.sql_transfer(question_type, entities.get('disease'))
            if queries:
                result.append({'question_type': question_type, 'sql': queries})
        return result

    def sql_transfer(self, question_type, entities):
        if not entities or question_type not in self.RELATIONS:
            return []
        relation, label = self.RELATIONS[question_type]
        return [{
            'query': f'MATCH (m:Disease)-[r:{relation}]->(n:{label}) '
                     'WHERE m.name = $name RETURN m.name, r.name, n.name',
            'parameters': {'name': name},
        } for name in entities]
