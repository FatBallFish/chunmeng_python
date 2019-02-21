from flask import Flask,request
from img import py_captcha_main as ImgCaptcha
from sms import py_sms_main as SmsCaptcha
from configparser import ConfigParser
import random,MD5
import json,redis
import logging
import sys,getopt

app = Flask(__name__)
def Initialize(argv:list):
    """
websockets 模块初始化，此函数应在所有命令之前调用
    :param argv: 命令行参数表
    """
    # print("Enter the function")
    global Redis,config_addr
    r_host = "localhost"
    r_port = 6379
    r_db = 0
    r_pass = ""
    try:
        opts,args = getopt.getopt(argv,"hi:",["imgaddr=","help"])
    except getopt.GetoptError:
        print("test.py -i <ImgCaptchaAddr> -s <SmsCaptchaAddr>")
        sys.exit(2)
    for opt,arg in opts:
        # print("opt,arg",opt,arg)
        if opt in ("-h","--help"):
            print("-"*80)
            print("-h or --help      Show this passage.")
            print("-c or --config    Configuration file path")
            print("-"*80)
            sys.exit()
        elif opt in("-c","--config"):
            config_addr = str(opt)
            break
        else:
            log_main.warning("Useless argv:[%s|%s]",opt,arg)
            print("Useless argv:[%s|%s]"%(opt,arg))
    else:
        log_main.error("missing config argv")
        print("missing config argv")
        log_main.info("Program Ended")
        sys.exit()
    cf = ConfigParser()
    try:
        cf.read(config_addr)
    except Exception as e:
        log_main.error("Error config file path")
        print("Error config file path")
        log_main.info("Program Ended")
        sys.exit()
    sections = cf.sections()
    for section in sections:
        if section in ["ImgCaptcha","Redis","SmsCaptcha"]:
            break
    else:
        log_main.error("Config file missing some necessary sections")
        print("Config file missing some necessary sections")
        log_main.info("Program Ended")
        sys.exit()

    try:
        r_host = cf.get("Redis","host")
        r_port = cf.get("Redis","port")
        r_db = cf.get("Redis", "db")
        r_pass = cf.get("Redis","pass")
    except Exception as e:
        log_main.error(e)
        print(e)
        log_main.info("Program Ended")
        sys.exit()

    try:
        Redis = redis.Redis(host=r_host,port=r_port,db=r_db,password=r_pass)
    except Exception as e:
        log_main.error(e)
        print(e)
        log_main.info("Program Ended")
        sys.exit()
    # ------模块初始化------
    ImgCaptcha.Initialize()
    SmsCaptcha.Initialize()


@app.route("/api/captcha",methods=["POST"])
def captcha():
    data = request.json
    # 先获取json里id的值，若不存在，默认值为-1
    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1
    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type","subtype","data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id":id,"status":-1,"message":"Error JSON key","data":{}})
    # 处理json
    if data["type"] == "img":
        if data["subtype"] == "generate":
            data = data["data"]
            title,addr = ImgCaptcha.CreatCode()
            rand_str = ""
            for i in range(5):
                char1 = random.choice(
                    [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                rand_str += char1
            # status 0 ImgCaptcha生成成功

            return json.dumps({
                "id":id,
                "status":0,
                "message":"Successful",
                "data":{"title":title,"addr":addr,"rand":rand_str}
            })
        elif data["subtype"] == "delete":
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    elif data["type"] == "sms":
        if data["subtype"] == "generate":
            pass
        elif data["subtype"] == "delete":
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


if __name__ == '__main__':
    # -------------------主程序初始化-------------------
    ImgCaptchaAddr = ""
    LOG_FORMAT = "[%(asctime)-15s] - [%(name)10s]\t- [%(levelname)s]\t- [%(funcName)-20s:%(lineno)3s]\t- [%(message)s]"
    DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
    logging.basicConfig(filename="my.log", level=logging.INFO,
                        format=LOG_FORMAT.center(30),
                        datefmt=DATA_FORMAT)
    log_main = logging.getLogger(__name__)
    Initialize(sys.argv[1:])