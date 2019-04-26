# coding=utf-8
import requests,json
import base64

headers = {'content-type': "application/json"}
# data={"id":0,"status":0,"type":"img","subtype":"generate","data":{}}

# response = requests.post(url="http://127.0.0.1:4081/captcha",data=json.dumps(data),headers=headers)



## 添加寻物启事api
# data={
#     "id":0,
#     "status":0,
#     "type":"property",
#     "subtype":"add",
#     "data":{
#         "lab":"丢人",
#         "title":"我丢人了",
#         "content":"我丢了一个许淳皓",
#         "lost_time":"2019-04-22 16:17:42",
#         "loser_name":"王凌超",
#         "loser_phone":"",
#         "loser_qq":"893721708",
#         "publish_time":"",
#     }}
# token = "9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac"
# response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)

## 更新寻物启事api
# data={
#     "id":0,
#     "status":0,
#     "type":"property",
#     "subtype":"update",
#     "data":{
#         "id":1555943163,
#         "lab":"一卡通",
#         "title":"我丢了一张一卡通",
#         "content":"在9#教学楼206丢失一个一卡通",
#         "lost_time":"2019-04-26 0:18:30",
#         "loser_name":"王凌超",
#         "loser_phone":"13750687010",
#         "loser_qq":"893721708",
#         "publish_time":"",
#     }}
# data={
#     "id":0,
#     "status":0,
#     "type":"property",
#     "subtype":"update",
#     "data":{
#         "id":1555943163,
#         "state":1,
#         "title":"我丢了一张一卡通",
#         "content":"我在教学楼丢了一张校园卡",
#         "finder_name":"wlc",
#         "finder_phone":"13750687010",
#     }}
# token = "9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac"
# # response = requests.post(url="http://127.0.0.1:4081/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)

## 删除寻物启事api
data={
    "id":0,
    "status":0,
    "type":"property",
    "subtype":"delete",
    "data":{
        "id":1555945812,
    }}
token = "9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac"
response = requests.post(url="http://127.0.0.1:4081/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)





print(response.text)
# data_json = response.json()
# data = data_json["data"]
# img_b64 = data["imgdata"]
# img_data = base64.b64decode(img_b64)
# with open("./captcha/[%s].png" % data["code"],"wb") as f:
#     f.write(img_data)
