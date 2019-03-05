import requests,json
import base64

headers = {'content-type': "application/json"}
data={"id":0,"status":0,"type":"img","subtype":"generate","data":{}}
response = requests.post(url="http://127.0.0.1:8080/captcha",data=json.dumps(data),headers=headers)
print(response.json())
# data_json = response.json()
# data = data_json["data"]
# img_b64 = data["imgdata"]
# img_data = base64.b64decode(img_b64)
# with open("./captcha/[%s].png" % data["code"],"wb") as f:
#     f.write(img_data)
