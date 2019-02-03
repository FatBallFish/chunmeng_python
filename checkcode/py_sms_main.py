from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from PIL import Image,ImageDraw,ImageFont
import random

class SMS(object):
    def __init__(self):
        # 短信应用SDK AppID
        self.appid = 1400097031
        # 短信应用SDK AppKey
        self.appkey = '417a2a23700289bf50f6cff4fdefa467'
        # 定义单发信息组件
        self.ssender = SmsSingleSender(self.appid, self.appkey)

    def SendCheckCode(self,phone_number, checkcode):
        """
        向指定手机号发送指定验证码，返回证验证结果

        :return: 字典，返回证验证结果。例：{'result': 0, 'errmsg': 'OK', 'ext': '', 'sid': '8:e5CXsVN8994a8ukmfeG20190202', 'fee': 1}
        :param phone_number: 接受验证码的手机号码，文本型
        :param checkcode: 将要发送的验证码内容，文本型
        """
        # 需要发送短信的手机号码
        # phone_numbers = ["13750687010","13566284913","17677386094"]
        # 短信模板ID，需要在短信应用中申请
        template_id = 176189  # 验证码模版id
        # 签名
        # NOTE: 这里的签名"腾讯云"只是一个示例，真实的签名需要在短信控制台中申请，另外签名参数使用的是`签名内容`，而不是`签名ID`
        sms_sign = "本小宅"
        # print("checkcode:",checkcode)
        # 模版参数，具体根据短信模版中定义的参数进行
        params = ["注册账号", checkcode, 5]
        try:
            result = self.ssender.send_with_param(86, phone_number, template_id, params, sign=sms_sign, extend="", ext="")
            # 签名参数未提供或者为空时，会使用默认签名发送短信
        except HTTPError as e:
            # print(e)
            return e
        except Exception as e:
            # print(e)
            return e
        # print(result)
        return result

class ImgCheckcode(object):
    def __init__(self):
        self.code_str = ""
        self.webpath = ""

    def CreatCode(self):
        """
        创建一个120px*30px的五位随机验证码

        :return: 元组，（验证码内容，验证码网络地址）
        """
        self.code_str = ""
        # 定义使用image类实例化一个长为120px，宽为30px，基于RGB的（255，255，255）颜色的图片
        img1 = Image.new(mode="RGB",size=(120,30),color=(255,255,255))
        # 实例化一支画笔
        draw1 = ImageDraw.Draw(img1,mode="RGB")
        # 定义要使用的字体,第一个参数表示字体的路径,第二个参数表示字体大小
        font1 = ImageFont.truetype("military_font.ttf",28)
        for i in range(5):
            # 每循环一次，从a到z中随机生成一个字母或数字
            # 使用ASCII码，A-Z为65-90，a-z为97-122，0-9为48-57,使用chr把生成的ASCII码转换成字符
            # str 把生成的数字转换成字符串
            char1 = random.choice([chr(random.randint(65,90)),chr(random.randint(48,57)),chr(random.randint(97,122))])
            self.code_str += char1
            # 每循环一次重新生成随机颜色
            color1 = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            # 把生成的字母或者数字添加到图片上
            # 图片长度为120px，要生成5个数字或字母则每添加一个，其位置就要向后移动24px
            if random.randint(0,1):
                draw1.line((0,random.randint(0,30),120,random.randint(0,30)),color1,0)
            draw1.text([i*20+10,5],char1,color1,font1)
        # print(self.code_str)
        # 把生成的图片保存为“pic.png”格式
        path = ".\\checkcode\\%s.png" % self.code_str
        self.webpath = "www.lcworkroom/checkcode/%s.png" % self.code_str
        with open(path, "wb") as f:
            img1.save(f, format="png")
        return (self.code_str,self.webpath)

    def GetCodeText(self):
        """
        取上次生成的验证码的内容

        :return: 文本型，验证码内容
        """
        return self.code_str

    def GetCodePath(self):
        """
        取上次生成的验证码网络地址

        :return: 文本型，验证码网络地址
        """
        return self.webpath
if __name__ == "__main__":
    # sms = SMS()
    # result = sms.SendCheckCode("13750687010", "1234")
    # print(result)
    imgcode = ImgCheckcode()
    imgcode.CreatCode()
    print(imgcode.code_str,imgcode.webpath)

