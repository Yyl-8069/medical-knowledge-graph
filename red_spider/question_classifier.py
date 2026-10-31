import os
from pathlib import Path
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        #　特征词路径
        self.disease_path = os.path.join(cur_dir, './dict/disease.txt')
        self.drug_path = os.path.join(cur_dir, './dict/drug.txt')
        self.food_path = os.path.join(cur_dir, './dict/food.txt')
        self.symptom_path = os.path.join(cur_dir, './dict/symptom.txt')
        # # 加载特征词
        self.disease_words= {i.strip() for i in Path(self.disease_path).read_text(encoding='utf-8').splitlines() if i.strip()}
        self.drug_words= {i.strip() for i in Path(self.drug_path).read_text(encoding='utf-8').splitlines() if i.strip()}
        self.food_words= {i.strip() for i in Path(self.food_path).read_text(encoding='utf-8').splitlines() if i.strip()}
        self.symptom_words= {i.strip() for i in Path(self.symptom_path).read_text(encoding='utf-8').splitlines() if i.strip()}
        self.region_words = self.disease_words | self.drug_words | self.food_words | self.symptom_words
        
        # 构建actree, 可加速关键词匹配查找
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        
        # 问句疑问词, V1.0版本仅⽀持症状, ⻝品, 药品的查询.
        self.symptom_request = ['症状', '表征', '现象', '症候', '表现']
        self.food_request = ['饮⻝', '饮⽤', '吃', '⻝', '伙⻝', '膳⻝', '喝', '菜' ,'忌⼝', 
        '补品', '保健品', '⻝谱', '菜谱', '⻝⽤', '⻝物','补品']
        self.drug_request = ['药', '药品', '⽤药', '胶囊', '⼝服液', '炎⽚']
        
        print('model init finished ......')
        
    # 分类主函数
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        
        data['args'] = medical_dict
        # 收集问句中所涉及的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'
        
        question_types = []
        
        # 症状
        if self.check_words(self.symptom_request, question) and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)
        
        # 推荐⻝品
        if self.check_words(self.food_request, question) and ('disease' in types):
            question_type = 'disease_food'
            question_types.append(question_type)
        
        # 推荐药品
        if self.check_words(self.drug_request, question) and ('disease' in types):
            question_type = 'disease_drug'
            question_types.append(question_type)
        
        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['disease_symptom']
            
        # 将多个分类结果进行并行处理, 组成一个字典
        data['question_types'] = question_types
        
        return data
    
    # 构建关键词对应的节点类型
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
                
            # 检查是否有⻝品关键词
            if word in self.food_words:
                word_dict[word].append('food')
                
            # 检查是否有症状关键词
            if word in self.symptom_words:
                word_dict[word].append('symptom')
                
        return word_dict
    
    # 构造actree加速过滤
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree
    
    # 问句检查
    def check_medical(self, question):
        region_words = []
        
        # 利⽤AcTree加速查询关键词
        for i in self.region_tree.iter(question):
            word = i[1][1]
            region_words.append(word)
            
        stop_words = []
        # ⼦词进⼊停⽤词表
        for word1 in region_words:
            for word2 in region_words:
                if word1 in word2 and word1 != word2:
                    stop_words.append(word1)
                    
        final_words = [i for i in region_words if i not in stop_words]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_words}
        
        return final_dict
    
    # 基于特征词进⾏问句检测, 并进⾏问句类型的规则分类
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
