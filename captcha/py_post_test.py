import requests,json
import time

headers = {'content-type': "application/json"}
data={"id":0,"status":0,"type":"img","subtype":"generate","data":{}}
response = requests.post(url="https://www.lcworkroom.cn/abc/captcha",data=json.dumps(data),headers=headers)
print(response.json())