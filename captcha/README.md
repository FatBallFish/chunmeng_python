# Python与Java的websocket传输交互json

### Json的通用格式：

```python
{
  "id":"",
  "status":"",
  "type":"",
  "subtype":"",
  "data":{"message":""}
}
```
**所需参数介绍：**

|参数|介绍|调用方|样例|
|:--:|:--:|:--:|:--:|
|id|事件处理id，请求端发送，接收端返回时原样返回|请求、返回|"id":"123456"|
|status|返回请求处理状态，请求时可不填。默认返回0时为请求处理成功，若失败返回错误码|请求、返回|"status":""|
|message|状态简略信息，若成功调用则显示"successful"|返回|"message":"successful"|
|type|请求类型|请求|"type":"user"|
|subtype|请求子类型|请求|"subtype":"login|
|data|传送数据|请求、返回|"data":{"action":"imgcaptcha"}|

> ## **用户操作类**
 + ### **登录图片验证码**
    + **Java端发送请求**
   ```python
   {
       "id":"事件ID",
       "status":"",
       "type":"captcha",
       "subtype":"img",
       "data":{
           "action":"generate" # 生成img验证码
       }
   }
   ```
   + **Python端返回成功处理情况**
   ```python
   {
       "id":"请求时的ID",
       "status":"0",
       "errmsg":"successful",
       "data":{
           "title":"N4Fsx", # 验证码内容
           "addr":"1ed39d9793fdddb95ac32512ce0089cb.png"
       }
   }
   ```
   > 注意：Python成功返回时的addr为验证码文件名，由MD5加盐加密获得。
   
   + **Python端返回失败处理情况**
   ```python
   {
     "id":"请求时的ID",
     "status":1000, # 错误码
     "errmsg":"验证码文件创建失败",
     "data":{},
   }
   ```
   > status传递的错误码类型为整型。具体的错误码详见最下方表格。
---
+ ### **注册手机验证码**
    + **Java端发送请求**
    ```python
    {
        "id":"事件ID",
        "status":"",
        "type":"captcha",
        "subtype":"sms",
        "data":{
            "action":"generate", # 生成sms验证码
            "phone":"137XXXXXXXX"
            }
    }
    ```
    > phone 字段需用文本型传递，且只能为中国大陆手机号，不支持国外手机号
   + **Python端返回成功处理情况**
   ```python
   {
      "id":"请求时的ID",
      "status":"0",
      "errmsg":"successful",
      "data":{
          "title":"8846" # 验证码内容
      }
   }
   ```
   > 注意：Python成功返回时的addr为验证码文件名，由MD5加盐加密获得。
   
   + **Python端返回失败处理情况**
   ```python
   {
        "id":"请求时的ID",
        "status":1000,  #错误码
        "errmsg":"手机号不存在",
        "data":{},
   }
   ```
   > status传递的错误码类型为整型。具体的错误码参照**腾讯云短信服务API文档**。
   > [短信错误码](https://cloud.tencent.com/document/product/382/3771 "腾讯云短信API文档")


---

> ## Others
> github里的例程已设置成本地测试。
> 若要修改成网络测试，将“py_captcha.main.py”第39，40行的path和webpath进行相应修改。
> webpath注意斜杠方向；将”html_web.html“第64行改成相应地址。
> 网络测试直接打开下列网址即可，已在服务器部署了服务。
> [测试链接](http://www.lcworkroom.cn/captcha.html "本小宅")