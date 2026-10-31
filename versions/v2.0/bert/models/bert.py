import torch
import torch.nn as nn
import os
from pathlib import Path
from transformers import BertModel, BertTokenizer, BertConfig

# 编写 Config 类代码
class Config(object):
    def __init__(self, dataset):
        self.model_name = "bert"
        # self.data_path = "E:/vscode/project3/red_spider/v2.0/bert/project_data/"
        root = Path(__file__).resolve().parents[1]
        four_class = dataset == 'four_class'
        self.data_path = str(root / ('project_data' if four_class else 'project_data_19')) + os.sep
        self.train_path = self.data_path + 'train.txt'
        self.dev_path = self.data_path + 'dev.txt'
        self.test_path = self.data_path + 'test.txt'
        self.class_list = (Path(self.data_path) / 'class.txt').read_text(encoding='utf-8').splitlines()
        self.save_path = str(root / 'save_path' / ('bert.pt' if four_class else 'bert_19.pt'))
        Path(self.save_path).parent.mkdir(exist_ok=True)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 设备
        self.require_improvement = 1000 # 若超过1000batch效果还没提升，则提前结束训练
        self.num_classes = len(self.class_list) # 类别数
        self.num_epochs = 1 # epoch数
        self.batch_size = 64 # mini-batch⼤⼩
        self.pad_size = 32 # 每句话处理成的⻓度(短填⻓切)
        self.learning_rate = 1e-5 # 学习率
        
        self.bert_path = str(root / 'bert_pretrain')
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)
        self.bert_config = BertConfig.from_pretrained(self.bert_path +
        '/bert_config.json')
        self.hidden_size = 768
        
        
        
        
class Model(nn.Module):
    def __init__(self, config):
        super(Model, self).__init__()
        self.bert = BertModel.from_pretrained(config.bert_path, 
        config=config.bert_config)
        for param in self.bert.encoder.layer[6:]:
            param.requires_grad = False
        self.fc = nn.Linear(config.hidden_size, config.num_classes)
        
    # def forward(self, x):
    #     # 输⼊的句⼦
    #     context = x[0]
    #     # 对padding部分进⾏mask, 和句⼦⼀个size, padding部分⽤0表示, ⽐如[1, 1, 1, 1, 0, 0]
    #     mask = x[2]
    #     out = self.bert(context, attention_mask=mask)
    #     out = self.fc(out.pooler_output)
        
    #     return out  
    
    # onnx时的接口
    def forward(self, input_ids, attention_mask=None, token_type_ids=None):
        if isinstance(input_ids, (tuple,list)):
            input_ids, _, attention_mask = input_ids
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        out = self.bert(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        out = self.fc(out.pooler_output)
        return out


# if __name__ == '__main__':
#     config = Config(dataset="medical")
#     save_path = config.save_path
#     print("实际保存路径：", repr(save_path))
