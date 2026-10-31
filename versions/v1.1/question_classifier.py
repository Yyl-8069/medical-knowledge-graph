from pathlib import Path
import os
import ahocorasick
import time

# 实现问题分类的主类代码
class QuestionClassifier:
    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.disease_path = os.path.join(cur_dir, 'dict/disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict/department.txt')
        self.check_path = os.path.join(cur_dir, 'dict/check.txt') 
        self.drug_path = os.path.join(cur_dir, 'dict/drug.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict/symptom.txt')
        self.producer_path = os.path.join(cur_dir, 'dict/producer.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        
        # 加载特征词
        self.disease_words = [i.strip() for i in Path(self.disease_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.drug_words = [i.strip() for i in Path(self.drug_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.food_words = [i.strip() for i in Path(self.food_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.symptom_words = [i.strip() for i in Path(self.symptom_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.department_words = [i.strip() for i in Path(self.department_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.check_words = [i.strip() for i in Path(self.check_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.producer_words = [i.strip() for i in Path(self.producer_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        self.region_words = set(self.disease_words + self.drug_words + self.food_words +self.symptom_words + self.department_words + \
            self.check_words + self.producer_words)    
        
        self.deny_words = [i.strip() for i in Path(self.deny_path).read_text(encoding='utf-8').splitlines() if i.strip()]
        
        # 构造领域actree, 可以加速关键词匹配查找
        self.region_tree = self.build_actree(list(self.region_words))
        # 构造词典
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
        
        # 问句疑问词, 当前版本仅⽀持症状, ⻝品, 药品, 病因, 并发症, 预防, 持续时间, 治疗⽅法, 治愈概率, 检查, 治疗⼿段, 易感⼈群, 科室归属的查询
        self.symptom_request = ['症状', '表征', '现象', '症候', '表现']
        self.food_request = ['饮⻝', '饮⽤', '吃', '⻝', '伙⻝', '膳⻝', '喝','菜', '忌⼝', '补品', '保健品', '⻝谱', '菜谱', '⻝⽤', '⻝物']
        self.drug_request = ['药', '药品', '⽤药', '胶囊', '⼝服液', '炎⽚']
        self.cause_request = ['原因','成因', '为什么', '怎么会', '怎样才', '咋样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会', '会导致', '会造成']
        self.acompany_request = ['并发症', '并发', '⼀起发⽣', '⼀并发⽣', '⼀起出现', '⼀并出现', '⼀同发⽣', '⼀同出现', '伴随发⽣', '伴随', '共现']
        self.prevent_request = ['预防', '防范', '抵制', '抵御', '防⽌','躲避','逃避','避开', '免得', '逃开', '避开', '避掉', '躲开', '躲掉', \
            '绕开', '怎样才能不', '怎么才能不', '咋样才能不', '咋才能不', '如何才能不', '怎样才不', '怎么才不', '咋样才不', '咋才不', \
                '如何才不', '怎样才可以不', 
        '怎么才可以不', '咋样才可以不', '咋才可以不', '如何可以不', '怎样才可不', '怎么才可不', '咋样才可不', '咋才可不', '如何可不']
        self.lasttime_request = ['周期', '痊愈期', '康复', '恢复', '缓解', '摆脱', '控制', '稳定', '持续', '最佳', '何时', '多久', '多⻓时间', \
            '多少时间', '⼏天', '⼏年', '多少天', '多少⼩时', '⼏个⼩时', '多少年']
        self.cureway_request = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治⽅式', '疗法', '咋治', '怎么办', '咋办', '咋治']
        self.cureprob_request = ['多⼤概率能治好', '多⼤⼏率能治好', '治好希望⼤么', '⼏率', '⼏成', '⽐例', '可能性', '能治', '可治', '可以治', '可以医']
        self.check_request = ['检查', '检查项⽬', '查出', '检查', '测出', '试出']
        self.cure_request = ['治疗什么', '治啥', '治疗措施', '策略', '辅助治疗', '治疗', '治疗啥', '医治啥', '治愈啥', '主治啥', \
            '主治什么', '有什么⽤', '有何⽤', '⽤处', '⽤途', '有什么好处', '有什么益处', '有何益处', '⽤来', '⽤来做啥', '⽤来作甚', '需要', '要']
        self.easyget_request = ['易感⼈群', '容易感染', '易发⼈群', '什么⼈', '哪些⼈', '感染', '染上', '得上']
        self.belong_request = ['属于什么科', '属于', '什么科', '科室', '哪个科']
        
        print('model init finished......')
        
    # 分类主函数
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        
        data['args'] = medical_dict
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'
        
        question_types = []
        
        # 疾病与症状关系
        if self.check_word_in_sentence(self.symptom_request, question) and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)
            
        # 症状与疾病关系
        if self.check_word_in_sentence(self.symptom_request, question) and ('symptom' in types):
            question_type = 'symptom_disease'
            question_types.append(question_type)
            
        # 疾病的原因
        if self.check_word_in_sentence(self.cause_request, question) and ('disease' in types):
            question_type = 'disease_cause'
            question_types.append(question_type)
            
        # 并发症
        if self.check_word_in_sentence(self.acompany_request, question) and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)
            
        # 依据疾病推荐⻝品
        if self.check_word_in_sentence(self.food_request, question) and 'disease' in types:
            deny_status = self.check_word_in_sentence(self.deny_words, question)
            
            # 疾病不能吃食物
            if deny_status:
                question_type = 'disease_not_food'
                question_types.append(question_type)
            # 疾病要吃的食物
            else:
                question_type = 'disease_do_food'
                question_types.append(question_type)
                
        # 食物与疾病的关系
        if self.check_word_in_sentence(self.food_request + self.cure_request, question) and 'food' in types:
            deny_status = self.check_word_in_sentence(self.deny_words, question)
            
            # 食物与疾病忌吃关系
            if deny_status:
                question_type = 'food_not_disease'
                question_types.append(question_type)
            # 食物与疾病宜吃关系
            else:
                question_type = 'food_do_disease'
                question_types.append(question_type)
                
        # 根据疾病推荐药品
        if self.check_word_in_sentence(self.drug_request, question) and ('disease' in types):
            question_type = 'disease_drug'
            question_types.append(question_type)
            
        # 药品能治疗什么疾病
        if self.check_word_in_sentence(self.cure_request, question) and 'drug' in types:
            question_type = 'drug_disease'
            question_types.append(question_type)
            
        # 疾病应该接受什么检查项目
        if self.check_word_in_sentence(self.check_request, question) and 'disease' in types:
            question_type = 'disease_check'
            question_types.append(question_type)
            
        # 检查项目对应那种疾病
        if self.check_word_in_sentence(self.check_request + self.cure_request, question) and 'check' in types:
            question_type = 'check_disease'
            question_types.append(question_type)
            
        # 疾病如何预防
        if self.check_word_in_sentence(self.prevent_request, question) and 'disease' in types:
            question_type = 'disease_prevent'
            question_types.append(question_type)
        
        # 疾病医疗周期
        if self.check_word_in_sentence(self.lasttime_request, question) and 'disease' in types:
            question_type = 'disease_lasttime'
            question_types.append(question_type)
            
        # 疾病治疗⽅式
        if self.check_word_in_sentence(self.cureway_request, question) and 'disease' in types:
            question_type = 'disease_cureway'
            question_types.append(question_type)
            
        # 疾病治愈概率
        if self.check_word_in_sentence(self.cureprob_request, question) and 'disease' in types:
            question_type = 'disease_cureprob'
            question_types.append(question_type)
            
        # 疾病易感染⼈群
        if self.check_word_in_sentence(self.easyget_request, question) and 'disease' in types :
            question_type = 'disease_easyget'
            question_types.append(question_type)
            
        # 如果没有查到相关的外部查询信息, 则将该疾病与症状的信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['symptom_disease']
            
        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']
            
        if self.check_word_in_sentence(self.belong_request, question) and 'disease' in types:
            question_types = [item for item in question_types if item != 'disease_desc']
            question_types.append('disease_belong')

        # 将多个分类结果进⾏合并处理, 组装成⼀个字典
        data['question_types'] = question_types
        
        return data
    
    # 构造关键词对应的节点类型
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
                
            # 检查是否有科室关键词
            if word in self.department_words:
                word_dict[word].append('department')
                
            # 检查是否有检查关键词
            if word in self.check_words:
                word_dict[word].append('check')
                
            # 检查是否有⽣产商关键词
            if word in self.producer_words:
                word_dict[word].append('producer')
            
        return word_dict
    
    # 构造actree进行加速过滤
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
            
        actree.make_automaton()
        return actree
    
    # 问句检查的函数
    def check_medical(self, question):
        region_words = []
        
        # 利⽤actree加速查询关键词
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
        final_words = {i: self.wdtype_dict.get(i) for i in final_words}
        
        return final_words
    
    # 基于特征词进⾏问句检测, 并进⾏问句类型的规则分类
    def check_word_in_sentence(self, words, sent):
        for word in words:
            if word in sent:
                return True
        return False
    
if __name__ == '__main__':
    qc = QuestionClassifier()
    while True:
        question = input('input an question: ')
        data = qc.classify(question)
        print(data)
