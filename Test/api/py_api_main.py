import requests
import json
import sys,time
time_start = time.time()
head = "http://private.lcworkroom.cn/api/user/login"
headers = {'content-type': "application/json"}
body = {"credential":"2234175792","password":"asswecan","enduring":False}
response = requests.post(url=head,data=json.dumps(body),headers=headers)
print(response.text)
response_dict = json.loads(response.text)
if 'status' not in response_dict.keys():
    print("用户登录发生未知错误")
    sys.exit()
if response_dict["status"] == 0:
    token = response_dict["token"]
else:
    print("登录失败！")
    sys.exit()

# token="30151fb7e4ae7dbbae5852708b61e598e2fa7a207420b84e382d335ac16a5fb0"
print(token)
head = "http://private.lcworkroom.cn/api/user/info"
body = {"token":token}
response = requests.get(url=head,params=body)
print(response)
print(response.text)
response_dict = json.loads(response.text)
if 'status' not in response_dict.keys():
    print("读取用户信息发生未知错误")
    sys.exit()
if response_dict["status"] == 0:
    response_dict = response_dict["info"]
    id = response_dict["id"]
    name = response_dict["name"]
    phone = response_dict["phone"]
    email = response_dict["email"]
    nickname = response_dict["nickname"]
    permissionGroup = response_dict["permissionGroup"]
    print("id\t\t\tname\t\t\tphone\t\t\temail\t\t\tnickname\t\t\tpermissionGroup")
    print(id,"\t",name,"\t",phone,"\t",email,"\t",nickname,"\t",permissionGroup)
else:
    print("用户信息读取失败，估计是token无效")
time_end = time.time()
print('totally cost',time_end-time_start)