from transformers import AutoModelForCausalLM, AutoTokenizer


class Qwen_RedSpider():
    def __init__(self, model_path):
        model_path = model_path + '/Qwen3-4B-Instruct'
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype='auto',
            device_map='cuda'
        )
    
    def chat(self, prompt):
        messages = [
            {'role': 'system', 'content': '你是一个阿里云创造的千问大模型型. 你是⼀个⾮常专业并贴⼼的助⼿.'},
            {'role': 'user', 'content': prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors='pt').to('cuda')
        
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
            
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return response
