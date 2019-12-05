# coding=utf-8
import requests, json
import base64

headers = {'content-type': "application/json"}
# data={"id":0,"status":0,"type":"img","subtype":"generate","data":{}}

# response = requests.post(url="http://127.0.0.1:4081/captcha",data=json.dumps(data),headers=headers)


# 添加寻物启事api

# data = {
#     "id": 0,
#     "status": 0,
#     "type": "property",
#     "subtype": "add",
#     "data": {
#         "content": "丢丢丢",
#         "lab": "card",
#         "occurrence_time": "",
#         "pic_num": 3,
#         "pic_url1": "./api/external/get/pic/property/eafe254797d819bfd0f1d5782ae1e6b8",
#         "pic_url2": "./api/external/get/pic/property/efea3e8dd4c701ce6b468f5584c130f6",
#         "pic_url3": "./api/external/get/pic/property/5dbe81d1a473450506117c4abc924a35",
#         "publish_time": "",
#         "title": "丢",
#         "type": 2,
#         "user_name": "123",
#         "user_phone": "321",
#         "user_qq": "123456",
#         }}

# data = {
#     "id": 0,
#     "status": 0,
#     "type": "property",
#     "subtype": "add",
#     "data": {
#         "type": 2,
#         "lab": "人类",
#         "title": "代领一个许淳皓",
#         "content": "我在路上捡到一个许淳皓",
#         "occurrence_time": "2019-04-22 16:17:42",
#         "user_name": "王凌超",
#         "user_phone": "",
#         "user_qq": "893721708",
#         "publish_time": "",
#     }}
# token = "a55026d26b842ce685bd9d1e7692aa8a0c24063f3db20123d1322c559f16e1a2"
# response = requests.post(url="http://127.0.0.1:4081/property?token={}".format(token),data=json.dumps(data), headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/property?token={}".format(token),data=json.dumps(data), headers=headers)

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

# 获取商品列表
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

# 获取商品信息
data={
    "id":0,
    "status":0,
    "type":"product",
    "subtype":"info",
    "data":{
        "product_id":5873413,
    }}
token = "124ea47c0f4f2d1edbfdb1d0bc54c448028de0602c9b0088eac60b81de1dfd9b"
response = requests.post(url="http://127.0.0.1:4081/get/product?token={}".format(token),data=json.dumps(data),headers=headers)
# response = requests.post(url="https://www.zustservice.cn/api/external/get/shop?token={}".format(token),data=json.dumps(data),headers=headers)
print(response.text)
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


# ## 上传图片
# with open("./temp/temp.png","rb") as f:
#       file_data = f.read()
# # print(file_data)
# img_base64 = str(base64.b64encode(file_data),"utf-8")
# print("base64:\n{}".format(img_base64))
# data={"id":0,
#       "status":0,
#       "type":"pic",
#       "subtype":"upload",
#       "data":{
#           "from":"property",
#           "base64":img_base64,
#           "name":"test1"
# }}
# token = "36217bba0c734b85f53e7d8b7ef96c7469a67a44440ff89def5d8dcce5e60a54"
# response = requests.post(url="http://127.0.0.1:4081/pic?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)

# # 创建店铺
# # ["product_id", "product_num", "product_unitprice", "product_totalprice"]
# data={
#     "id":0,
#     "status":0,
#     "type":"shop",
#     "subtype":"creat",
#     "data":{
#         "shop_name":"店铺名称",
#         "user_id":1180310086,
#     }}
# token = "227e950ba7ba8bc97bf600ce202b8f8f661ebca4fd46bd399a698c164ea995c4"
# response = requests.post(url="http://127.0.0.1:4081/shop?token={}".format(token),data=json.dumps(data),headers=headers)

# # 更新店铺信息
# # ["product_id", "product_num", "product_unitprice", "product_totalprice"]
# data={
#     "id":0,
#     "status":0,
#     "type":"shop",
#     "subtype":"update",
#     "data":{
#         "shop_id":656019061,
#         "shop_content":"五小灵童团队的店铺",
#     }}
# token = "a65857ae067ca9f1bbcd2316855296bb447f67b4e6ce27d675294ebf440a5110"
# response = requests.post(url="http://127.0.0.1:4081/shop?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)

# # 新增订单
# # ["product_id", "product_num", "product_unitprice", "product_totalprice"]
# data={
#     "id":0,
#     "status":0,
#     "type":"purchase",
#     "subtype":"apply",
#     "data":{
#         "product_id":4517733,
#         "product_num":1,
#         "product_unitprice":101.5,
#         "product_totalprice":101.5
#     }}
# token = "227e950ba7ba8bc97bf600ce202b8f8f661ebca4fd46bd399a698c164ea995c4"
# response = requests.post(url="http://127.0.0.1:4081/purchase?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)

# # 查询订单信息
# data={
#     "id":0,
#     "status":0,
#     "type":"purchase",
#     "subtype":"info",
#     "data":{
#         "purchase_id":"15749503434517733",
#     }}
# token = "4de04c69b096465c28568d002c651bcd516f5b9ad4d95ea5889791bde7079879"
# response = requests.post(url="http://127.0.0.1:4081/purchase?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)

# # 支付订单
# data={
#     "id":0,
#     "status":0,
#     "type":"purchase",
#     "subtype":"pay",
#     "data":{
#         "purchase_id":"15749511524517733",
#         "method":"wallet"
#     }}
# token = "4de04c69b096465c28568d002c651bcd516f5b9ad4d95ea5889791bde7079879"
# response = requests.post(url="http://127.0.0.1:4081/purchase?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)

# # 取消订单
# data={
#     "id":0,
#     "status":0,
#     "type":"purchase",
#     "subtype":"cancel",
#     "data":{
#         "purchase_id":"15749511524517733",
#     }}
# token = "4de04c69b096465c28568d002c651bcd516f5b9ad4d95ea5889791bde7079879"
# response = requests.post(url="http://127.0.0.1:4081/purchase?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)

# # 获取订单列表
# data={
#     "id":0,
#     "status":0,
#     "type":"purchase",
#     "subtype":"list",
#     "data":{}}
# token = "4de04c69b096465c28568d002c651bcd516f5b9ad4d95ea5889791bde7079879"
# response = requests.post(url="http://127.0.0.1:4081/purchase?token={}".format(token),data=json.dumps(data),headers=headers)
# # response = requests.post(url="https://www.zustservice.cn/api/external/property/find?token={}".format(token),data=json.dumps(data),headers=headers)
# print(response.text)