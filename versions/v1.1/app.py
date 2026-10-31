from question_classifier import *
from question_parser import *
from answer_search import *
import time

# 服务框架使⽤Flask, 导⼊⼯具包
from flask import Flask
from flask import request

app = Flask(__name__)

# 导⼊发送http请求的requests⼯具
import requests

# 红蜘蛛机器⼈综合问答类
class Red_Spider:
    def __init__(self):
        # 1: 问题分类器
        self.classifier = QuestionClassifier()
        # 2: 问题解析器
        self.parser = QuestionParser()
        # 3: 答案搜索器
        self.searcher = AnswerSearcher()
        
    def chat_main(self, sentence):
        answer = '您好, 我是红蜘蛛AI助理, 希望可以帮到您, 祝您身体安康, 快乐常伴~'
        
        # 1: ⾸先进⾏问题分类, 如果⽆法分类到症状, ⻝品, 药品相关问题上, 则直接返回客套话
        res_classify = self.classifier.classify(sentence)
        if not res_classify:
            return answer
        
        # print('res_classify: ', res_classify)
        # 2: 对分类后的问题进⾏解析, 组装出neo4j查询语句
        res_sql = self.parser.parser_main(res_classify)
        
        # print('res_sql: ', res_sql)
        # 3: 利⽤查询语句, 直接调⽤答案搜索器查询neo4j, 得到最终答案
        final_answers = self.searcher.search_main(res_sql)
        
        # ⽆法查询到相关答案, 则返回客套话; 否则将若⼲答案分⾏返回
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)
        
        
# 实例化红蜘蛛机器⼈
start_time = time.time()
red_spider = Red_Spider()
end_time = time.time()
print('cost time: ', end_time - start_time)
print('红蜘蛛AI机器⼈初始化完毕.')

# 设定传智红蜘蛛AI服务的路由和请求⽅法      
@app.route('/v1/main_server/', methods=["POST"])
def main_server():
    # 接收来⾃请求⽅发送的服务字段
    uid = request.form['uid']
    text = request.form['text']
    
    # 调⽤红蜘蛛AI机器⼈执⾏查询与回复
    answer = red_spider.chat_main(text)
    
    return answer
