

# Python端 API文档

> 注：main.py文件运行时需用 -c configpath 来指定配置文件路径。
### Json的通用格式：

```python
{
  "id":"",
  "status":0,
  "type":"",
  "subtype":"",
  "data":{"key":"value"}
}
```

**所需参数介绍：**

|参数|介绍|调用方|样例|
|:--:|:--:|:--:|:--:|
|id|事件处理id，整型，请求端发送，接收端返回时原样返回|请求、返回|"id":"123456"|
|status|返回请求处理状态，请求时status填写0。默认返回0时为请求处理成功，若失败返回错误码|请求、返回|"status":0|
|message|状态简略信息，若成功调用则返回"successful"，失败返回错误信息|返回|"message":"successful"|
|type|请求类型|请求|"type":"user"|
|subtype|请求子类型|请求|"subtype":"login"|
|data|传送数据|请求、返回|"data":{"token":"xxxxxxxxxxxxx"}|

## **验证码类**

### 验证码API地址：

> https://www.zustservice.cn/api/external/captcha

#### **登录图片验证码**

+ **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"img",
    "subtype":"generate",
    "data":{}
}
```

+ **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{
        "imgdata":"iVBORw0yrfmx5m7975n32/23Y+cdf1Rv9oA6.....(以下省略)",
        "rand":"CST43"  #随机文本
    }
}
```

> ## 注意
> 新版本里将返回数据`data`中的`code`字段删除了。  
>
> 1. `id`字段需是整型数据。若是文本型数字数据，返回时自动转换成整数型数据；若是非数字型文本，则返回`-1`。`id`用于让前端在服务繁忙时能够对应服务;  
> 2. Python成功返回时的`imgdata`为验证码base64图片数据，前端获得数据后进行转码再显示;  
> 3. `rand`为随机字符串，前端获得验证码后需要将验证码和`rand`文本一并传给java端进行验证，`hash = MD5(code+rand)`。  
> 4. 验证码不区分大小写，请自行将验证码转换成全部小写。
>
> 

+ **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":1000, # 错误码
  "message":"验证码文件创建失败",
  "data":{},
}
```

> `status`传递的错误码类型为整型。具体的错误码详见最下方表格。

---



#### **图片验证码校验**

+ **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"img",
    "subtype":"validate",
    "data":{"hash":"asddwfw……"}
}
```

> ## 注意
>
> `hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`

+ **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{}
}
```

+ **Python端返回失败处理情况**

```python
{
  "id":请求时的ID,
  "status":-1, # 验证码hash值不匹配
  "message":"验证码hash值不匹配",
  "data":{},
}
```

> `status`传递的错误码类型为整型。具体的错误码详见最下方表格。

##### 局部status表

| status | message                                        |
| ------ | ---------------------------------------------- |
| 0      | 校验成功，验证码存在                           |
| -1     | 校验失败，验证码hash值不匹配（包括验证码过期） |

---

#### **注册手机验证码**

+ **POST发送请求的json文本**

```python
{
    "id":事件ID,
    "status":0,
    "type":"sms",
    "subtype":"generate",
    "data":{
        "phone":"137xxxxxxxx",
        "hash":"as1sdfdw4w……"
        }
}
```

> ## 注意
> 1. `phone`字段需用文本型传递，且只能为中国大陆手机号，不支持国外手机号
>
> 2. `hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`

+ **Python端返回成功处理情况**

```python
{
   "id":请求时的ID,
   "status":0,
   "message":"successful",
   "data":{
       "rand":"DSf4s"
   }
}
```

> ## 注意：
> 新版本里将返回数据`data`中的`code`字段删除了。  
> 1.Python成功返回时的addr为验证码文件名，由MD5加盐加密获得。  
> 2.`rand`为随机字符串，前端获得验证码后需要将验证码和rand文本一并传给java端进行验证，`hash = MD5(code+rand)`。  
> **3.手机验证码的时效为3min，由后端处理。验证码超时后端会返回`status = -4`的错误。**

+ **Python端返回失败处理情况**

```python
{
     "id":"请求时的ID",
     "status":1016,  #错误码
     "message":"手机号格式错误",
     "data":{},
}
```
> ## 注意
> `status`传递的错误码类型为整型。具体的错误码参照**腾讯云短信服务API文档**。
> [短信错误码



---



## **头像类**

### 头像上传API地址：

> https://www.zustservice.cn/api/external/portrait

#### **上传头像API**

- **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"portrait",
    "subtype":"upload",
    "data":{
        "name":"string"
        "id":"string"
        "base64":"string"
        "type":"string"
    }
}
```

- **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{
        "url":"https://www.zustservice.cn/XXX/XXX.png",
    }
}
```

> ## 注意
>
> 1. 目前所有的头像图片是专门的COS对象储存服务器里
> 2. 图片文件大小限制在1024kb以下
> 3. type字段要准确
> 4. 目前的api不会返回上传的图片路径，如果处理成功会返回百度的logo图片地址

- **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":1000, # 错误码
  "message":"验证码文件创建失败",
  "data":{},
}
```



#### 头像获取API地址：

> https://www.zustservice.cn/api/external/get/portrait/< id >

#### **获取头像API**

- **GET发送请求的链接参数**

```python
https://www.zustservice.cn/api/external/get/portrait/<id>
    <id>:账号id
```

- **Python端返回成功处理情况**

```python
返回图片的bytes数据
```

> ## 注意
>
> 1. 目前所有的头像图片是放在专门的COS对象储存服务器里，非码三秃的域名引用图片返回ban图片
> 2. id参数类型正确但不存在，返回默认头像
> 3. id参数类型不正确，返回error图片
> 4. 若无任何返回则是后端炸了。

- **Python端返回失败处理情况**

```python
1.非码三秃域名获取图片时：返回ban图片
2.id参数不正确或者指定id图片不存在：返回error图片
3.如果没有返回任何东西，就是后端炸了
```



## **寻物启事·失物招领类**

### 寻物启事API地址：

> https://www.zustservice.cn/api/external/property/find?token={token值}

#### **添加寻物启事文章API**

- **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"property",
    "subtype":"add",
    "data":{
        "lab":"测试", # 标签
        "title":"测试标题", # 文章标题
        "content":"我找到一件东西", # 文章内容
        "lost_time":"2019-04-22 16:17:42", # 丢失时间，日期时间型文本
        "loser_name":"王凌超", # 丢失者姓名
        "loser_phone":"123456", # 丢失者手机
        "loser_qq":"893721708", # 丢失者qq
        "publish_time":"", # 缺省自动为服务器当前时间
    }
}
```

|     参数     | 可否为空 | 可否缺省 |    数据类型     |         例子          |                     备注                      |
| :----------: | :------: | -------- | :-------------: | :-------------------: | :-------------------------------------------: |
|      id      |    √     | √        |     bigint      |                       |         文章id，唯一性，后端自动生成          |
|    state     |    √     | √        |       int       |                       |            0为正在进行，1为已结束             |
|     lab      |          |          |     string      |        "测试"         |                                               |
|    title     |          |          |     string      |      "测试标题"       |                                               |
|   content    |          |          |     string      |   "我找到一件东西"    |                                               |
|  lost_time   |    √     |          | datetime-string | "2019-04-22 16:17:42" | 需要是日期时间型文本，为空默认为信息发布时间  |
|  loser_name  |          |          |     string      |       "王凌超"        |                                               |
| loser_phone  |    √     |          |     string      |       "123456"        |                                               |
|   loser_qq   |    √     |          |     string      |      "893721708"      |                                               |
|  finder_id   |    √     | √        |     string      |                       |              找到者id，该api不用              |
| finder_name  |    √     | √        |     string      |                       |             找到者姓名，该api不用             |
| finder_phone |    √     | √        |     string      |                       |             找到者手机，该api不用             |
|  finder_qq   |    √     | √        |     string      |                       |              找到者qq，该api不用              |
|   user_id    |    √     | √        |     string      |     "1180310086"      |      发起者用户id，后端自动通过token获取      |
| publish_time |    √     |          | datetime-string | "2019-04-22 16:17:42" |      建议为空。为空自动为服务器当前时间       |
| update_time  |    √     | √        | datetime-string | "2019-04-22 16:17:42" | 更新时间，该api不用，且创建时默认等于发布时间 |



- **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{}
}
```

- **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-200, # 错误码
  "message":"Connect Database Failed",
  "data":{},
}
```

#### 局部status表

| status | message                            | 内容                                |
| ------ | ---------------------------------- | ----------------------------------- |
| -100   | Missing necessary args             | api地址中缺少token参数              |
| -101   | Error token                        | token不正确                         |
| -102   | Get userid failed for the token    | 使用该token获取userid失败           |
| -200   | Connect Database Failed            | 数据库操作失败，检查SQL语句是否正确 |
| -201   | Necessary key-value can't be empty | 关键键值对值不可为空                |



------

## 全局Status表

| 参数 |     Message      |         内容          |
| :--: | :--------------: | :-------------------: |
|  0   |        OK        |     函数处理正确      |
|  -1  |  Error JSON key  |  json文本必需key缺失  |
|  -2  | Error JSON value |   json文本value错误   |
|  -3  |  Error data key  | data数据中必需key缺失 |
|  -4  |    Error Hash    |   Hash校验文本错误    |
| -404 |  Unknown Error   |    未知的Redis错误    |

------

> `status`传递的错误码类型为整型。
>
> 验证码相关的错误码详见最下方表格。[短信错误码表](https://cloud.tencent.com/document/product/382/3771 "腾讯云短信API文档")



> ## Others
>
> 头像API仅测试使用。
>
> 