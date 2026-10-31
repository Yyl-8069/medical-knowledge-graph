from neo4j import GraphDatabase
from config import get_neo4j_config


class AnswerSearcher:
    def __init__(self):
        self.num_limit = 10
        self.driver = GraphDatabase.driver(**get_neo4j_config())

    def close(self):
        self.driver.close()

    def search_main(self, sqls):
        final_answers = []
        if not sqls:
            return final_answers
        with self.driver.session() as session:
            for sql_ in sqls:
                answers = []
                for query in sql_['sql']:
                    answers.extend(session.run(query['query'], query['parameters']).data())
                answer = self.answer_prettify(sql_['question_type'], answers)
                if answer:
                    final_answers.append(answer)
        return final_answers

    # 根据对应的qustion_type, 调⽤相应的回复模板
    def answer_prettify(self, question_type, answers):
        final_answer = ''
        if not answers:
            return ''
        
        if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括:{1}'.format(subject, ';'.join(sorted(set(desc))[:self.num_limit]))
        
        elif question_type == 'disease_food':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}推荐⻝谱包括:{1}'.format(subject, ';'.join(sorted(set(desc))[:self.num_limit]))
        
        elif question_type == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}推荐的药品包括:{1}'.format(subject, ';'.join(sorted(set(desc))[:self.num_limit]))
        return final_answer
