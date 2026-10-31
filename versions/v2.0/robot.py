# 导⼊3个⼦任务的功能函数
from question_classifier_19 import *
from question_parser import *
from answer_search import *
from chat_gpt import *
import time


# 红蜘蛛机器⼈综合问答类
class Red_Spider:
    def __init__(self, flag=None, model_path='./pretrain_model'):
        # 1: 问题分类器
        print('初始化QuestionClassifier......')
        self.classifier = QuestionClassifier()
        
        # 2: 问题解析器
        print('初始化QuestionParser......')
        self.parser = QuestionParser()
        
        # 3: 答案搜索器
        print('初始化AnswerSearcher......')
        self.searcher = AnswerSearcher()
        
        # 4: ⽣成回复模块
        print('初始化ChatGPT......')
        self.generator = ChatGPT(flag, model_path) if flag else None
        
        # 开幕词设置
        self.answer = '您好, 我是红蜘蛛AI助理, 希望可以帮到您, 祝您身体安康, 快乐常伴~'
        print(self.answer)
        
    def chat_main(self, sentence):
        # 1: ⾸先进⾏问题分类, 如果⽆法分类到症状, ⻝品, 药品相关问题上, 则直接返回客套话
        res_classify = self.classifier.classify(sentence)
        
        # 如果无法生成则转交给大模型
        if not res_classify:
            return self.generator.chat(sentence) if self.generator else '未查到对应图谱信息。'
        
        # print('res_classify: ', res_classify)
        # 2: 对分类后的问题进⾏解析, 组装出neo4j查询语句
        res_sql = self.parser.parser_main(res_classify)
        
        # 如果无法生成转交给大模型
        if not res_sql:
            return self.generator.chat(sentence) if self.generator else '未查到对应图谱信息。'

        # print('res_sql: ', res_sql)
        # 3: 利⽤查询语句, 直接调⽤答案搜索器查询neo4j, 得到最终答案
        final_answers = self.searcher.search_main(res_sql)
        
        # ⽆法查询到相关答案, 则返回客套话; 否则将若⼲答案分⾏返回
        if not final_answers:
            return self.generator.chat(sentence) if self.generator else '未查到对应图谱信息。'
        else:
            return '\n'.join(final_answers)

    
if __name__ == '__main__':
    # 实例化红蜘蛛机器⼈
    print('初始化AI红蜘蛛......')
    start_time = time.time()
    import os
    flag = os.environ.get('LLM_BACKEND')
    
    model_path = './pretrain_model'
    red_spider = Red_Spider(flag, model_path)
    end_time = time.time()
    print('初始化耗时{}s'.format(end_time - start_time))
    
    # ⽆限循环多轮对话
    while True:
        question = input('⽤户:')
        if question == 'Q' or question == 'q':
            break
        
        answer = red_spider.chat_main(question)
        print('AI红蜘蛛:', answer)
        print('\n')
