

# Python端 API文档

[TOC]



> 注：main.py文件运行时需用 -c configpath 来指定配置文件路径。
## **Json的通用格式：**

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

#### 登录图片验证码

> **API类型**

**请求类型：`POST`**

> **验证码API地址：**

**https://www.zustservice.cn/api/external/captcha**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"img",
    "subtype":"generate",
    "data":{}
}
```

> **Python端返回成功处理情况**

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

+ 新版本里将返回数据`data`中的`code`字段删除了。  

+ `id`字段需是整型数据。若是文本型数字数据，返回时自动转换成整数型数据；若是非数字型文本，则返回`-1`。`id`用于让前端在服务繁忙时能够对应服务;  

+ Python成功返回时的`imgdata`为验证码base64图片数据，前端获得数据后进行转码再显示;  

+ `rand`为随机字符串，前端获得验证码后需要将验证码和`rand`文本一并传给java端进行验证，`hash = MD5(code+rand)`。  

+ 验证码不区分大小写，请自行将验证码转换成全部小写。

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":1000, # 错误码
  "message":"验证码文件创建失败",
  "data":{},
}
```

+ `status`传递的错误码类型为整型。具体的错误码详见最下方表格。

---



#### 图片验证码校验

> **API类型**

**请求类型：`POST`**

> **验证码API地址：**

**https://www.zustservice.cn/api/external/captcha**

> **POST发送请求的json文本**

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

+ `hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":请求时的ID,
  "status":-1, # 验证码hash值不匹配
  "message":"验证码hash值不匹配",
  "data":{},
}
```

+ `status`传递的错误码类型为整型。具体的错误码详见最下方表格。

> **局部status表**

| status | message                                        |
| ------ | ---------------------------------------------- |
| 0      | 校验成功，验证码存在                           |
| -1     | 校验失败，验证码hash值不匹配（包括验证码过期） |

---

#### 注册手机验证码

> **API类型**

**请求类型：`POST`**

> **验证码API地址：**

**https://www.zustservice.cn/api/external/captcha**

> **POST发送请求的json文本**

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

+ phone`字段需用文本型传递，且只能为中国大陆手机号，不支持国外手机号`
+ hash`字段的数据要求是用户填写的验证码内容与rand文本进行MD5加密获得。即`hash = MD5(code + rand)`

> **Python端返回成功处理情况**

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

+ 新版本里将返回数据`data`中的`code`字段删除了。  
+ Python成功返回时的addr为验证码文件名，由MD5加盐加密获得。  
+ `rand`为随机字符串，前端获得验证码后需要将验证码和rand文本一并传给java端进行验证，`hash = MD5(code+rand)`。  
+ **手机验证码的时效为3min，由后端处理。验证码超时后端会返回`status = -4`的错误。**

> **Python端返回失败处理情况**

```python
{
     "id":"请求时的ID",
     "status":1016,  #错误码
     "message":"手机号格式错误",
     "data":{},
}
```
> ## 注意

+ `status`传递的错误码类型为整型。具体的错误码参照**腾讯云短信服务API文档**。
  [短信错误码



---



## **头像类**

#### 上传头像API

> **API类型**

**请求类型：`POST`**

> **头像上传API地址：**

**https://www.zustservice.cn/api/external/portrait**

> **POST发送请求的json文本**

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

> **Python端返回成功处理情况**

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

+ 目前所有的头像图片是专门的COS对象储存服务器里

+ 图片文件大小限制在1024kb以下

+ type字段要准确

+ 目前的api不会返回上传的图片路径，如果处理成功会返回百度的logo图片地址

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":1000, # 错误码
  "message":"验证码文件创建失败",
  "data":{},
}
```

#### 获取头像API

> **API类型**

**请求类型：`GET`**

> **头像获取API地址：**

**https://www.zustservice.cn/api/external/get/portrait/< id >**

> **GET发送请求的链接参数**

```python
https://www.zustservice.cn/api/external/get/portrait/<id>
```

+ `<id>`：账号id

> **Python端返回成功处理情况**

```python
返回图片的bytes数据
```

> ## 注意

+ 目前所有的头像图片是放在专门的COS对象储存服务器里，非码三秃的域名引用图片返回ban图片

+ id参数类型正确但不存在，返回默认头像

+ id参数类型不正确，返回error图片

+ 若无任何返回则是后端炸了。

> **Python端返回失败处理情况**

```python
1.非码三秃域名获取图片时：返回ban图片
2.id参数不正确或者指定id图片不存在：返回error图片
3.如果没有返回任何东西，就是后端炸了
```



## **寻物启事·失物招领类**

#### 添加启事文章API

> **API类型**

**请求类型：`POST`**

> **POST启事API地址**

**https://www.zustservice.cn/api/external/property?token={token值}**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"property",
    "subtype":"add",
    "data":{
        "type":1,
        "lab":"测试", # 标签
        "title":"测试标题", # 文章标题
        "content":"我找到一件东西", # 文章内容
        "occurrence_time":"2019-04-22 16:17:42", # 丢失时间，日期时间型文本
        "user_name":"王凌超", # 丢失者姓名
        "user_phone":"123456", # 丢失者手机
        "user_qq":"893721708", # 丢失者qq
        "publish_time":"", # 缺省自动为服务器当前时间
    }
}
```

> **data字段表**

|        参数         | 可否为空 | 可否缺省 |      数据类型       |           例子            | 字段长度限制 |                            备注                            |
| :-----------------: | :------: | -------- | :-----------------: | :-----------------------: | :----------: | :--------------------------------------------------------: |
|         id          |    √     | √        |       bigint        |                           |  -2^31~2^31  |                 文章id，主键，后端自动生成                 |
|      **type**       |          |          |       **int**       |           **1**           |    **1**     |  **文章类型，1为寻物启事，2为失物招领。不是这两个报错。**  |
|        state        |    √     | √        |         int         |                           |  -2^15~2^15  |              事件状态，0为正在进行，1为已结束              |
|         lab         |          |          |       string        |          "测试"           |      50      |                                                            |
|        title        |          |          |       string        |        "测试标题"         |      20      |                                                            |
|       content       |          |          |       string        |     "我找到一件东西"      |   **500**    |                                                            |
| **occurrence_time** |  **√**   |          | **datetime-string** | **"2019-04-22 16:17:42"** |              | **发生时间，需要是日期时间型文本，为空默认为信息发布时间** |
|     **user_id**     |  **√**   | **√**    |     **string**      |     **“1180310086”**      |    **15**    |                        **发起者id**                        |
|    **user_name**    |          |          |     **string**      |       **"王凌超"**        |    **10**    |                       **发起者姓名**                       |
|   **user_phone**    |  **√**   |          |     **string**      |       **"123456"**        |    **15**    |                       **发起者手机**                       |
|     **user_qq**     |  **√**   |          |     **string**      |      **"893721708"**      |    **15**    |                        **发起者QQ**                        |
|    **user2_id**     |  **√**   | **√**    |     **string**      |                           |    **15**    |                  **找到者id，该api不用**                   |
|   **user2_name**    |  **√**   | **√**    |     **string**      |                           |    **10**    |                 **找到者姓名，该api不用**                  |
|   **user2_phone**   |  **√**   | **√**    |     **string**      |                           |    **15**    |                 **找到者手机，该api不用**                  |
|    **user2_qq**     |  **√**   | **√**    |     **string**      |                           |    **15**    |                  **找到者qq，该api不用**                   |
|    publish_time     |    √     |          |   datetime-string   |   "2019-04-22 16:17:42"   |              |             建议为空。为空自动为服务器当前时间             |
|     update_time     |    √     | √        |   datetime-string   |   "2019-04-22 16:17:42"   |              |       更新时间，该api不用，且创建时默认等于发布时间        |
|     **pic_num**     |  **√**   | **√**    |       **int**       |           **2**           |   **0-3**    |                   **图片数量，最多三张**                   |
|    **pic_url1**     |  **√**   | **√**    |     **string**      |                           |   **1024**   |                       **图片1地址**                        |
|    **pic_url2**     |  **√**   | **√**    |     **string**      |                           |   **1024**   |                       **图片2地址**                        |
|    **pic_url3**     |  **√**   | **√**    |     **string**      |                           |   **1024**   |                       **图片3地址**                        |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"uid":文章uid # 长整数型}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-200, # 错误码
  "message":"Failure to operate database",
  "data":{},
}
```

> **局部status表**

| status | message                            | 内容                                |
| ------ | ---------------------------------- | ----------------------------------- |
| -100   | Missing necessary args             | api地址中缺少token参数              |
| -101   | Error token                        | token不正确                         |
| -102   | Get userid failed for the token    | 使用该token获取userid失败           |
| -200   | Failure to operate database            | 数据库操作失败，检查SQL语句是否正确 |
| -201   | Necessary key-value can't be empty | 关键键值对值不可为空                |
| -202   | Missing necessary data key-value   | 缺少关键的键值对                    |
| -203   | Arg's value type error             | 键值对数据类型错误                  |
| -204   | Arg's value error                  | 键值对数据错误                      |



#### 更新启事文章API

> **API类型**

**请求类型：`POST`**

> **POST启事API地址**

**https://www.zustservice.cn/api/external/property?token={token值}**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"property",
    "subtype":"update",
    "data":{
        "id":12334567, # 文章id
        "title":"测试标题", # 文章标题
        "content":"我找到一件东西", # 文章内容
    }
}
```

> **data字段表**

|        参数         | 可否为空 | 可否缺省 |      数据类型       |           例子            | 字段长度限制 |                           备注                           |
| :-----------------: | :------: | -------- | :-----------------: | :-----------------------: | :----------: | :------------------------------------------------------: |
|         id          |          |          |       bigint        |                           |  -2^31~2^31  |                     文章id，不可修改                     |
|      **type**       |          | **√**    |       **int**       |           **1**           |    **1**     | **文章类型，1为寻物启事，2为失物招领。不是这两个报错。** |
|        state        |          | √        |         int         |                           |  -2^15~2^15  |                  0为正在进行，1为已结束                  |
|         lab         |          | √        |       string        |      "卡类\|一卡通"       |      50      |               标签，用“ \| ” 进行分割文本                |
|        title        |          | √        |       string        |        "测试标题"         |      20      |                           标题                           |
|       content       |          | √        |       string        |     "我找到一件东西"      |   **500**    |                         丢失详情                         |
| **occurrence_time** |  **√**   | **√**    | **datetime-string** | **"2019-04-22 16:17:42"** |              |   **发生时间，日期时间型文本，为空默认为信息发布时间**   |
|     **user_id**     |          | **√**    |     **string**      |     **"1180310086"**      |    **15**    |      **发起者用户id，不填写后端自动读取，不可修改**      |
|    **user_name**    |          | **√**    |     **string**      |       **"王凌超"**        |    **10**    |                      **发起者姓名**                      |
|   **user_phone**    |  **√**   | **√**    |     **string**      |       **"123456"**        |    **15**    |                    **发起者手机号码**                    |
|     **user_qq**     |  **√**   | **√**    |     **string**      |      **"893721708"**      |    **15**    |                       **发起者qq**                       |
|    **user2_id**     |  **√**   | **√**    |     **string**      |     **“1180310085”**      |    **15**    |                       **响应者id**                       |
|   **user2_name**    |  **√**   | **√**    |     **string**      |       **“码三秃”**        |    **10**    |                      **响应者姓名**                      |
|   **user2_phone**   |  **√**   | **√**    |     **string**      |     **“1216515656”**      |    **15**    |                      **响应者手机**                      |
|    **user2_qq**     |  **√**   | **√**    |     **string**      |      **“15448486”**       |    **15**    |                       **响应者qq**                       |
|     update_time     |    √     | √        |   datetime-string   |   "2019-04-22 16:17:42"   |              | 更新时间，日期时间型文本，为空或缺省默认为服务器当前时间 |

+ update API中`id`字段和`user_id`不可进行修改，只能做查询的条件

+ update API执行成功的条件是`id`存在且id对应的`user_id`与传递的`user_id`或者`token`所对应的`user_id`一致，才能成功删除。若失败返回-200错误码。

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"uid":文章uid # 长整数型}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-200, # 错误码
  "message":"Failure to operate database",
  "data":{},
}
```

> **局部status表**

| status | message                            | 内容                                |
| ------ | ---------------------------------- | ----------------------------------- |
| -100   | Missing necessary args             | api地址中缺少token参数              |
| -101   | Error token                        | token不正确                         |
| -102   | Get userid failed for the token    | 使用该token获取userid失败           |
| -200   | Failure to operate database            | 数据库操作失败，检查SQL语句是否正确 |
| -201   | Necessary key-value can't be empty | 关键键值对值不可为空                |
| -202   | Missing necessary data key-value   | 缺少关键的键值对                    |
| -203   | Arg's value type error             | 键值对数据类型错误                  |
| -204   | Arg’s value error                  | 键值对数据错误                      |



#### 删除启事文章API

> **API类型**

**请求类型：`POST`**

> **POST启事API地址**

**https://www.zustservice.cn/api/external/property?token={token值}**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"property",
    "subtype":"delete",
    "data":{
        "id":12334567, # 文章id
        "user_id":"1180310086" # 用户id
    }
}
```

> **data字段表**

|  参数   | 可否为空 | 可否缺省 | 数据类型 |     例子     | 字段长度限制 |                    备注                    |
| :-----: | :------: | -------- | :------: | :----------: | :----------: | :----------------------------------------: |
|   id    |          |          |  bigint  |              |  -2^31~2^31  |              文章id，不可修改              |
| user_id |          | √        |  string  | "1180310086" |      15      | 发起者用户id，不填写后端自动读取，不可修改 |

+ delete API 参数只能是以上两个，其他字段哪怕传递过来也自动忽略

+ delete API执行成功的条件是`id`存在且id对应的`user_id`与传递的`user_id`或者`token`所对应的`user_id`一致，才能成功删除。若失败返回-200错误码。



> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"uid":文章uid # 长整数型}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-200, # 错误码
  "message":"Failure to operate database",
  "data":{},
}
```

> **局部status表**

| status | message                            | 内容                                |
| ------ | ---------------------------------- | ----------------------------------- |
| -100   | Missing necessary args             | api地址中缺少token参数              |
| -101   | Error token                        | token不正确                         |
| -102   | Get userid failed for the token    | 使用该token获取userid失败           |
| -200   | Failure to operate database            | 数据库操作失败，检查SQL语句是否正确 |
| -201   | Necessary key-value can't be empty | 关键键值对值不可为空                |
| -202   | Missing necessary data key-value   | 缺少关键的键值对                    |
| -203   | Arg's value type error             | 键值对数据类型错误                  |



#### GET启事API地址

> **API类型**

**请求类型：`GET`**

> **GET启事API地址**

**https://www.zustservice.cn/api/external/get/property**

>  **参数表**

| 参数  |   缺省   |                           说明                            |           备注           |
| :---: | :------: | :-------------------------------------------------------: | :----------------------: |
| token | 必要参数 |                         用户token                         |                          |
| type  | 必要参数 |                  查询寻物启事或失物招领                   | 1为寻物启事，2为失物招领 |
|  key  | 可选参数 | 关键词检索，检索的字段包括id,lab，title，content，user_id |    不可与下方参数共用    |
|  id   | 可选参数 |                      寻物启事id检索                       |    不可与key参数共用     |
| state | 可选参数 |                     寻物启事state检索                     |    不可与key参数共用     |
|  lab  | 可选参数 |                     寻物启事标签检索                      |    不可与key参数共用     |
|  ...  | 可选参数 |            其他字段详情请参照上方的data字段表             |    不可与key参数共用     |

> **Python端返回成功处理情况**

```python
{
    "id": -1,
    "status": 0, 
    "message": "successful",
    "data": [{"id": 1556542860, "type": 1, "state": 1, "lab": "卡类", "title": "我丢了一张一卡通", "content": "我在教学楼丢了一张校园卡", "occurrence_time": "2019-04-22 16:17:42", "user_id": "1180310086", "user_name": "wlc", "user_phone": "13750687010", "user_qq": "893721708", "user2_id": "", "user2_name": "", "user2_phone": "", "user2_qq": "", "publish_time": "2019-04-29 21:01:00", "update_time": "2019-04-29 22:02:11"}]
}
```

+ 默认按照更新时间的降序排列

> Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-100, # 错误码
  "message":"Args Error",
  "data":{},
}
```

+ 与其他api返回的数据不同的是，data返回的是一个列表，而非一个字典，注意区分处理。

+ 语法正确但数据库无记录的话，data返回一个空列表，即`data:[]`

+ 此查询语句可进行关键字查询、精确查询

+ 关键字查询：在`lab`、`title`、`content`中模糊查找符合关键字的数据

+ 精确查询，在指定的字段进行查询，其中`id`，`status`以及`lost_time`、`publish_time`、`update_time`等字段为精确查找，其余字段为模糊查找

> **局部status表**

| status |        message         |                内容                |
| :----: | :--------------------: | :--------------------------------: |
|  -100  |       Args Error       |       GET请求中参数名不正确        |
|  -101  |    Args Type Error     |           参数值类型错误           |
|  -103  |     Args conflict      | 同时使用了key参数和其他非token参数 |
|  -104  | Missing necessary args |          缺少必要的参数值          |
|  -105  |      Error token       |            token不正确             |
|  -106  |       Args Error       |             参数值错误             |

------

## **学生自营平台类**

### **店铺（shop） API**

#### 创建店铺

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/shop?token={token值}**

> **data字段表**

|     name     | data type | length | not null | primary key | 注释     |
| :----------: | :-------: | :----: | -------- | ----------- | -------- |
|   shop_id    |  big int  |   9    | √        | √           | 店铺id   |
|  shop_name   |  string   |  100   | √        | √           | 店铺名称 |
| shop_content |  string   |        |          |             | 店铺内容 |
|   user_id    |  big int  |   11   | √        |             | 店主id   |
|  creat_time  | datetime  |        | √        |             | 创建时间 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"shop",
    "subtype":"creat",
    "data":{
        "shop_name":"码三秃的店铺", # 店铺名称
        "user_id":1180310086 # 用户id
    }
}
```

+ `shop_id`在该API里不需要传入，哪怕传入也做无效处理，`shop_id`为随机生成的9位id
+ `shop_name`为必传字段，且不为空，且后期不可修改
+ `shop_content`为选填字段，不填默认为空
+ `user_id`修改为`int`类型变量
+ `creat_time`在该API里不需要传入，哪怕传入也做无效处理，`creat_time`为系统当前时间

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"shop_id":811729970 # 长整数型}
}
```

+ 返回9位的`shop_id`

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-100, # 错误码
  "message":"Args Error",
  "data":{},
}
```

> **局部 Status 状态表**

| status |               message               |          内容          |
| :----: | :---------------------------------: | :--------------------: |
|  100   |       The shop name was used        |    店铺名称已被使用    |
|  101   | The number of shops has been capped | 该账号下店铺数量已上限 |

+ 其他`status`码请看[全局Status表](#全局Status表)

#### 更新店铺

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/shop?token={token值}**

> **data字段表**

|     name     | data type | length | not null | primary key | 注释     |
| :----------: | :-------: | :----: | -------- | ----------- | -------- |
|   shop_id    |  big int  |   9    | √        | √           | 店铺id   |
|  shop_name   |  string   |  100   | √        | √           | 店铺名称 |
| shop_content |  string   |        |          |             | 店铺内容 |
|   user_id    |  big int  |   11   | √        |             | 店主id   |
|  creat_time  | datetime  |        | √        |             | 创建时间 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"shop",
    "subtype":"creat",
    "data":{
        "shop_id":"811729970", # 店铺id
        "shop_content":"这是码三秃家的店铺" # 店铺内容
    }
}
```

- `shop_id`为必传字段
- `shop_content`为必传字段
- 若用户登录所用`token`对应的`user_id`不是店长id，则无法修改店铺信息

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{}
}
```

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-100, # 错误码
  "message":"Args Error",
  "data":{},
}
```

> **局部 Status 状态表**

| status |      message       |         内容         |
| :----: | :----------------: | :------------------: |
|  100   | No right to update | 当前所处用户无权操作 |

+ 其他`status`码请看[全局Status表](#全局Status表)

## **全局Status表**

| 参数 |             Message             |                内容                 | 请求类型  |
| :--: | :-----------------------------: | :---------------------------------: | --------- |
|  0   |               OK                |            函数处理正确             | POST、GET |
|  -1  |         Error JSON key          |         json文本必需key缺失         | POST      |
|  -2  |        Error JSON value         |          json文本value错误          | POST      |
|  -3  |         Error data key          |        data数据中必需key缺失        | POST      |
|  -4  |           Error Hash            |          Hash校验文本错误           | POST      |
| -100 |     Missing necessary args      |       api地址中缺少token参数        | POST、GET |
| -101 |           Error token           |             token不正确             | POST、GET |
| -102 | Get userid failed for the token |      使用该token获取userid失败      | POST、GET |
| -200 |   Failure to operate database   | 数据库操作失败，检查SQL语句是否正确 | POST、GET |
| -404 |          Unknown Error          |           未知的Redis错误           | POST      |

------

> `status`传递的错误码类型为整型。
>
> 验证码相关的错误码详见最下方表格。[短信错误码表](https://cloud.tencent.com/document/product/382/3771 "腾讯云短信API文档")



> ## Others
>
> 头像API仅测试使用。
>
> 