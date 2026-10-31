# coding: utf-8
import random
import re
from collections import defaultdict

# 定义类别和对应的标签
categories = {
    0: "disease_drug",
    1: "disease_do_food",
    2: "disease_not_food",
    3: "food_do_disease",
    4: "food_not_disease",
    5: "disease_symptom",
    6: "disease_cureway",
    7: "disease_prevent",
    8: "disease_ckeck",
    9: "drug_disease",
    10: "check_disease",
    11: "disease_lasttime",
    12: "disease_cureprob",
    13: "disease_easyget",
    14: "disease_not_easyget",
    15: "disease_acompany",
    16: "disease_cause",
    17: "symptom_disease",
    18: "disease_belong"
}

# 扩展词汇库 - 添加更多常见药物别名和商品名
diseases = ["感冒", "流感", "高血压", "糖尿病", "心脏病", "肺炎", "胃炎", "哮喘", "关节炎", "骨质疏松", 
           "抑郁症", "焦虑症", "湿疹", "牛皮癣", "白内障", "青光眼", "肝炎", "肾炎", "甲状腺功能亢进", "贫血",
           "偏头痛", "支气管炎", "胃溃疡", "肝硬化", "胰腺炎", "前列腺炎", "宫颈炎", "乳腺增生", "腰椎间盘突出", "骨质疏松",
           "癫痫", "帕金森", "阿尔茨海默病", "红斑狼疮", "类风湿关节炎", "痛风", "过敏性鼻炎", "中耳炎", "牙周炎", "白内障",
           "冠心病", "心肌梗塞", "脑卒中", "肺气肿", "慢性肾炎", "肝硬化", "胰腺癌", "乳腺癌", "肺癌", "结肠癌"]

foods = ["苹果", "香蕉", "橙子", "菠菜", "胡萝卜", "鸡肉", "鱼肉", "牛奶", "鸡蛋", "豆腐", 
        "米饭", "面条", "面包", "巧克力", "咖啡", "茶", "蜂蜜", "大蒜", "姜", "核桃",
        "西红柿", "黄瓜", "土豆", "牛肉", "猪肉", "虾", "蟹", "酸奶", "奶酪", "燕麦",
        "玉米", "红薯", "蘑菇", "海带", "紫菜", "花生", "杏仁", "腰果", "葡萄", "西瓜",
        "菠萝", "芒果", "荔枝", "龙眼", "柚子", "柠檬", "苦瓜", "茄子", "芹菜", "洋葱"]

# 添加更多常见药物名称和商品名
drugs = ["阿司匹林", "布洛芬", "青霉素", "头孢", "胰岛素", "降压药", "降糖药", "抗抑郁药", "抗生素", "止痛药",
        "消炎药", "维生素C", "钙片", "铁剂", "中药", "草药", "眼药水", "药膏", "喷雾剂", "胶囊",
        "阿莫西林", "罗红霉素", "左氧氟沙星", "甲硝唑", "奥美拉唑", "雷尼替丁", "二甲双胍", "格列本脲", "阿托伐他汀", "辛伐他汀",
        "氨氯地平", "缬沙坦", "氯沙坦", "普萘洛尔", "美托洛尔", "地高辛", "华法林", "氯吡格雷", "阿司匹林肠溶片", "对乙酰氨基酚",
        "扑热息痛", "布洛芬缓释胶囊", "头孢克肟", "阿奇霉素", "莫西沙星", "环丙沙星", "氟康唑", "伊曲康唑", "甲钴胺", "维生素B12",
        "感冒灵", "板蓝根", "999感冒冲剂", "白加黑", "泰诺", "感康", "芬必得", "芬乃屯", "安乃近", "复方甘草片",
        "云南白药", "创可贴", "碘伏", "红霉素软膏", "皮炎平", "达克宁", "马应龙", "六味地黄丸", "牛黄解毒片", "板蓝根颗粒"]

symptoms = ["头痛", "发热", "咳嗽", "流鼻涕", "喉咙痛", "胸痛", "呼吸困难", "乏力", "恶心", "呕吐",
           "腹泻", "便秘", "皮疹", "瘙痒", "关节疼痛", "视力模糊", "心悸", "头晕", "失眠", "食欲不振",
           "耳鸣", "鼻塞", "打喷嚏", "肌肉酸痛", "背痛", "腹痛", "腹胀", "消化不良", "尿频", "尿急",
           "血尿", "水肿", "体重下降", "多汗", "皮肤发黄", "口腔溃疡", "牙龈出血", "脱发", "记忆力减退", "注意力不集中",
           "心慌", "气短", "胸闷", "手脚麻木", "关节肿胀", "皮肤干燥", "眼睛干涩", "口干", "口苦", "口臭"]

checks = ["血常规", "尿常规", "X光", "CT扫描", "MRI", "心电图", "超声检查", "血压测量", "血糖测试", "肝功能测试",
         "肾功能测试", "甲状腺功能测试", "胃镜检查", "肠镜检查", "骨密度检测", "眼科检查", "听力测试", "过敏测试", "基因检测", "病理活检",
         "血脂检查", "心肌酶谱", "肿瘤标志物", "凝血功能", "电解质检查", "免疫功能检查", "脑电图", "肌电图", "肺功能检查", "宫颈涂片检查",
         "乳腺钼靶", "前列腺特异性抗原", "幽门螺杆菌检测", "乙肝五项", "艾滋病检测", "梅毒检测", "结核菌素试验", "碳13呼气试验", "动态心电图", "动态血压监测"]

cure_ways = ["药物治疗", "手术治疗", "物理治疗", "心理治疗", "饮食调理", "运动疗法", "中医针灸", "按摩推拿", "放射治疗", "化疗",
            "免疫治疗", "靶向治疗", "介入治疗", "康复训练", "氧疗", "透析", "移植", "激光治疗", "冷冻治疗", "热疗",
            "生物反馈", "认知行为疗法", "职业治疗", "言语治疗", "音乐治疗", "艺术治疗", "水疗", "磁疗", "电疗", "光疗"]

departments = ["内科", "外科", "儿科", "妇科", "眼科", "耳鼻喉科", "皮肤科", "神经科", "心血管科", "消化科",
              "内分泌科", "呼吸科", "骨科", "泌尿科", "精神科", "肿瘤科", "急诊科", "康复科", "中医科", "全科",
              "感染科", "风湿免疫科", "血液科", "肾内科", "肝病科", "乳腺科", "甲状腺科", "疼痛科", "老年病科", "营养科",
              "心理科", "整形外科", "烧伤科", "创伤科", "血管外科", "胸外科", "脑外科", "手外科", "显微外科", "器官移植科"]

# 添加更多自然语言表达方式
expressions = {
    "ask": ["请问", "想问一下", "咨询一下", "麻烦问一下", "不知道", "想了解", "请教一下", "帮忙解答", "求教", "咨询",
           "好奇", "不太明白", "有点困惑", "想确认一下", "请问医生"],
    "symptom_desc": ["最近总是", "这几天", "近期", "这一阵子", "感觉", "出现", "有了", "开始有", "老是", "经常",
                    "一直", "时不时", "偶尔", "突然", "忽然"],
    "time_desc": ["已经持续了", "大概有", "将近", "差不多", "大约", "快有", "已经有", "持续了", "差不多有", "拖了"],
    "severity": ["有点", "比较", "非常", "特别", "极其", "相当", "十分", "格外", "异常", "严重",
                "轻微", "稍微", "不太", "略微", "有点点"],
    "uncertainty": ["可能", "好像", "似乎", "觉得", "怀疑", "担心", "怕是", "猜测", "估计", "推测",
                   "不确定", "不太确定", "有点拿不准", "不太肯定", "隐约感觉"],
    "purpose": ["该怎么办", "怎么处理", "如何解决", "有什么办法", "应该怎么做", "需要注意什么", "该如何是好", "有什么建议", "怎么应对",
               "应该怎么选择", "哪个更好", "有什么区别", "怎么判断", "怎么确认"],
    "greetings": ["医生您好，", "大夫，", "医生，", "您好，", "医生你好，", "大夫您好，", "您好医生，", ""],
    "endings": ["谢谢！", "感谢！", "拜托了！", "麻烦您了！", "请问有什么建议吗？", "希望能得到您的指导。", "期待您的回复。", "非常感谢！", "",
               "请指教！", "麻烦您解答一下。", "希望能得到专业意见。"],
    "filler_words": ["那个", "就是", "嗯", "啊", "呃", "然后", "其实", "实际上", "说实话", "说起来",
                    "对了", "顺便问一下", "另外", "还有", "还有一点"]
}

# 添加一些常见的口语表达和干扰词
common_phrases = [
    "我有点担心", "心里没底", "不知道怎么办", "挺着急的", "心里慌", "特别焦虑", "晚上睡不好",
    "工作受影响", "生活被打乱", "家人也很担心", "朋友建议我来咨询", "网上查了查", "看了些资料",
    "之前去过医院", "医生给开了点药", "但效果不太明显", "想再咨询一下", "希望能得到专业意见",
    "这种情况常见吗", "需要立即处理吗", "会不会有什么严重后果", "有什么需要注意的",
    "饮食上要注意什么", "生活习惯需要调整吗", "需要休息多久", "还能正常工作吗",
    "想确认一下", "想了解一下", "想请教一下", "想问清楚", "想搞明白",
    "不太确定", "有点疑惑", "有点拿不准", "不太清楚", "不太明白"
]

# 常见问题句式模板
question_patterns = {
    "drug_disease": [
        "吃{drug}能治疗{disease}吗",
        "服用{drug}可以治{disease}吗",
        "{drug}对{disease}有效吗",
        "{drug}能不能治疗{disease}",
        "用{drug}可以处理{disease}吗",
        "{drug}适合{disease}患者吗",
        "{disease}能用{drug}治疗吗",
        "{disease}患者可以吃{drug}吗",
        "吃{drug}能缓解{disease}的症状吗",
        "治疗{disease}可以用{drug}吗"
    ],
    "disease_drug": [
        "{disease}应该吃什么药",
        "{disease}该用什么药物",
        "治疗{disease}需要吃哪些药",
        "{disease}吃什么药效果好",
        "{disease}患者应该服用什么药",
        "有{disease}该吃什么药",
        "得了{disease}需要用药吗",
        "{disease}用什么药能治好",
        "针对{disease}有什么推荐的药物",
        "{disease}的常用治疗药物有哪些"
    ],
    "disease_lasttime": [
        "{disease}一般多久能好",
        "{disease}需要多长时间恢复",
        "治疗{disease}需要多久",
        "{disease}一般要持续多长时间",
        "得{disease}多久能痊愈",
        "{disease}一般多久可以治愈",
        "患{disease}需要多久才能好转",
        "{disease}的治疗周期是多久",
        "得{disease}一般多久能康复",
        "治疗{disease}大概需要多长时间"
    ],
    "disease_easyget": [
        "哪些人容易得{disease}",
        "什么人容易患{disease}",
        "{disease}的高发人群有哪些",
        "哪些人群容易感染{disease}",
        "什么年龄段的人容易得{disease}",
        "什么职业的人容易得{disease}",
        "什么体质的人容易得{disease}",
        "什么情况下容易得{disease}",
        "哪些因素会增加{disease}的风险",
        "什么人是{disease}的易感人群"
    ]
}

# 生成更自然的问句，添加更多噪声和多样性
def natural_question(template, disease="", food="", drug="", symptom="", check="", cure_way="", department=""):
    # 随机选择表达方式
    ask = random.choice(expressions["ask"])
    symptom_desc = random.choice(expressions["symptom_desc"])
    time_desc = random.choice(expressions["time_desc"])
    severity = random.choice(expressions["severity"])
    uncertainty = random.choice(expressions["uncertainty"])
    purpose = random.choice(expressions["purpose"])
    
    # 随机添加时间描述
    time_period = f"{time_desc}{random.randint(1, 30)}天了" if random.random() > 0.5 else ""
    
    # 随机添加严重程度描述
    severity_desc = f"{severity}严重" if random.random() > 0.5 else ""
    
    # 随机添加填充词
    filler = random.choice(expressions["filler_words"]) if random.random() > 0.7 else ""
    
    # 随机添加常见短语
    common_phrase = random.choice(common_phrases) if random.random() > 0.6 else ""
    
    # 应用模板
    question = template.format(
        ask=ask,
        symptom_desc=symptom_desc,
        time_desc=time_desc,
        time_period=time_period,
        severity=severity,
        severity_desc=severity_desc,
        uncertainty=uncertainty,
        purpose=purpose,
        filler=filler,
        common_phrase=common_phrase,
        disease=disease,
        food=food,
        drug=drug,
        symptom=symptom,
        check=check,
        cure_way=cure_way,
        department=department
    )
    
    # 随机添加问候语
    greeting = random.choice(expressions["greetings"])
    question = greeting + question
    
    # 随机添加结束语
    if random.random() > 0.7:
        ending = random.choice(expressions["endings"])
        question = question + ending
    
    # 随机添加一些口语化表达
    if random.random() > 0.8:
        oral_expressions = ["呢", "呀", "吧", "哦", "嘛", "啦", "哈", "哟", "诶", "哎"]
        question = question + random.choice(oral_expressions)
    
    # 随机添加一些错别字或拼音
    if random.random() > 0.9:
        typo_words = {
            "请问": "亲问", "咨询": "资询", "医生": "医森", "治疗": "治了", 
            "症状": "证状", "检查": "检察", "药物": "要物", "食物": "食务",
            "能": "恩", "可以": "可已", "应该": "因该", "什么": "森么",
            "怎么": "肿么", "没有": "木有", "特别": "特呗", "非常": "灰常"
        }
        for correct, typo in typo_words.items():
            if correct in question and random.random() > 0.7:
                question = question.replace(correct, typo)
    
    # 随机添加一些不完整的句子
    if random.random() > 0.95:
        incomplete_endings = ["...", "。。.", "——", "~~~", "。。。"]
        question = question + random.choice(incomplete_endings)
    
    return question

# 生成每个类别的问题
def generate_questions():
    questions = []
    
    # 0: disease_drug - 有疾病该吃什么药物
    for i in range(1000):
        disease = random.choice(diseases)
        drug = random.choice(drugs)
        templates = [
            # 增强版模板 - 添加更多贴近实际的表达
            "{ask}{common_phrase}{filler}{disease}应该怎么处理？{purpose}",
            "{uncertainty}{common_phrase}{filler}有了{disease}，{ask}该怎么办？",
            "{symptom_desc}{disease}的情况{time_period}，{ask}有什么建议？",
            "被诊断出{disease}，{ask}{common_phrase}{filler}接下来该怎么做？",
            "{disease}患者{ask}{common_phrase}{filler}日常需要注意什么？",
            "{ask}针对{disease}，{common_phrase}{filler}有什么应对方法？",
            "家人有{disease}，{ask}{common_phrase}{filler}该怎么帮助他？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}该怎么控制？",
            "{ask}{disease}发作时{common_phrase}{filler}应该怎么应对？",
            "医生给了些建议治疗{disease}，{ask}{common_phrase}{filler}这些合适吗？",
            # 新增贴近实际的模板
            "{disease}应该吃什么药",
            "{disease}该用什么药物",
            "治疗{disease}需要吃哪些药",
            "{disease}吃什么药效果好",
            "{disease}患者应该服用什么药",
            "有{disease}该吃什么药",
            "得了{disease}需要用药吗",
            "{disease}用什么药能治好",
            "针对{disease}有什么推荐的药物",
            "{disease}的常用治疗药物有哪些"
        ]
        question = natural_question(random.choice(templates), disease=disease, drug=drug)
        questions.append((question, 0))
    
    # 1: disease_do_food - 疾病该吃什么食物
    for i in range(1000):
        disease = random.choice(diseases)
        food = random.choice(foods)
        templates = [
            "{ask}{common_phrase}{filler}{disease}在日常饮食上应该注意什么？{purpose}",
            "有{disease}，{ask}{common_phrase}{filler}平时吃什么比较好？",
            "{disease}患者{ask}{common_phrase}{filler}有哪些饮食方面的建议？",
            "{symptom_desc}{disease}{time_period}，{ask}{common_phrase}{filler}饮食上怎么安排？",
            "{ask}对{disease}有帮助的{common_phrase}{filler}有哪些？",
            "家人得{disease}了，{ask}{common_phrase}{filler}我应该准备些什么？",
            "{disease}恢复期{ask}{common_phrase}{filler}吃什么有助于好转？",
            "{ask}{disease}患者需要{common_phrase}{filler}补充些什么？",
            "查出{disease}，{ask}{common_phrase}{filler}我的饮食应该怎么调整？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}有什么可以推荐的？",
            # 新增贴近实际的模板
            "{disease}适合吃什么",
            "{disease}应该多吃什么",
            "有{disease}能吃{food}吗",
            "{disease}患者适合食用{food}吗",
            "{disease}可以吃{food}吗",
            "{disease}适合吃{food}吗",
            "{disease}应该避免吃什么",
            "{disease}患者不能吃什么",
            "得{disease}应该注意饮食吗",
            "{disease}饮食上有什么建议"
        ]
        question = natural_question(random.choice(templates), disease=disease, food=food)
        questions.append((question, 1))
    
    # 2: disease_not_food - 疾病不该吃什么食物
    for i in range(1000):
        disease = random.choice(diseases)
        food = random.choice(foods)
        templates = [
            "{ask}{common_phrase}{filler}{disease}有哪些需要避免的？",
            "有{disease}，{ask}{common_phrase}{filler}不能接触什么？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}有什么需要留意的？",
            "{ask}对{disease}不利的{common_phrase}{filler}有哪些？",
            "患有{disease}，{ask}{common_phrase}{filler}需要避开什么？",
            "{symptom_desc}{disease}的情况{time_period}，{ask}{common_phrase}{filler}有什么不能碰的？",
            "{ask}{disease}患者应该{common_phrase}{filler}限制些什么？",
            "诊断出{disease}，{ask}{common_phrase}{filler}我的日常有哪些需要避免的？",
            "{disease}急性期{ask}{common_phrase}{filler}应该注意避开什么？",
            "{ask}{disease}与什么{common_phrase}{filler}不太合适？",
            # 新增贴近实际的模板
            "{disease}不能吃什么",
            "{disease}患者应该避免什么食物",
            "有{disease}不能吃{food}吗",
            "{disease}患者不能吃{food}吗",
            "{disease}忌口有哪些",
            "{disease}不能吃{food}吗",
            "得{disease}应该避免什么",
            "{disease}不能吃哪些东西",
            "{disease}饮食禁忌是什么",
            "{disease}有哪些饮食禁忌"
        ]
        question = natural_question(random.choice(templates), disease=disease, food=food)
        questions.append((question, 2))
    
    # 3: food_do_disease - 已知食物有利于疾病
    for i in range(1000):
        food = random.choice(foods)
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}接触{food}对{disease}有影响吗？",
            "{food}对{disease}患者{common_phrase}{filler}有帮助吗？{purpose}",
            "{ask}{disease}可以{common_phrase}{filler}多接触{food}吗？",
            "听说{food}对{disease}有好处，{ask}{common_phrase}{filler}这是真的吗？",
            "{disease}患者{ask}{common_phrase}{filler}适合接触{food}吗？",
            "{ask}接触{food}能{common_phrase}{filler}改善{disease}的情况吗？",
            "{food}对{disease}的恢复{common_phrase}{filler}有促进作用吗？",
            "{ask}{disease}患者经常{common_phrase}{filler}接触{food}好不好？",
            "家人有{disease}，{ask}{common_phrase}{filler}我应该多让他接触{food}吗？",
            "{ask}{food}中的成分对{disease}{common_phrase}{filler}有什么作用？",
            # 新增贴近实际的模板
            "{food}对{disease}有好处吗",
            "吃{food}能帮助{disease}恢复吗",
            "{disease}可以多吃{food}吗",
            "{food}有助于{disease}吗",
            "有{disease}适合吃{food}吗",
            "{disease}患者吃{food}有帮助吗",
            "吃{food}对{disease}有影响吗",
            "{food}对{disease}有什么好处",
            "得{disease}应该多吃{food}吗",
            "{disease}适合食用{food}吗"
        ]
        question = natural_question(random.choice(templates), disease=disease, food=food)
        questions.append((question, 3))
    
    # 4: food_not_disease - 已知食物不利于疾病
    for i in range(1000):
        food = random.choice(foods)
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}接触{food}对{disease}有影响吗？",
            "{disease}患者{ask}{common_phrase}{filler}可以接触{food}吗？",
            "{ask}{food}会{common_phrase}{filler}加重{disease}的情况吗？",
            "听说{food}对{disease}不太好，{ask}{common_phrase}{filler}这是真的吗？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}能接触{food}吗？",
            "{ask}{disease}患者接触{food}{common_phrase}{filler}有什么影响？",
            "{food}对{disease}的处理{common_phrase}{filler}有干扰吗？",
            "{ask}{disease}急性期可以{common_phrase}{filler}接触{food}吗？",
            "患有{disease}，{ask}{common_phrase}{filler}需要完全避开{food}吗？",
            "{ask}{food}中的什么成分对{disease}{common_phrase}{filler}不太合适？",
            # 新增贴近实际的模板
            "{food}对{disease}不好吗",
            "吃{food}会加重{disease}吗",
            "{disease}可以吃{food}吗",
            "{food}不利于{disease}吗",
            "有{disease}不能吃{food}吗",
            "{disease}患者吃{food}有影响吗",
            "吃{food}对{disease}有害吗",
            "{food}对{disease}有什么坏处",
            "得{disease}应该避免{food}吗",
            "{disease}不适合食用{food}吗"
        ]
        question = natural_question(random.choice(templates), disease=disease, food=food)
        questions.append((question, 4))
    
    # 5: disease_symptom - 已知的疾病会有什么症状
    for i in range(1000):
        disease = random.choice(diseases)
        symptom = random.choice(symptoms)
        templates = [
            "{ask}{common_phrase}{filler}{disease}通常有哪些表现？",
            "{uncertainty}{common_phrase}{filler}有了{disease}，{ask}会有什么情况？",
            "{disease}的常见表现有哪些？{purpose}",
            "{ask}{disease}早期会{common_phrase}{filler}有什么征兆？",
            "{symptom_desc}{symptom}，{uncertainty}{common_phrase}{filler}是{disease}吗？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}可能会出现哪些情况？",
            "{ask}{disease}的典型表现是什么？",
            "{disease}患者{ask}{common_phrase}{filler}通常会有哪些不适？",
            "{ask}{disease}发展到后期会{common_phrase}{filler}有什么表现？",
            "{disease}急性发作时{ask}{common_phrase}{filler}会有什么情况？",
            # 新增贴近实际的模板
            "{disease}有什么症状",
            "{disease}的表现有哪些",
            "得了{disease}会有什么症状",
            "{disease}有哪些典型症状",
            "{disease}早期症状是什么",
            "{disease}的常见症状有哪些",
            "有{disease}会出现什么情况",
            "{disease}患者通常有什么表现",
            "得{disease}会有什么不舒服",
            "{disease}的主要症状是什么"
        ]
        question = natural_question(random.choice(templates), disease=disease, symptom=symptom)
        questions.append((question, 5))
    
    # 6: disease_cureway - 疾病的治疗方法
    for i in range(1000):
        disease = random.choice(diseases)
        cure_way = random.choice(cure_ways)
        templates = [
            "{ask}{common_phrase}{filler}{disease}一般怎么处理？",
            "有{disease}，{ask}{common_phrase}{filler}有哪些处理方法？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}该怎么应对？",
            "{ask}{disease}的处理方式有哪些？{purpose}",
            "{disease}患者{ask}{common_phrase}{filler}通常接受什么处理？",
            "{symptom_desc}{disease}的情况{time_period}，{ask}{common_phrase}{filler}应该怎么应对？",
            "{ask}{cure_way}对{disease}{common_phrase}{filler}有效吗？",
            "{disease}晚期{ask}{common_phrase}{filler}还有办法吗？",
            "{ask}{disease}可以{common_phrase}{filler}彻底解决吗？有什么处理方法？",
            "诊断出{disease}，{ask}{common_phrase}{filler}接下来该怎么应对？",
            # 新增贴近实际的模板
            "{disease}怎么治疗",
            "{disease}的治疗方法有哪些",
            "治疗{disease}有什么办法",
            "有{disease}怎么处理",
            "{disease}有哪些治疗方案",
            "得了{disease}应该怎么治疗",
            "{disease}可以用{cure_way}治疗吗",
            "{disease}的常规治疗方法是什么",
            "{disease}的治疗手段有哪些",
            "{disease}应该怎么处理"
        ]
        question = natural_question(random.choice(templates), disease=disease, cure_way=cure_way)
        questions.append((question, 6))
    
    # 7: disease_prevent - 疾病该如何预防
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}如何避免{disease}？",
            "{ask}{common_phrase}{filler}怎样降低{disease}的风险？",
            "担心会有{disease}，{ask}{common_phrase}{filler}该怎么预防？",
            "{disease}{ask}{common_phrase}{filler}有什么预防方法？",
            "{ask}日常生活中如何{common_phrase}{filler}防止{disease}？",
            "家族有{disease}病史，{ask}{common_phrase}{filler}我该怎么注意？",
            "{ask}{disease}的高危人群应该{common_phrase}{filler}如何预防？",
            "{ask}预防{disease}{common_phrase}{filler}需要注意什么？",
            "{disease}的预防措施有哪些？{purpose}",
            "{ask}有没有预防{disease}{common_phrase}{filler}的方法？",
            # 新增贴近实际的模板
            "{disease}怎么预防",
            "如何预防{disease}",
            "{disease}的预防方法有哪些",
            "预防{disease}应该注意什么",
            "怎样避免得{disease}",
            "怎么防止{disease}",
            "{disease}有哪些预防措施",
            "预防{disease}的有效方法",
            "容易得{disease}怎么预防",
            "怎么降低{disease}的风险"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 7))
    
    # 8: disease_ckeck - 疾病需要检查的项目
    for i in range(1000):
        disease = random.choice(diseases)
        check = random.choice(checks)
        templates = [
            "{ask}{common_phrase}{filler}怀疑{disease}需要做什么？",
            "{uncertainty}{common_phrase}{filler}有了{disease}，{ask}应该做哪些？",
            "{disease}{ask}{common_phrase}{filler}通常需要做哪些？",
            "{symptom_desc}{disease}的情况{time_period}，{ask}{common_phrase}{filler}该做什么确认？",
            "{ask}{check}能{common_phrase}{filler}查出{disease}吗？",
            "诊断{disease}{ask}{common_phrase}{filler}需要哪些项目？",
            "{ask}{disease}的常规{common_phrase}{filler}有哪些？",
            "{disease}复查{ask}{common_phrase}{filler}需要做哪些？",
            "{ask}{disease}早期{common_phrase}{filler}应该做什么？",
            "{disease}患者{ask}{common_phrase}{filler}需要定期做哪些？",
            # 新增贴近实际的模板
            "{disease}需要做什么检查",
            "检查{disease}需要做哪些项目",
            "诊断{disease}需要什么检查",
            "怀疑{disease}应该做什么检查",
            "有{disease}需要检查什么",
            "{disease}应该做哪些检查",
            "确诊{disease}需要什么检查",
            "{disease}的常规检查项目有哪些",
            "检查{disease}需要多少钱",
            "{disease}需要定期检查什么"
        ]
        question = natural_question(random.choice(templates), disease=disease, check=check)
        questions.append((question, 8))
    
    # 9: drug_disease - 已知药物能治疗什么疾病
    for i in range(1000):
        drug = random.choice(drugs)
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{drug}是针对什么的？",
            "{drug}{ask}{common_phrase}{filler}主要用于哪些情况？",
            "{ask}使用{drug}能{common_phrase}{filler}处理什么？",
            "医生给了{drug}，{ask}{common_phrase}{filler}这个是针对什么的？",
            "{ask}{drug}的适用{common_phrase}{filler}有哪些？",
            "{drug}对哪些情况{common_phrase}{filler}有效？{purpose}",
            "{ask}{disease}可以{common_phrase}{filler}使用{drug}吗？",
            "{drug}{ask}{common_phrase}{filler}有什么效果？",
            "{ask}{drug}是{common_phrase}{filler}处方类的吗？主要用于什么？",
            "{drug}的作用是什么？{ask}{common_phrase}{filler}能处理{disease}吗？",
            # 重点增强 - 添加更多贴近实际的表达
            "吃{drug}能治疗{disease}吗",
            "服用{drug}可以治{disease}吗",
            "{drug}对{disease}有效吗",
            "{drug}能不能治疗{disease}",
            "用{drug}可以处理{disease}吗",
            "{drug}适合{disease}患者吗",
            "{disease}能用{drug}治疗吗",
            "{disease}患者可以吃{drug}吗",
            "吃{drug}能缓解{disease}的症状吗",
            "治疗{disease}可以用{drug}吗",
            # 更多变化
            "吃{drug}对{disease}有用吗",
            "{drug}能治{disease}吗",
            "吃{drug}可以治疗{disease}吗",
            "有{disease}能吃{drug}吗",
            "{disease}吃{drug}有效吗",
            "吃{drug}能改善{disease}吗",
            "吃{drug}对{disease}有帮助吗",
            "吃{drug}能治{disease}吗",
            "{drug}对{disease}的疗效如何",
            "吃{drug}能治好{disease}吗"
        ]
        question = natural_question(random.choice(templates), disease=disease, drug=drug)
        questions.append((question, 9))
    
    # 10: check_disease - 检查的项目能得出是什么疾病
    for i in range(1000):
        check = random.choice(checks)
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{check}能发现哪些？",
            "{check}不正常{ask}{common_phrase}{filler}可能是什么？",
            "{ask}做{check}能{common_phrase}{filler}确认{disease}吗？",
            "{check}结果有问题，{ask}{common_phrase}{filler}可能是什么情况？",
            "{ask}{check}主要用于{common_phrase}{filler}筛查哪些？",
            "{check}显示有情况，{ask}{common_phrase}{filler}会是什么？",
            "{ask}{disease}可以通过{check}{common_phrase}{filler}确认吗？",
            "{check}{ask}{common_phrase}{filler}能发现早期的{disease}吗？",
            "{ask}{check}在哪些情况的{common_phrase}{filler}确认中有价值？",
            "体检{check}不正常，{ask}{common_phrase}{filler}可能是什么健康问题？",
            # 新增贴近实际的模板
            "{check}能检查出{disease}吗",
            "做{check}能查出{disease}吗",
            "{check}可以诊断{disease}吗",
            "怀疑{disease}需要做{check}吗",
            "{check}结果异常可能是什么病",
            "做{check}能确定{disease}吗",
            "{disease}需要做{check}检查吗",
            "确诊{disease}需要做{check}吗",
            "{check}对{disease}的诊断有帮助吗",
            "{disease}的{check}指标是什么"
        ]
        question = natural_question(random.choice(templates), disease=disease, check=check)
        questions.append((question, 10))
    
    # 11: disease_lasttime - 疾病医疗周期
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{disease}一般需要处理多久？",
            "有{disease}，{ask}{common_phrase}{filler}多久能好转？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}还需要应对多长时间？",
            "{ask}{disease}的处理{common_phrase}{filler}周期是多久？",
            "{disease}患者{ask}{common_phrase}{filler}通常需要应对多长时间？",
            "{ask}{disease}能{common_phrase}{filler}短期解决吗？还是需要长期应对？",
            "{disease}恢复{ask}{common_phrase}{filler}需要多长时间？",
            "{ask}{disease}的处理是{common_phrase}{filler}短期还是长期的？",
            "{disease}急性期{ask}{common_phrase}{filler}一般持续多久？",
            "{ask}{disease}缓解后还需要{common_phrase}{filler}继续应对吗？要多久？",
            # 新增贴近实际的模板
            "{disease}一般多久能好",
            "{disease}需要多长时间恢复",
            "治疗{disease}需要多久",
            "{disease}一般要持续多长时间",
            "得{disease}多久能痊愈",
            "{disease}一般多久可以治愈",
            "患{disease}需要多久才能好转",
            "{disease}的治疗周期是多久",
            "得{disease}一般多久能康复",
            "治疗{disease}大概需要多长时间"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 11))
    
    # 12: disease_cureprob - 疾病治愈的可能性
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{disease}能解决吗？",
            "{disease}{ask}{common_phrase}{filler}的解决率有多高？",
            "{ask}{disease}患者能{common_phrase}{filler}完全恢复吗？",
            "{disease}晚期{ask}{common_phrase}{filler}还有希望吗？",
            "{ask}{disease}的预后{common_phrase}{filler}怎么样？",
            "{disease}{time_period}了，{ask}{common_phrase}{filler}还能处理好吗？",
            "{ask}{disease}是不是{common_phrase}{filler}难以应对的？",
            "{disease}患者{ask}{common_phrase}{filler}的生存情况是多少？",
            "{ask}{disease}处理后{common_phrase}{filler}容易再次出现吗？",
            "{disease}{ask}{common_phrase}{filler}有多大的解决可能性？",
            # 新增贴近实际的模板
            "{disease}能治好吗",
            "{disease}的治愈率是多少",
            "得了{disease}能完全康复吗",
            "{disease}可以根治吗",
            "{disease}的治愈可能性大吗",
            "治疗{disease}的成功率高吗",
            "{disease}复发率高吗",
            "{disease}的预后怎么样",
            "得了{disease}能活多久",
            "{disease}的生存率是多少"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 12))
    
    # 13: disease_easyget - 疾病的易得人群
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}什么人容易有{disease}？",
            "{disease}{ask}{common_phrase}{filler}的高危人群有哪些？",
            "{ask}哪些人容易{disease}？",
            "什么情况下{ask}{common_phrase}{filler}容易{disease}？",
            "{ask}{disease}的常见{common_phrase}{filler}人群是哪些？",
            "{disease}{ask}{common_phrase}{filler}在什么人群中多见？",
            "{ask}什么年龄段的{common_phrase}{filler}人容易{disease}？",
            "{disease}{ask}{common_phrase}{filler}有性别差异吗？哪种性别更容易？",
            "{ask}哪些职业的{common_phrase}{filler}人容易{disease}？",
            "{disease}{ask}{common_phrase}{filler}和遗传有关吗？什么样的人风险高？",
            # 新增贴近实际的模板
            "哪些人容易得{disease}",
            "什么人容易患{disease}",
            "{disease}的高发人群有哪些",
            "哪些人群容易感染{disease}",
            "什么年龄段的人容易得{disease}",
            "什么职业的人容易得{disease}",
            "什么体质的人容易得{disease}",
            "什么情况下容易得{disease}",
            "哪些因素会增加{disease}的风险",
            "什么人是{disease}的易感人群"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 13))
    
    # 14: disease_not_easyget - 疾病不易得的人群
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}什么人不容易{disease}？",
            "{ask}{common_phrase}{filler}如何降低{disease}的风险？",
            "{disease}{ask}{common_phrase}{filler}的低风险人群有哪些特征？",
            "{ask}什么生活习惯可以{common_phrase}{filler}减少{disease}的出现？",
            "{disease}{ask}{common_phrase}{filler}在什么人群中少见？",
            "{ask}怎么做才能{common_phrase}{filler}避免{disease}？",
            "{disease}{ask}{common_phrase}{filler}的保护因素有哪些？",
            "{ask}哪些人对{disease}{common_phrase}{filler}有抵抗力？",
            "{disease}{ask}{common_phrase}{filler}有没有天然抵抗力强的人群？",
            "{ask}什么饮食或生活方式可以{common_phrase}{filler}预防{disease}？",
            # 新增贴近实际的模板
            "哪些人不容易得{disease}",
            "什么人不容易患{disease}",
            "{disease}的低发人群有哪些",
            "哪些人群不容易感染{disease}",
            "什么年龄段的人不容易得{disease}",
            "什么职业的人不容易得{disease}",
            "什么体质的人不容易得{disease}",
            "如何避免得{disease}",
            "哪些习惯可以预防{disease}",
            "怎么降低{disease}的风险"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 14))
    
    # 15: disease_acompany - 疾病的并发症
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{disease}可能引起哪些其他问题？",
            "{disease}不及时处理{ask}{common_phrase}{filler}会有什么后果？",
            "{ask}{disease}会导致其他什么情况？",
            "{disease}晚期{ask}{common_phrase}{filler}会出现哪些相关问题？",
            "{ask}{disease}可能影响{common_phrase}{filler}哪些方面？",
            "{disease}{ask}{common_phrase}{filler}的常见相关问题有哪些？",
            "{ask}{disease}会引发什么严重的{common_phrase}{filler}健康问题？",
            "{disease}控制不好{ask}{common_phrase}{filler}会有什么影响？",
            "{ask}{disease}可能带来哪些{common_phrase}{filler}长期影响？",
            "{disease}{ask}{common_phrase}{filler}会损伤哪些身体功能？",
            # 新增贴近实际的模板
            "{disease}会引起什么并发症",
            "{disease}的并发症有哪些",
            "得了{disease}会引发什么病",
            "{disease}可能导致什么问题",
            "不治疗{disease}会有什么后果",
            "{disease}的常见并发症是什么",
            "患{disease}可能引发什么疾病",
            "得{disease}会带来什么其他问题",
            "{disease}会引起哪些后遗症",
            "{disease}的严重并发症有哪些"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 15))
    
    # 16: disease_cause - 疾病的病因
    for i in range(1000):
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{disease}是什么原因引起的？",
            "{ask}{common_phrase}{filler}为什么会有{disease}？",
            "{disease}{ask}{common_phrase}{filler}的起因是什么？",
            "{ask}{disease}的主要{common_phrase}{filler}致病因素有哪些？",
            "{disease}{ask}{common_phrase}{filler}和遗传有关吗？",
            "{ask}什么会导致{common_phrase}{filler}{disease}？",
            "{disease}{ask}{common_phrase}{filler}是怎么发生的？",
            "{ask}{disease}的发病{common_phrase}{filler}机制是什么？",
            "{disease}{ask}{common_phrase}{filler}与环境因素有关吗？",
            "{ask}{disease}是病毒引起的还是{common_phrase}{filler}细菌引起的？",
            # 新增贴近实际的模板
            "{disease}是怎么引起的",
            "{disease}的原因是什么",
            "得{disease}是什么原因",
            "{disease}的病因有哪些",
            "什么原因会导致{disease}",
            "{disease}是怎么得的",
            "引起{disease}的因素有哪些",
            "为什么会得{disease}",
            "{disease}的发病原因是什么",
            "导致{disease}的主要原因"
        ]
        question = natural_question(random.choice(templates), disease=disease)
        questions.append((question, 16))
    
    # 17: symptom_disease - 已知的症状与疾病的关系
    for i in range(1000):
        symptom = random.choice(symptoms)
        disease = random.choice(diseases)
        templates = [
            "{ask}{common_phrase}{filler}{symptom}可能是什么情况？",
            "{symptom_desc}{symptom}{time_period}，{ask}{common_phrase}{filler}可能是什么问题？",
            "{ask}{symptom}与哪些情况{common_phrase}{filler}有关？",
            "{symptom}{ask}{common_phrase}{filler}需要警惕什么？",
            "{ask}{symptom}是{disease}{common_phrase}{filler}的表现吗？",
            "{symptom}{severity_desc}，{ask}{common_phrase}{filler}可能是什么？",
            "{ask}什么情况会导致{common_phrase}{filler}{symptom}？",
            "{symptom_desc}{symptom}，{uncertainty}{common_phrase}{filler}是{disease}的前兆吗？",
            "{ask}{symptom}持续不退{common_phrase}{filler}可能是什么原因？",
            "{symptom}伴有其他不适{ask}{common_phrase}{filler}可能是什么情况？",
            # 新增贴近实际的模板
            "{symptom}是什么病",
            "有{symptom}可能是什么病",
            "{symptom}可能是什么疾病",
            "出现{symptom}是什么原因",
            "{symptom}可能是{disease}吗",
            "有{symptom}是不是{disease}",
            "{symptom}是{disease}的症状吗",
            "{symptom}通常是什么病",
            "出现{symptom}应该考虑什么病",
            "有{symptom}可能得了什么病"
        ]
        question = natural_question(random.choice(templates), disease=disease, symptom=symptom)
        questions.append((question, 17))
    
    # 18: disease_belong - 疾病应该要挂什么科
    for i in range(1000):
        disease = random.choice(diseases)
        department = random.choice(departments)
        templates = [
            "{ask}{common_phrase}{filler}{disease}应该看什么？",
            "{uncertainty}{common_phrase}{filler}有了{disease}，{ask}该找哪个？",
            "{disease}{ask}{common_phrase}{filler}属于哪个范畴？",
            "{ask}{disease}患者应该{common_phrase}{filler}找{department}吗？",
            "{symptom_desc}{disease}的情况{time_period}，{ask}{common_phrase}{filler}该看什么？",
            "{ask}处理{disease}应该{common_phrase}{filler}选择什么专业？",
            "{disease}{ask}{common_phrase}{filler}是看内科还是外科？",
            "{ask}{disease}应该{common_phrase}{filler}找专家还是普通？",
            "{disease}复查{ask}{common_phrase}{filler}应该找什么？",
            "{ask}{disease}需要{common_phrase}{filler}多专业会诊吗？应该先看哪个？",
            # 新增贴近实际的模板
            "{disease}应该挂什么科",
            "{disease}应该看什么科室",
            "有{disease}应该挂什么科",
            "得了{disease}应该看什么科",
            "{disease}属于什么科室",
            "{disease}应该去看哪个科",
            "看{disease}应该挂什么号",
            "得{disease}应该挂什么科",
            "{disease}应该去什么科室",
            "{disease}挂什么科比较好"
        ]
        question = natural_question(random.choice(templates), disease=disease, department=department)
        questions.append((question, 18))
    
    return questions

# 生成问题并打乱顺序
all_questions = generate_questions()
random.shuffle(all_questions)

# 保存到文件
with open("train.txt", "w", encoding="utf-8") as f:
    for question, label in all_questions:
        f.write(f"{question}\t{label}\n")

print(f"已生成 {len(all_questions)} 条问题，并保存到 train.txt 文件中")


# 这是class.txt文件中19大类型
# disease_drug
# disease_do_food
# disease_not_food
# food_do_disease
# food_not_disease
# disease_symptom
# disease_cureway
# disease_prevent
# disease_ckeck
# drug_disease
# check_disease
# disease_lasttime
# disease_cureprob
# disease_easyget
# disease_not_easyget
# disease_acompany
# disease_cause
# symptom_disease
# disease_belong
# 按照此类型分别生成出以下内容
# 模拟病人询问医生的问句，有疾病该吃什么药物，疾病该吃什么食物，疾病不该吃什么食物，已知食物有利于疾病，已知食物不利于疾病，已知的疾病会有什么症状的关系，疾病的治疗方法，疾病该如何预防，疾病需要检查的项目，已知药物能治疗什么疾病，检查的项目能得出是什么疾病，疾病医疗周期，疾病治愈的可能性，疾病的易得人群，疾病不易得的人群，疾病的并发症，已知的症状与疾病的关系，疾病应该要挂什么科的关系。

# 帮我各生成1000条高质量数据，并要求在每个句子的后面根据上面19大类添加 0-18的label，并且是句子和label之间使用\t分隔符号分隔开（注意不是使用\t来分隔开，而是我们在编程中常用的'\t'分隔符号来分隔）
# 我会从不同表述角度入手，结合日常用语和专业询问方式，让问句丰富多变。尽量不重复出现相同字样与相同内容，帮我封装成一个txt文件类型的格式，不要序列号也部分类别，并且打乱顺序，与前面的内容不重复,谢谢
# 生成一个生成数据的python代码，谢谢。