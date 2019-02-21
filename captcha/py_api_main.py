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
    global r,config_addr
    try:
        opts,args = getopt.getopt(argv,"hc:",["config","help"])
    except getopt.GetoptError:
        print("test.py -c <ConfigFilePath> -h <help>")
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
            config_addr = str(arg)
            print("config_addr:",config_addr)
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
        r = redis.Redis(host=r_host,port=r_port,db=r_db,password=r_pass)
    except Exception as e:
        log_main.error(e)
        print(e)
        log_main.info("Program Ended")
        sys.exit()
    # ------模块初始化------
    ImgCaptcha.Initialize(config_addr)
    SmsCaptcha.Initialize(config_addr)


@app.route("/captcha",methods=["POST"])
def captcha():
    data = request.json
    print(data)
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
            code,addr = ImgCaptcha.CreatCode()
            rand_str = ""
            for i in range(5):
                char1 = random.choice(
                    [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                rand_str += char1
            # status 0 ImgCaptcha生成成功
            # r.sadd("ImgCaptcha",title)
            return json.dumps({
                "id":id,
                "status":0,
                "message":"Successful",
                "data":{"code":code,"addr":addr,"rand":rand_str}
            })
        elif data["subtype"] == "delete":
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status":-2, "message": "Error JSON value", "data": {}})
    elif data["type"] == "sms":
        if data["subtype"] == "generate":
            data = data["data"]
            phone = str(data["phone"])
            code = random.randint(10000,99999)
            result = SmsCaptcha.SendCaptchaCode(phone,code,ext=str(id))
            status = result["result"]
            message = result["errmsg"]
            if message == "OK":
                message = "Successful"
            rand_str = ""
            if status == 0:
                for i in range(5):
                    char1 = random.choice(
                        [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                    rand_str += char1
                # status 0 SmsCaptcha生成成功
                # r.sadd("SmsCaptcha",title)
                return json.dumps({
                    "id": id,
                    "status": status,
                    "message": message,
                    "data": {"code": code,"rand": rand_str}
                })
            else:
                # status=result["result"] 遇到错误原样返回腾讯云信息
                return json.dumps({
                    "id": id,
                    "status": status,
                    "message": message,
                    "data": {}
                })
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
    app.run("127.0.0.1",port=8080,debug=True)