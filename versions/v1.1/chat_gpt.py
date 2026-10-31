class ChatGPT:
    def __init__(self, flag='deepseek', model_path='./pretrain_model'):
        if flag == 'deepseek':
            from deepsk import DS_RedSpider
            self.generator = DS_RedSpider()
        elif flag == 'gpt2':
            from gpt2 import GPT2_ReSpider
            self.generator = GPT2_ReSpider(model_path)
        elif flag == 'qwen':
            from qwen import Qwen_RedSpider
            self.generator = Qwen_RedSpider(model_path)
        else:
            raise ValueError('Unsupported model backend: ' + flag)

    def chat(self, prompt):
        return self.generator.chat(prompt)
