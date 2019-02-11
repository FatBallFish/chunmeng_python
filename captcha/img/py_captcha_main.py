# 导入图形模块，随机数模块
from PIL import Image,ImageDraw,ImageFont
import MD5
import random
import logging
import os,configparser
path=""
code_str = ""
webpath = ""
log_img = logging.getLogger("ImgCaptcha")

def Initialize():
    """
ImgCaptcha 模块初始化，此函数应在所有函数之前调用
    """
    global path
    cf = configparser.ConfigParser()
    cf.read("./config.ini")
    path = cf.get("Main","ImgCaptchaAddr")
    if path == "":
        os.makedirs("captcha", exist_ok=True)
        path = "./captcha"
        log_img.info("【Initialize】ImgCaptchaAddr not located,use the default config")
    else:
        try:
            os.makedirs(path, exist_ok=True)
            log_img.info("【Initialize】Located ImgCaptcha address:[%s]",path)
        except Exception as e:
            log_img.error("【Initialize】UnknownError:",e)
    log_img.info("【Initialize】Module ImgCaptcha loaded")

def CreatCode(font:str = "military_font.ttf")->tuple:
    """
创建一个验证码图片文件，返回文件名（*.png）
    :param font: 字体文件名
    :return: 元组，(验证码内容，验证码文件名)
    """
    global code_str
    global webpath,path
    code_str = ""
    # 定义使用image类实例化一个长为120px，宽为30px，基于RGB的（255，255，255）颜色的图片
    img1 = Image.new(mode="RGB",size=(120,30),color=(255,255,255))
    # 实例化一支画笔
    draw1 = ImageDraw.Draw(img1,mode="RGB")
    # 定义要使用的字体,第一个参数表示字体的路径,第二个参数表示字体大小
    try:
        font1 = ImageFont.truetype(font,28)
    except:
        log_img.error("【CreatCode】Failed to load font [%s]",font)
        print("Failed to load font [%s]"%font)
        return "Error"

    for i in range(5):
        # 每循环一次，从a到z中随机生成一个字母或数字
        # 使用ASCII码，A-Z为65-90，a-z为97-122，0-9为48-57,使用chr把生成的ASCII码转换成字符
        # str 把生成的数字转换成字符串
        char1 = random.choice([chr(random.randint(65,90)),chr(random.randint(48,57)),chr(random.randint(97,122))])
        code_str += char1
        # 每循环一次重新生成随机颜色
        color1 = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        # 把生成的字母或者数字添加到图片上
        # 图片长度为120px，要生成5个数字或字母则每添加一个，其位置就要向后移动24px
        if random.randint(0,1):
            draw1.line((0,random.randint(0,30),120,random.randint(0,30)),color1,0)
        draw1.text([i*20+10,5],char1,color1,font1)
    #print(code_str)
    # 把生成的图片保存为“pic.png”格式，文件名通过加盐获得

    file_name = "%s.png"%MD5.md5(code_str)
    file_path = os.path.join(path,file_name)
    try:
        with open(file_path, "wb") as f:
            try:
                img1.save(f, format="png")
            except:
                log_img.error("【CreatCode】Failed to save captcha img [%s]",path)
                return "Error"
        log_img.info("【CreatCode】Created a captcha [%s]",code_str)
        return (code_str,file_name)
    except:
        log_img.error("【CreatCode】Failed to open/write captcha img [%s]",path)
        return "Error"
def GetCodeText()->str:
    """
返回验证码内容
    :return: 验证码内容
    """
    return code_str

def GetCodePath()->str:
    """
返回验证码保存目录
    :return: 验证码保存目录
    """
    return path

if __name__ == "__main__":
    CreatCode()