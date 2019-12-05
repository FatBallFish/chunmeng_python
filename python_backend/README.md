`

# Python端 API文档

[TOC]

## 目录

- [**Json的通用格式**](#Json的通用格式)
- [**验证码类**](#验证码类)
  - [登录图片验证码](#登录图片验证码)
  - [图片验证码校验](#图片验证码校验)
  - [注册手机验证码](#注册手机验证码)
- [**头像类**](#头像类)
  - [上传头像API](#上传头像API)
  - [获取头像API](#获取头像API)
  - [上传图片](#上传图片)
  - [获取图片](#获取图片)
- [**寻物启事·失物招领类**](#寻物启事·失物招领类)
  - [添加启事文章API](#添加启事文章API)
  - [更新启事文章API](#更新启事文章API)
  - [删除启事文章API](#删除启事文章API)
  - [GET启事API地址](#GET启事API地址)
- [**学生自营平台类**](#学生自营平台类)
  - [**店铺（shop） API**](#店铺shop-api)
    - [创建店铺](#创建店铺)
    - [更新店铺](#更新店铺)
    - [获取店铺列表](#获取店铺列表)
    - [获取店铺信息](#获取店铺信息)
  - [**商品（product） API**](#商品product-api)
    - [创建商品（**有字段修改**）](#创建商品)
    - [更新商品（**有字段修改**）](#更新商品)
    - [获取商品列表（**有字段修改**）](#获取商品列表)
  - [**订单（purchase） API**](#订单purchase-api)
    - [创建订单](#创建订单)
    - [支付订单](#支付订单)
    - [取消订单](#取消订单)
    - [获取订单消息](#获取订单消息)
    - [获取订单列表](#获取订单列表)
- [**全局Status表**](#全局Status表)

> 注：main.py文件运行时需用 -c configpath 来指定配置文件路径。
## **Json的通用格式**

```python
{
  "id":"",
  "status":0,
  "type":"",
  "subtype":"",
  "data":{"key":"value"}
}
```

> **所需参数介绍：**

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



## **图片类**

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

#### 上传图片

> **API类型**

**请求类型：`POST`**

> **头像上传API地址：**

**https://www.zustservice.cn/api/external/pic**

> **POST发送请求的json文本**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"pic",
    "subtype":"upload",
    "data":{
        "from":"property"
        "base64":"图片base64数据"
        "name":"lalalala"
    }
}
```

> **data字段表**

|  参数  | 可否为空 | 可否缺省 | 数据类型 |       例子        | 字段长度限制 |                             备注                             |
| :----: | :------: | :------: | :------: | :---------------: | :----------: | :----------------------------------------------------------: |
|  from  |          |          |  string  |     property      |              | 图片来源，只有以下可选项：<br />"property":寻物启事&失物招领<br />"shop":店铺<br />"product":产品<br /> "portrait":头像<br /> |
| base64 |          |          |  string  | iVBORw0KGgoAA.... |              |                        图片base64数据                        |
|  name  |          |    √     |  string  |       pro1        |              | 如果name不设置的话将自动取图片MD5值作为图片名字，该名字将用于后期获取图片用。<br />**如果头像使用此api进行上传的话可以将name设置成用户学号** |



> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{
        "url":"./api/external/get/pic/property/a5466a1ce75e8043ab3bf5689fdec4aa",
    }
}
```

> ## 注意

+ 目前所有的头像图片是专门的COS对象储存服务器里

+ 图片文件大小限制在1024kb以下

+ type字段要准确


> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-500, # 错误码
  "message":"COS upload Error",
  "data":{},
}
```

#### 获取图片

> **API类型**

**请求类型：`GET`**

> **头像获取API地址：**

**https://www.zustservice.cn/api/external/get/pic/<j_from>/< name >**

> **GET发送请求的链接例子**

```python
https://www.zustservice.cn/api/external/get/pic/property/a5466a1ce75e8043ab3bf5689fdec4aa
```

+ `<j_from>`：图片来源
+ `<name>`：图片名称

> **Python端返回成功处理情况**

```python
返回图片的bytes数据
```

> ## 注意

+ 目前所有的头像图片是放在专门的COS对象储存服务器里，非码三秃的域名引用图片返回ban图片

+ id参数类型不正确，返回error图片

+ 若无任何返回则是后端炸了。

> **Python端返回失败处理情况**

```python
1.非码三秃域名获取图片时：返回ban图片
2.参数不正确或者名称所对应的的图片不存在：返回error图片
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

|     name     | data type | length | 不可空 | 可缺省 | 注释     |
| :----------: | :-------: | :----: | :----: | :----: | -------- |
|  shop_name   |  string   |  100   |   √    |        | 店铺名称 |
| shop_content |  string   |        |        |   √    | 店铺内容 |
|   user_id    |  big int  |   11   |   √    |        | 店主id   |

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

|     name     | data type | length | 不可空 | 可缺省 | 注释            |
| :----------: | :-------: | :----: | :----: | :----: | --------------- |
|   shop_id    |  big int  |   9    |   √    |        | 店铺id          |
| shop_content |  string   |        |        |        | 店铺内容        |
|   pic_url    |  string   |  512   |        |        | 店铺图片url地址 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"shop",
    "subtype":"update",
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

#### 获取店铺列表

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/get/shop?token={token值}**

> **data字段表**

|   name    | data type | length | 不可空 | 可缺省 | 注释                                                         |
| :-------: | :-------: | :----: | :----: | :----: | ------------------------------------------------------------ |
| shop_name |  string   |  100   |        |        | 店铺名关键字，模糊查找，返回包含该字段内容的所有记录。为空返回所有的店铺信息 |
|   order   |  string   |        |        |   √    | 排序规则，SQL语法规则：`字段+排序模式`。<br />字段：请看下方`返回JSON.data表`<br />排序模式：`ASC` 为升序，`DESC` 为降序<br />可用`AND`、`OR`和`( )`进行组合。<br />例子：`creat_time DESC` |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"shop",
    "subtype":"list",
    "data":{
        "shop_name":"小", # 店铺名关键字
        "order":"shop_id DESC" # 排序规则
    }
}
```

- `shop_name`为必传字段
- `order`为选传字段，不填默认按照记录添加顺序排序

> **返回JSON.data表**

|     name     | data type | length | 注释        |
| :----------: | :-------: | :----: | ----------- |
|   shop_id    |  big int  |   9    | 店铺id      |
|  shop_name   |  string   |  100   | 店铺名称    |
| shop_content |  string   |        | 店铺内容    |
|   user_id    |  big int  |   11   | 店主id      |
|  creat_time  | datetime  |        | 创建时间    |
|   pic_url    |  string   |  512   | 店铺图片url |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data": [
        {"shop_id": 811729970, "shop_name": "小码三秃", "shop_content": "码三秃团队的店铺2", "user_id": 1180310086, "user_name": "王凌超", "creat_time": "2019-07-14 17:15:08"}, 
        {"shop_id": 656019061, "shop_name": "五小灵童", "shop_content": "", "user_id": 1180310086, "user_name": "王凌超", "creat_time": "2019-07-14 17:15:44"}
    ]
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

| status |    message    |  内容  |
| :----: | :-----------: | :----: |
|   1    | Empty records | 空记录 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 获取店铺信息

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/get/shop?token={token值}**

> **data字段表**

|   name    | data type | length | 不可空 | 可缺省 | 注释             |
| :-------: | :-------: | :----: | :----: | :----: | ---------------- |
|  shop_id  |  big int  |   9    |   √    |   √    | 店铺id，二选一   |
| shop_name |  string   |  100   |   √    |   √    | 店铺名称，二选一 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"shop",
    "subtype":"info",
    "data":{
        "shop_id":"小码三秃", # 店铺名
    }
}
```

- 此请求为全字匹配检索，不同于上一个模糊检索。
- `shop_name`、`shop_name`两者必传一个字段
- 若两个字段都传，则使用`shop_id`进行检索

> **返回JSON.data表**

|     name     | data type | length | 注释        |
| :----------: | :-------: | :----: | ----------- |
|   shop_id    |  big int  |   9    | 店铺id      |
|  shop_name   |  string   |  100   | 店铺名称    |
| shop_content |  string   |        | 店铺内容    |
|   user_id    |  big int  |   11   | 店主id      |
|  creat_time  | datetime  |        | 创建时间    |
|   pic_url    |  string   |  512   | 店铺图片url |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data": {
        "shop_id": 811729970, 
        "shop_name": "小码三秃", 
        "shop_content": "码三秃团队的店铺2", 
        "user_id": 1180310086, 
        "creat_time": "2019-07-14 17:15:08"
    }
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

| status |    message    |  内容  |
| :----: | :-----------: | :----: |
|   1    | Empty records | 空记录 |

- 其他`status`码请看[全局Status表](#全局Status表)

### **商品（product） API**

#### 创建商品

> **API类型**

**请求类型：`POST`**

> **POST商品API地址**

**https://www.zustservice.cn/api/external/product?token={token值}**

> **data字段表**

|     name     | data type | length | 不可空 | 可缺省 | 注释     |
| :----------: | :-------: | :----: | :------: | :---------: | -------- |
| product_name |  string   |  100   | √        |            | 商品名称 |
| product_content |  string   |        |          | √ | 商品内容 |
| product_key | string     | 255 |          | √ | 商品关键字|
| product_price | float |  | √ | | 商品价格 |
|     shop_id     |  big int  |   9    |   √    |        | 店铺id     |
| pic_url | string | |  | √ | 商品封面 |
| product_status | int | | √ |  | 产品状态：<br />0.下架（默认）<br />1.上架<br />2.被删除 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"product",
    "subtype":"creat",
    "data":{
        "product_name":"测试商品1", # 商品名称
        "product_key":"测试商品", # 商品关键字
        "producy_content":"测试", # 商品内容
        "product_price":"100.5", # 商品价格
        "shop_id":811729970, # 店铺id
        "product_status":0
    }
}
```

- `product_id`在该API里不需要传入，哪怕传入也做无效处理，`product_id`为随机生成的7位id
- `product_name`、`product_price`、`shop_id`、`product_status`为必传字段，且不为空
- 若`shop_id`所对应的店主id并非token所对应的`user_id`，则该请求无效
- `user_id`修改为`int`类型变量
- `creat_time`、`update_time`在该API里不需要传入，哪怕传入也做无效处理，`update_time`为系统当前时间

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"product_id":4517733 # 长整数型}
}
```

- 返回7位的`product_id`

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

| status |       message       |                             内容                             |
| :----: | :-----------------: | :----------------------------------------------------------: |
|  100   | No right to operate | 无权操作，可能有以下原因：<br />1. 操作者不是店铺所有人<br />2. shop_id 错误 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 更新商品

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/product?token={token值}**

> **data字段表**

|        name        | data type | length | 不可空 | 可缺省 | 注释                                                     |
| :----------------: | :-------: | :----: | :----: | :----: | -------------------------------------------------------- |
|     product_id     |  big int  |   7    |   √    |        | 商品id                                                   |
|    product_name    |  string   |  100   |   √    |   √    | 商品名称                                                 |
|  product_content   |  string   |        |        |   √    | 商品内容                                                 |
|    product_key     |  string   |  255   |        |   √    | 商品关键字                                               |
|   product_price    |   float   |        |   √    |   √    | 商品价格                                                 |
|  product_disprice  |   float   |        |        |   √    | 商品折扣价                                               |
|    product_sale    |    int    |        |        |   √    | 商品销量                                                 |
|   product_click    |    int    |        |        |   √    | 商品点击量                                               |
| product_collection |    int    |        |        |   √    | 商品收藏量                                               |
|      shop_id       |  big int  |   9    |   √    |        | 店铺id                                                   |
|      pic_url       |  string   |        |        |   √    | 商品封面                                                 |
|   product_status   |    int    |        |   √    |        | 产品状态：<br />0.下架（默认）<br />1.上架<br />2.被删除 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"product",
    "subtype":"creat",
    "data":{
        "product_id":4517733,
        "shop_id":811729970,
        "product_status":1,
        "product_name":"头秃生发水",
        "product_content":"<h1>Duang~</h1>",
        "product_key":"生发|秃"
    }
}
```

- `product_id`、`shop_id`为必传字段，且不为空，仅做匹配使用，不可修改
- `product_status`为必传字段，且不为空
- 若`product_id`所属的`shop_id`并非请求所给的`user_id`，则该请求无效
- 若请求所给的`shop_id`所对应的`user_id`并非token所对应的`user_id`，则该请求无效
- `product_name`、`product_price`、`shop_id`为必传字段，且不为空
- `user_id`修改为`int`类型变量
- `creat_time`、`update_time`在该API里不需要传入，哪怕传入也做无效处理，`update_time`为系统当前时间

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

| status |       message       |                             内容                             |
| :----: | :-----------------: | :----------------------------------------------------------: |
|  100   | No right to operate | 无权操作，可能有以下原因：<br />1. 操作者不是店铺所有人<br />2.商品并不属于该店铺<br />2. shop_id 或 produc_id 错误 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 获取商品列表

> **API类型**

**请求类型：`POST`**

> **GET店铺API地址**

**https://www.zustservice.cn/api/external/get/product?token={token值}**

> **data字段表**

|     name     | data type | length | 不可空 | 可缺省 |                             注释                             |
| :----------: | :-------: | :----: | :----: | :----: | :----------------------------------------------------------: |
| product_name |  string   |  100   |        |   √    |                   商品名称，默认为全部商品                   |
| product_key  |  string   |  255   |        |   √    |                     商品关键字，默认为空                     |
|   shop_id    |  big int  |   9    |   √    |   √    |                    店铺id，默认为全体店铺                    |
|     type     |    int    |        |   √    |   √    | 商品状态，默认为`up`：<br />`down`：下架中<br />`up`：上架中<br />`all`：上架+下架商品<br />`del`：已删除 |
|    order     |  string   |        |        |   √    | 排序规则，默认按记录添加顺序排序<br />SQL语法规则：`字段+排序模式`。<br />字段：请看下方`返回JSON.data表`<br />排序模式：`ASC` 为升序，`DESC` 为降序<br />可用`AND`、`OR`和`( )`进行组合。<br />例子：`creat_time DESC` |

> **json请求格式**

```python
{
    "id":0,
    "status":0,
    "type":"product",
    "subtype":"list",
    "data":{
        "product_name":"测试商品",
        "product_key":"测试",
        "shop_id":811729970,
        "type":"all",
        "order":"creat_time ASC"
    }
}
```

+ `product_name`、`product_key`两者为模糊查找
+ `product_name`、`product_key`、`shop_id`三者条件为 `AND`关系

> **返回JSON.data表**

|        name        | data type | length | 注释       |
| :----------------: | :-------: | :----: | ---------- |
|     product_id     |  big int  |   7    | 商品id     |
|    product_name    |  string   |  100   | 商品名称   |
|  product_content   |  string   |        | 商品内容   |
|    product_key     |  string   |  255   | 商品关键字 |
|   product_price    |   float   |        | 商品价格   |
|  product_disprice  |   float   |        | 商品折扣价 |
|    product_sale    |    int    |        | 商品销量   |
|   product_click    |    int    |        | 商品点击量 |
| product_collection |    int    |        | 商品收藏量 |
|      shop_id       |  big int  |   9    | 店铺id     |
|     creat_time     | datetime  |        | 创建时间   |
|    update_time     | datetime  |        | 更新时间   |
|      pic_url       |  string   |        | 商品封面   |
|   product_status   |    int    |        | 商品状态   |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":[
        {"product_id": 7368397, "product_name": "测试商品2", "product_content": "这是一个测试商品", "product_key": "测试|商品", "product_price": 100.5, "product_disprice": null, "product_sale": 0, "product_click": 0, "product_collection": 0, "shop_id": 811729970, "creat_time": "2019-07-14 23:58:52", "update_time": "None", "product_pic": null, "product_status": 0}
    ]
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

#### 获取商品信息

> **API类型**

**请求类型：`POST`**

> **GET店铺API地址**

**https://www.zustservice.cn/api/external/get/product?token={token值}**

> **data字段表**

|    name    | data type | length | 不可空 | 可缺省 |   注释    |
| :--------: | :-------: | :----: | :----: | :----: | :-------: |
| product_id |    int    |   7    |        |        | 商品7位id |

> **json请求格式**

```python
{
    "id":0,
    "status":0,
    "type":"product",
    "subtype":"info",
    "data":{
        "product_id":5873413,
    }
}
```

> **返回JSON.data表**

|        name        | data type | length | 注释       |
| :----------------: | :-------: | :----: | ---------- |
|     product_id     |  big int  |   7    | 商品id     |
|    product_name    |  string   |  100   | 商品名称   |
|  product_content   |  string   |        | 商品内容   |
|    product_key     |  string   |  255   | 商品关键字 |
|   product_price    |   float   |        | 商品价格   |
|  product_disprice  |   float   |        | 商品折扣价 |
|    product_sale    |    int    |        | 商品销量   |
|   product_click    |    int    |        | 商品点击量 |
| product_collection |    int    |        | 商品收藏量 |
|      shop_id       |  big int  |   9    | 店铺id     |
|     creat_time     | datetime  |        | 创建时间   |
|    update_time     | datetime  |        | 更新时间   |
|      pic_url       |  string   |        | 商品封面   |
|   product_status   |    int    |        | 商品状态   |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{
        "product_id": 5873413, 
        "product_name": "\u65b9\u4fbf", 
        "product_content": "\u66f4\u4e0d\u80fd", 
        "product_key": null, 
        "product_price": 3.54, 
        "product_disprice": null, 
        "product_sale": 0, 
        "product_click": 0, 
        "product_collection": 0, 
        "shop_id": 474048217, 
        "creat_time": "2019-12-02 19:13:23", 
        "update_time": "2019-12-02 19:13:25", 
        "pic_url": "./api/external/get/pic/shop/5dbe81d1a473450506117c4abc924a35", 
        "product_status": 1
    }
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

| status |     message      |     内容     |
| :----: | :--------------: | :----------: |
|  100   | Error Product id | 错误的商品id |

- 其他`status`码请看[全局Status表](#全局Status表)

### **订单（purchase） API**

#### 创建订单

> **API类型**

**请求类型：`POST`**

> **POST商品API地址**

**https://www.zustservice.cn/api/external/purchase?token={token值}**

> **data字段表**

|        name        | data type | length | 不可空 | 可缺省 | 注释     |
| :----------------: | :-------: | :----: | :----: | :----: | -------- |
|     product_id     |    int    |   7    |   √    |        | 商品id   |
|    product_num     |    int    |        |   √    |        | 商品数量 |
| product_unitprice  |   float   |        |   √    |        | 商品单价 |
| product_totalprice |   float   |        |   √    |        | 商品总价 |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"purchase",
    "subtype":"apply",
    "data":{
        "product_id":4517733,
        "product_num":1,
        "product_unitprice":101.5,
        "product_totalprice":101.5
    }
}
```

- `product_id`7位商品id
- `creat_time`在该API里不需要传入，哪怕传入也做无效处理

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data":{"purchase_id": "15749511524517733"}
}
```

- 返回17位的文本型`purchase_id`

> **Python端返回失败处理情况**

```python
{
  "id":"请求时的ID",
  "status":-100, # 错误码
  "message":"Args Error",
  "data":{},
}
```

| status |       message        |     内容     |
| :----: | :------------------: | :----------: |
|  100   | Product_id not exist | 商品id不存在 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 支付订单

> **API类型**

**请求类型：`POST`**

> **POST商品API地址**

**https://www.zustservice.cn/api/external/purchase?token={token值}**

> **data字段表**

|    name     | data type | length | 不可空 | 可缺省 | 注释                         |
| :---------: | :-------: | :----: | :----: | :----: | ---------------------------- |
| purchase_id |  string   |   17   |   √    |        | 订单id                       |
|   method    |  string   |        |   √    |        | 支付途经，目前只支持`wallet` |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"purchase",
    "subtype":"pay",
    "data":{
		"purchase_id":"15749511524517733",
        "method":"wallet"
    }
}
```

- `purchase_id`17位订单id

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

| status |              message              |         内容         |
| :----: | :-------------------------------: | :------------------: |
|  100   |       Purchase id not exist       |     订单id不存在     |
|  101   |     Have no right to operate      |  订单存在但无权操作  |
|  102   |       Balance is not enough       |     用户余额不足     |
|  200   |       Pay method not allow        |    支付方法不允许    |
|  201   | This purchase is not paying state | 该订单不是待支付状态 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 取消订单

> **API类型**

**请求类型：`POST`**

> **POST商品API地址**

**https://www.zustservice.cn/api/external/purchase?token={token值}**

> **data字段表**

|    name     | data type | length | 不可空 | 可缺省 | 注释   |
| :---------: | :-------: | :----: | :----: | :----: | ------ |
| purchase_id |  string   |   17   |   √    |        | 订单id |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"purchase",
    "subtype":"cancel",
    "data":{
		"purchase_id":"15749511524517733",
    }
}
```

- `purchase_id`17位订单id

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

| status |              message              |         内容         |
| :----: | :-------------------------------: | :------------------: |
|  100   |       Purchase id not exist       |     订单id不存在     |
|  101   |     Have no right to operate      |  订单存在但无权操作  |
|  201   | This purchase is not paying state | 该订单不是待支付状态 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 获取订单信息

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/purchase?token={token值}**

> **data字段表**

|    name     | data type | length | 不可空 | 可缺省 | 注释 |
| :---------: | :-------: | :----: | :----: | :----: | ---- |
| purchase_id |    str    |   17   |   √    |        |      |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"purchase",
    "subtype":"info",
    "data":{
        "purchase_id":"15749511524517733", # 订单id
    }
}
```

> **返回JSON.data表**

|        name        | data type | length | 注释                                             |
| :----------------: | :-------: | :----: | ------------------------------------------------ |
|    purchase_id     |  string   |   17   | 订单id                                           |
|   purchase_state   |  string   |        | 订单状态<br>paying:支付中(默认状态)<br>待完善... |
|      user_id       |    int    |        | 购买者id                                         |
|   purchase_type    |    int    |        | 订单类型，默认为0                                |
|   purchase_price   |   float   |        | 订单总价格                                       |
|     creat_time     | datetime  |        | 创建时间                                         |
|     pay_method     |  string   |        | 支付方式，目前仅支持`wallet`                     |
|     product_id     |    int    |        | 产品id                                           |
|    product_num     |    int    |        | 产品数量                                         |
| product_unitprice  |   float   |        | 产品单价                                         |
| product_totalprice |   float   |        | 产品总价，一般与订单总价格一致                   |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data": {
        "purchase_id": "15749511524517733", 
        "purchase_state": "paying", 
        "user_id": 1180310086, 
        "purchase_type": 0, 
        "purchase_price": 101.5, 
        "creat_time": "2019-11-28 22:25:52", 
        "pay_method":"wallet"
        "product_id": 4517733, 
        "product_num": 1, 
        "product_unitprice": 101.5, 
        "product_totalprice": 101.5
    }
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

| status |         message          |                     内容                      |
| :----: | :----------------------: | :-------------------------------------------: |
|  100   |  Purchase id not exist   |                 订单id不存在                  |
|  101   | Have no right to operate |              订单存在但无权获取               |
|  102   |  Error purchase id num   |            错误的订单id数(超过1个)            |
|  103   |  Error purchase id num   | 意外出现在purchase_info表中purchase id 不存在 |

- 其他`status`码请看[全局Status表](#全局Status表)

#### 获取订单列表

> **API类型**

**请求类型：`POST`**

> **POST店铺API地址**

**https://www.zustservice.cn/api/external/purchase?token={token值}**

> **data字段表**

|    name     | data type | length | 不可空 | 可缺省 | 注释 |
| :---------: | :-------: | :----: | :----: | :----: | ---- |
| purchase_id |    str    |   17   |   √    |        |      |

> **json请求格式**

```python
{
    "id":事件ID, # 整数型
    "status":0,
    "type":"purchase",
    "subtype":"list",
    "data":{}
}
```

> **返回JSON.data表**

|      name      | data type | length | 注释                                             |
| :------------: | :-------: | :----: | ------------------------------------------------ |
|  purchase_id   |  string   |   17   | 订单id                                           |
| purchase_state |  string   |        | 订单状态<br>paying:支付中(默认状态)<br>待完善... |
|    user_id     |    int    |        | 购买者id                                         |
| purchase_type  |    int    |        | 订单类型，默认为0                                |
| purchase_price |   float   |        | 订单总价格                                       |
|   creat_time   | datetime  |        | 创建时间                                         |
|   pay_method   |  string   |        | 支付方式                                         |

> **Python端返回成功处理情况**

```python
{
    "id":请求时的ID, # 整数型
    "status":0,
    "message":"successful",
    "data": {
        "purchase_id": "15749511524517733", 
        "purchase_state": "paying", 
        "user_id": 1180310086, 
        "purchase_type": 0, 
        "purchase_price": 101.5, 
        "creat_time": "2019-11-28 22:25:52", 
        "pay_method":"wallet"
    }
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

| status |         message          |                     内容                      |
| :----: | :----------------------: | :-------------------------------------------: |
|  100   |  Purchase id not exist   |                 订单id不存在                  |
|  101   | Have no right to operate |              订单存在但无权获取               |
|  102   |  Error purchase id num   |            错误的订单id数(超过1个)            |
|  103   |  Error purchase id num   | 意外出现在purchase_info表中purchase id 不存在 |

- 其他`status`码请看[全局Status表](#全局Status表)

## **全局Status表**

| 参数 |              Message               |                内容                 | 请求类型  |
| :--: | :--------------------------------: | :---------------------------------: | --------- |
|  0   |                 OK                 |            函数处理正确             | POST、GET |
|  -1  |           Error JSON key           |         json文本必需key缺失         | POST      |
|  -2  |          Error JSON value          |          json文本value错误          | POST      |
|  -3  |           Error data key           |        data数据中必需key缺失        | POST      |
|  -4  |             Error Hash             |          Hash校验文本错误           | POST      |
| -100 |       Missing necessary args       |       api地址中缺少token参数        | POST、GET |
| -101 |            Error token             |             token不正确             | POST、GET |
| -102 |  Get userid failed for the token   |      使用该token获取userid失败      | POST、GET |
| -200 |    Failure to operate database     | 数据库操作失败，检查SQL语句是否正确 | POST、GET |
| -201 | Necessary key-value can't be empty |        关键键值对值不可为空         | POST      |
| -202 |  Missing necessary data key-value  |          缺少关键的键值对           | POST      |
| -203 |       Arg's value type error       |         键值对数据类型错误          | POST      |
| -204 |         Arg's value error          |           键值对数据错误            | POST      |
| -404 |           Unknown Error            |           未知的Redis错误           | POST      |
| -500 |          COS upload Error          |           COS储存上传失败           | POST      |

------

> `status`传递的错误码类型为整型。
>
> 验证码相关的错误码详见最下方表格。[短信错误码表](https://cloud.tencent.com/document/product/382/3771 "腾讯云短信API文档")



> ## Others
>
> 头像API仅测试使用。
>
> 