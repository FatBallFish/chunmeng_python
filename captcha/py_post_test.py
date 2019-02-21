import requests,json
import time

headers = {'content-type': "application/json"}
data={"id":0,"status":0,"type":"sms","subtype":"generate","data":{"phone":"13750687010"}}
response = requests.post(url="https://www.lcworkroom.cn/api/captcha",data=json.dumps(data),headers=headers)
print(response.json())