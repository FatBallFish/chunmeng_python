import requests,json
import time

headers = {'content-type': "application/json"}
data={"id":0,"status":0,"type":"sms","subtype":"generate","data":{"phone":""}}
response = requests.post(url="http://127.0.0.1:8080/api/captcha",data=json.dumps(data),headers=headers)
print(response.json())