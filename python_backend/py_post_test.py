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
#         "type":2,
#         "lab":"人类",
#         "title":"代领一个许淳皓",
#         "content":"我在路上捡到一个许淳皓",
#         "occurrence_time":"2019-04-22 16:17:42",
#         "user_name":"王凌超",
#         "user_phone":"",
#         "user_qq":"893721708",
#         "publish_time":"",
#     }}
# token = "294c949e1573c562fd70ac12a58859d7a82e7c46a77c59d7c9f2559ff01cbe52"
# response = requests.post(url="https://www.zustservice.cn/api/external/property?token={}".format(token),data=json.dumps(data),headers=headers)

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
#     "type":"product",
#     "subtype":"list",
#     "data":{
#         "product_name":"测试商品",
#         "product_key":"测试",
#         "shop_id":811729970,
#         "type":"all",
#         "order":"creat_time ASC"
#     }}
# token = "f25c67a05694f68c2923a94216a7ff8b2939d65265195e15e433cda7dbf27ea2"
# response = requests.post(url="http://127.0.0.1:4081/get/product?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/get/shop?token={}".format(token),data=json.dumps(data),headers=headers)

#
# data={
#     "id":0,
#     "status":0,
#     "type":"shop",
#     "subtype":"list",
#     "data":{
#         "shop_name":"小",
#         "order":"creat_time ASC"
#     }}
# token = "f25c67a05694f68c2923a94216a7ff8b2939d65265195e15e433cda7dbf27ea2"
# response = requests.post(url="http://127.0.0.1:4081/get/shop?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/get/shop?token={}".format(token),data=json.dumps(data),headers=headers)

## 删除寻物启事api
# data={
#     "id":0,
#     "status":0,
#     "type":"property",
#     "subtype":"delete",
#     "data":{
#         "id":1556543305,
#     }}
# token = "9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac"
# response = requests.post(url="http://127.0.0.1:4081/property?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)


## 上传图片
with open("./temp/temp.png","rb") as f:
      file_data = f.read()
# print(file_data)
img_base64 = str(base64.b64encode(file_data),"utf-8")
print("base64:\n{}".format(img_base64))
data={"id":0,
      "status":0,
      "type":"pic",
      "subtype":"upload",
      "data":{
          "from":"property",
          "base64":img_base64,
          "name":"test1"
}}
token = "36217bba0c734b85f53e7d8b7ef96c7469a67a44440ff89def5d8dcce5e60a54"
response = requests.post(url="http://127.0.0.1:4081/pic?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)

print(response.text)
# data_json = response.json()
# data = data_json["data"]
# img_b64 = data["imgdata"]
# img_data = base64.b64decode(img_b64)
# with open("./captcha/[%s].png" % data["code"],"wb") as f:
#     f.write(img_data)
