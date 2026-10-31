import requests
import time

# 定义请求url和传⼊的data
url = "http://127.0.0.1:5001/v1/main_server/"

# data = {"uid": "AI-20250723", "text": "失眠了建议吃什么药呢?"}
# data = {"uid": "AI-20250723", "text": "失眠建议挂什么科?"}
# data = {"uid": "AI-20250723", "text": "失恋是一种什么疾病?"}
data = {"uid": "AI-20250723", "text": "deepseek,今晚吃啥好捏?"}

start_time = time.time()
# 向服务发送post请求
res = requests.post(url, data=data)

cost_time = time.time() - start_time

# 打印返回的结果
print('⽤户输⼊:', data['text'])
print('红蜘蛛AI:', res.text)
print('单条样本预测耗时: ', cost_time * 1000, 'ms')
