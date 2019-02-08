# Python与Java的websocket传输交互json
---

[TOC]

### Json的通用格式：

'''

    {
        "id":"",
        "status":"",
        "type":"",
        "subtype":"",
        "data":{
            "message":"",
            ...
            }
    }
    
'''

所需参数介绍：

|参数|介绍|样例|
|:--:|:--:|:--:|
|id|事件处理id，请求端发送，接收端返回时原样返回|"id":"123456"|
|status|返回请求处理状态，请求时可不填。默认返回0时为请求处理成功，若失败返回错误码|"status":""|
|type|请求类型|"type":"user"|
|subtype|请求子类型|"subtype":"login|
|data|传送数据|"data":{"action":"imgcaptcha"}|


> ## **用户操作类**
 + 登录图片验证码
    + Java端发送请求
    
    '''
    
        {
            "id":"事件ID"
            "status":"",
            "type":"user",
            "subtype"："login",
            "data":{
                "action":"imgcaptcha"
                }
        }
    
    '''
   + Python端返回成功处理情况
   
   '''
   
       {
            "id":"请求时的ID",
            "status"："0",
            "errmsg":"OK",
            "data":{
                "title":"N4Fsx", # 验证码内容
                "addr":"/captcha/N4Fsx.png"
                }
       }
       
   '''
   > 注意：Python成功返回时的addr由systemd传递的参数为准，文件名暂定为验证码内容，可能会有改变。
   
   + Python端返回失败处理情况
   
   '''
   
        {
            "id":"请求时的ID"，
            "status":"0001", # 错误码
            "errmsg":"验证码文件创建失败",
            "data":{},
        }
        
   '''
   > 具体的错误码详见最下方表格。
   

---

> ## Others
> github里的例程已设置成本地测试。
> 若要修改成网络测试，将“py_captcha.main.py”第39，40行的path和webpath进行相应修改。
> webpath注意斜杠方向；将”html_web.html“第64行改成相应地址。
> 网络测试直接打开下列网址即可，已在服务器部署了服务。
> http://www.lcworkroom.cn/captcha.html