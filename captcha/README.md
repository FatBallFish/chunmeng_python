# 验证码API文档

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
|subtype|请求子类型|请求|"subtype":"login|
|data|传送数据|请求、返回|"data":{"token":"xxxxxxxxxxxxx"}|

> ## **用户操作类**

#API测试链接：https://www.lcworkroom.cn/api/captcha

 + ### **登录图片验证码**
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
           "code":"N4Fsx", # 验证码内容
           "addr":"1ed39d9793fdddb95ac32512ce0089cb.png",
           "rand":"CST43"  #随机文本
       }
   }
   ```
   > ##注意：
   > 1.id字段需是整型数据。若是文本型数字数据，返回时自动转换成整数型数据；若是非数字型文本，则返回-1。id用于让前端在服务繁忙时能够对应服务;\
   > 2.Python成功返回时的addr为验证码文件名，由MD5加盐加密获得，验证码所在目录由nginx传递给前端，前端获得文件名后再进行拼接;\
   > 3.rand 为随机字符串，前端获得验证码后需要将验证码和rand文本一并传给java端进行验证。

   + **Python端返回失败处理情况**
   ```python
   {
     "id":"请求时的ID",
     "status":1000, # 错误码
     "message":"验证码文件创建失败",
     "data":{},
   }
   ```
   > status传递的错误码类型为整型。具体的错误码详见最下方表格。
---
+ ### **注册手机验证码**
    + **POST发送请求的json文本**
    ```python
    {
        "id":事件ID,
        "status":0,
        "type":"sms",
        "subtype":"generate",
        "data":{
            "phone":"137xxxxxxxx",
            }
    }
    ```
    > ##注意
    > phone 字段需用文本型传递，且只能为中国大陆手机号，不支持国外手机号
   + **Python端返回成功处理情况**
   ```python
   {
      "id":请求时的ID,
      "status":0,
      "message":"successful",
      "data":{
          "title":"88464", # 验证码内容
          "rand":"DSf4s"
      }
   }
   ```
   > ##注意：
   > 1.Python成功返回时的addr为验证码文件名，由MD5加盐加密获得。\
   > 2.rand 为随机字符串，前端获得验证码后需要将验证码和rand文本一并传给java端进行验证。\
   > **3.手机验证码的时效为5min，具体怎么实现还没想好**
   
   + **Python端返回失败处理情况**
   ```python
   {
        "id":"请求时的ID",
        "status":1016,  #错误码
        "message":"手机号格式错误",
        "data":{},
   }
   ```
   > ##注意
   > status传递的错误码类型为整型。具体的错误码参照**腾讯云短信服务API文档**。
   > [短信错误码](https://cloud.tencent.com/document/product/382/3771 "腾讯云短信API文档")

---
## status表
|参数|Message|内容|
|:--:|:--:|:--:|
|0|OK|函数处理正确|
|-1|Error JSON key|json文本必需key缺失|
|-2|Error JSON value|json文本value错误|

---

> ## Others
> github里的例程已设置成本地测试。\
> 若要修改成网络测试，将“py_api.main.py”第最后一行的host和port进行相应修改。\
> 网络测试直接打开下列网址即可，已在服务器部署了服务。
> [测试链接](http://www.lcworkroom.cn/api/captcha "本小宅")