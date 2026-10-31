from pathlib import Path
import os
import ahocorasick
from importlib import import_module
import numpy as np
import torch
import time
# from bert.models.bert import *
import onnxruntime as ort

UNK, PAD, CLS = '[UNK]', '[PAD]', '[CLS]'

class QuestionClassifier:
    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 特征词路径
        self.disease_path = os.path.join(cur_dir, './dict/disease.txt')
        self.department_path = os.path.join(cur_dir, './dict/department.txt')
        self.check_path = os.path.join(cur_dir, './dict/check.txt')
        self.producer_path = os.path.join(cur_dir, './dict/producer.txt')
        self.drug_path = os.path.join(cur_dir, './dict/drug.txt')
        self.food_path = os.path.join(cur_dir, './dict/food.txt')
        self.symptom_path = os.path.join(cur_dir, './dict/symptom.txt')
        self.deny_path = os.path.join(cur_dir, './dict/deny.txt')
        
        # 加载特征词
        self.disease_words = [i.strip() for i in Path(self.disease_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.drug_words = [i.strip() for i in Path(self.drug_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.food_words = [i.strip() for i in Path(self.food_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.symptom_words = [i.strip() for i in Path(self.symptom_path).read_text(encoding='utf-8').splitlines() if i.strip()] 
        self.department_words = [i.strip() for i in Path(self.department_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.check_words = [i.strip() for i in Path(self.check_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.producer_words = [i.strip() for i in Path(self.producer_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        
        self.region_words = set(self.disease_words + self.drug_words + self.food_words + self.symptom_words + self.department_words + \
            self.check_words + self.producer_words)
        
        self.deny_words = [i.strip() for i in Path(self.deny_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        
        # 构建领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        
        # 构建词典
        if hasattr(self, 'disease_words'):
            self.disease_words = set(self.disease_words)
        if hasattr(self, 'drug_words'):
            self.drug_words = set(self.drug_words)
        if hasattr(self, 'food_words'):
            self.food_words = set(self.food_words)
        if hasattr(self, 'symptom_words'):
            self.symptom_words = set(self.symptom_words)
        if hasattr(self, 'department_words'):
            self.department_words = set(self.department_words)
        if hasattr(self, 'check_words'):
            self.check_words = set(self.check_words)
        if hasattr(self, 'producer_words'):
            self.producer_words = set(self.producer_words)
        self.wdtype_dict = self.build_wdtype_dict()
        self.CLS = ['[CLS]']
        self.pad_size = 32
        
        # 初始化BERT模型，用于意图识别
        self.init_bert()
        
    def init_bert(self):
        model_name = 'bert'
        x = import_module('bert.models.' + model_name)
        config = x.Config('red_spider')
        
        self.model = x.Model(config).to(config.device)
        
        self.model.load_state_dict(torch.load(config.save_path, map_location=config.device, weights_only=True))
        
        
        self.tokenizer = config.tokenizer
        print('model init finished ......')
        
    def question_class(self, question):
        self.model.eval()
        tokens = self.CLS + self.tokenizer.tokenize(question)
        ids = self.tokenizer.convert_tokens_to_ids(tokens)[:self.pad_size]
        mask = [1] * len(ids) + [0] * (self.pad_size - len(ids))
        ids += [0] * (self.pad_size - len(ids))
        device = next(self.model.parameters()).device
        ids = torch.tensor([ids], device=device)
        mask = torch.tensor([mask], device=device)
        with torch.inference_mode():
            output = self.model(ids, mask, torch.zeros_like(ids))
        return int(output.argmax(dim=1).item())

    # 分类主函数
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        intent = self.question_class(question)
        data['args'] = medical_dict
        
        # 收集问句当中所设计到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'
        
        question_types = []
        
        # 0: disease_drug
        if intent == 0 and ('disease' in types):
            question_type = 'disease_drug'
            question_types.append(question_type)

        # 1: disease_do_food
        if intent == 1 and ('disease' in types):
            question_type = 'disease_do_food'
            question_types.append(question_type)

        # 2: disease_not_food
        if intent == 2 and ('disease' in types):
            question_type = 'disease_not_food'
            question_types.append(question_type)

        # 3: food_do_disease
        if intent == 3 and ('food' in types):
            question_type = 'food_do_disease'
            question_types.append(question_type)

        # 4: food_not_disease
        if intent == 4 and ('food' in types):
            question_type = 'food_not_disease'
            question_types.append(question_type)

        # 5: disease_symptom
        if intent == 5 and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)

        # 6: disease_cureway
        if intent == 6 and ('disease' in types):
            question_type = 'disease_cureway'
            question_types.append(question_type)

        # 7: disease_prevent
        if intent == 7 and ('disease' in types):
            question_type = 'disease_prevent'
            question_types.append(question_type)

        # 8: disease_ckeck
        if intent == 8 and ('disease' in types):
            question_type = 'disease_check'
            question_types.append(question_type)

        # 9: drug_disease
        if intent == 9 and ('drug' in types):
            question_type = 'drug_disease'
            question_types.append(question_type)

        # 10: check_disease
        if intent == 10 and ('check' in types):
            question_type = 'check_disease'
            question_types.append(question_type)

        # 11: disease_lasttime
        if intent == 11 and ('disease' in types):
            question_type = 'disease_lasttime'
            question_types.append(question_type)

        # 12: disease_cureprob
        if intent == 12 and ('disease' in types):
            question_type = 'disease_cureprob'
            question_types.append(question_type)

        # 13: disease_easyget
        if intent == 13 and ('disease' in types):
            question_type = 'disease_easyget'
            question_types.append(question_type)

        # 14: disease_not_easyget
        if intent == 14 and ('disease' in types):
            question_type = 'disease_not_easyget'
            question_types.append(question_type)

        # 15: disease_acompany
        if intent == 15 and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)

        # 16: disease_cause
        if intent == 16 and ('disease' in types):
            question_type = 'disease_cause'
            question_types.append(question_type)

        # 17: symptom_disease
        if intent == 17 and ('symptom' in types):
            question_type = 'symptom_disease'
            question_types.append(question_type)

        # 18: disease_belong
        if intent == 18 and ('disease' in types):
            question_type = 'disease_belong'
            question_types.append(question_type)
            
        # 若没有查到相关的外部查询信息，那么则将疾病的描述信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['disease_symptom']
            
        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types
        
        return data
    
    # 构建关键词对应节点类型
    def build_wdtype_dict(self):
        word_dict = dict()
        for word in self.region_words:
            word_dict[word] = []
            # 检查是否有疾病关键词
            if word in self.disease_words:
                word_dict[word].append('disease')
                
            # 检查是否有药品关键词
            if word in self.drug_words:
                word_dict[word].append('drug')
                
            # 检查是否有食品关键词
            if word in self.food_words:
                word_dict[word].append('food')
                
            # 检查是否有症状关键词
            if word in self.symptom_words:
                word_dict[word].append('symptom')
                
            # 检查是否有科室关键词
            if word in self.department_words:
                word_dict[word].append('department')
            
            # 检查是否有检查关键词
            if word in self.check_words:
                word_dict[word].append('check')
                
            # 检查是否有生产商关键词
            if word in self.producer_words:
                word_dict[word].append('producer')
        
        return word_dict
    
    # 构建actree加速过滤
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree
    
    # 问句检查
    def check_medical(self, question):
        region_words = []
        for i in self.region_tree.iter(question):
            word = i[1][1]
            region_words.append(word)
            
        stop_words = []
        for word1 in region_words:
            for word2 in region_words:
                if word1 in word2 and word1 != word2:
                    stop_words.append(word1)
                    
        final_words = [i for i in region_words if i not in stop_words]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_words}
        
        return final_dict
    
    # 基于特征词进行问句检测，并进行问句类型的规则分类
    def check_words(self, words, sent):
        for word in words:
            if word in sent:
                return True
        return False
    

if __name__ == '__main__':
    qc = QuestionClassifier()
    while True:
        question = input('input an question:')
        data = qc.classify(question)
        print(data)
