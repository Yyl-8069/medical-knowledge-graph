import torch
import onnxruntime
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.append('.')
import logging
import time
import json
from models.bert import *
from transformers import BertTokenizer
import numpy as np
import warnings

bert_path = str(Path(__file__).resolve().parents[1] / 'bert_pretrain')

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

class OnnxTrans():
    def __init__(self):
        self.init_model()
        self.init_onnx()
        
    def init_model(self):
        logger.info('init bert model......')
        self.config = Config(dataset='red_spider')
        # self.args = Args().get_parser()
        self.tokenizer = BertTokenizer.from_pretrained(bert_path)
        
        # 实例化bert模型
        self.model = Model(self.config)
        
        # 加载以训练好的模型, 后续是在bert_19.pt上进行ONNX加速
        self.model.load_state_dict(torch.load(self.config.save_path, map_location='cpu', weights_only=True), strict=True)
        self.model.eval()
       
    # 核心函数, 将bert模型导出onnx格式 
    def init_onnx(self):
        logger.info('convert torch model to onnx model......')
        
        # 导出onnx路径
        self.onnx_model_path = str(Path(self.config.save_path).with_suffix('.onnx'))
        
        # 明确使⽤torch的底层C语⾔包进⾏ONNX的导出操作
        operator_export_type = torch._C._onnx.OperatorExportTypes.ONNX
        
        # 构造一个虚拟输入
        onnx_input = self.make_onnx_infer_input()
        
        # 明确模型的输入, 输出, 动态轴设计
        dynamic_axes = {'input_ids': [0, 1], 'attention_mask': [0, 1], 'token_type_ids': [0, 1], 
                        'logits': [0]}
        
        # 将bert模型出成ONNX模型, 注意opset_version版本兼容性
        out = torch.onnx.export(self.model,  # 要导出的模型
                                onnx_input,  # 模型的虚拟输入
                                self.onnx_model_path,  # onnx模型的输出路径
                                verbose=False,  # 设置为 True 可以查看导出的图结构
                                opset_version=17,  # 模型的权重
                                input_names=['input_ids', 'attention_mask', 'token_type_ids'],
                                output_names=['logits'],
                                dynamic_axes=dynamic_axes  # 指定动态轴
                                )
        
    # 构造一个虚拟输入
    def make_onnx_infer_input(self):
        # 构造符合模型输入要求的虚拟张量
        # 例如: 一个包含 4 个 token 的序列 (包括 [CLS] 和 [SEP])
        onnx_input_ids = torch.LongTensor([[101, 13, 21, 102]]) # [CLS] + tokens + [SEP]
        onnx_attention_mask = torch.LongTensor([[1, 1, 1, 1]])  # 所有 token 都有效
        onnx_token_type_ids = torch.LongTensor([[0, 0, 0, 0]])  # 单句任务全部为零
        return (onnx_input_ids, onnx_attention_mask, onnx_token_type_ids)
    
    
if __name__ == '__main__':
    onnx = OnnxTrans()
