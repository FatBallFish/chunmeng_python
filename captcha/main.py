from flask import Flask,request,render_template
from img import py_captcha_main as ImgCaptcha
from sms import py_sms_main as SmsCaptcha
from COS import py_cos_main as COS
from configparser import ConfigParser
import random,MD5
import json,redis
import logging
import sys,getopt
import threading,time
import os
import base64

app = Flask(__name__)
imgcaptcha_list = []  #{"hash":hash,"TTL":180}
smscaptcha_list = []  #{"hash":hash,"TTL":180}

LOG_FORMAT = "[%(asctime)-15s] - [%(name)10s]\t- [%(levelname)s]\t- [%(funcName)-20s:%(lineno)3s]\t- [%(message)s]"
DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
log_outpath = "./my.log"
Main_filepath = os.path.dirname(os.path.abspath(__file__))
print("Main FilePath:",Main_filepath)

def Initialize(argv:list):
    """
模块初始化，此函数应在所有命令之前调用
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
            # log_main.warning("Useless argv:[%s|%s]",opt,arg)
            print("Useless argv:[%s|%s]"%(opt,arg))
    else:
        # log_main.error("missing config argv")
        print("missing config argv")
        # log_main.info("Program Ended")
        sys.exit()
    cf = ConfigParser()
    try:
        cf.read(config_addr)
    except Exception as e:
        ##log_main.error("Error config file path")
        print("Error config file path")
        ##log_main.info("Program Ended")
        sys.exit()
    sections = cf.sections()
    for section in sections:
        if section in ["Log","Redis","SmsCaptcha"]:
            break
    else:
        ##log_main.error("Config file missing some necessary sections")
        print("Config file missing some necessary sections")
        ##log_main.info("Program Ended")
        sys.exit()

    # 读main配置
    # TODO CONFIG
    global log_main
    try:
        global log_outpath, webhost, webport, webdebug
        log_outpath = cf.get("Main", "logoutpath")
        webhost = cf.get("Main", "webhost")
        webport = cf.get("Main", "webport")
        intdebug = cf.get("Main", "webdebug")
        if intdebug == 1:
            webdebug = True
        else:
            webdebug = False
        print("log_outpath:",log_outpath)
        print("webhost:",webhost)
        print("webport:", webport)
        print("webdebug:", webdebug)
    except Exception as e:
        print("Error")
    logging.basicConfig(filename=log_outpath, level=logging.INFO,
                        format=LOG_FORMAT.center(30),
                        datefmt=DATA_FORMAT)
    log_main = logging.getLogger(__name__)
    # 读Redis配置
    try:
        r_host = cf.get("Redis","host")
        r_port = cf.get("Redis","port")
        r_db = cf.get("Redis", "db")
        r_pass = cf.get("Redis","pass")
        global r_imgsetname,r_smssetname
        r_imgsetname = cf.get("Redis","img_setname")  #TODO global setname
        r_smssetname = cf.get("Redis","sms_setname")
        print("RedisHost:",r_host)
        print("RedisPort:", r_port)
        print("RedisDB:", r_db)
        print("RedisImgsetname:", r_imgsetname)
        print("RRedisSmssetname:", r_smssetname)
    except Exception as e:
        log_main.error(e)
        print(e)
        log_main.info("Program Ended")
        sys.exit()

    # 启动Redis 并初始化验证码库
    try:
        r = redis.StrictRedis(host=r_host,port=r_port,db=r_db,password=r_pass)
    except Exception as e:
        log_main.error(e)
        print(e)
        log_main.info("Program Ended")
        sys.exit()
    try:
        r.delete(r_imgsetname)
        print("Delete Redis's set [%s]" % r_imgsetname)
    except Exception as e:
        pass
    try:
        r.delete(r_smssetname)
        print("Delete Redis's set [%s]" % r_smssetname)
    except Exception as e:
        pass
    # ------模块初始化------
    ImgCaptcha.Initialize(config_addr,Main_filepath)
    SmsCaptcha.Initialize(config_addr,Main_filepath)
    COS.Initialize(config_addr,Main_filepath)


class MyThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        log_main.info("Start thread 【%s】 to auto del outtime code"%self.name)
        print ("开始线程：" + self.name)
        auto_del_code()
        log_main.info("End thread 【%s】 to auto del outtime code"%self.name)
        print ("退出线程：" + self.name)

def auto_del_code():
    while True:
        for imgcaptcha in imgcaptcha_list:
            if r.sismember(r_imgsetname, imgcaptcha["hash"]) == False:
                print("imghash:[%s]had deleted" % imgcaptcha["hash"])
                imgcaptcha_list.remove(imgcaptcha)
                continue
            # print("imghash:", imgcaptcha["hash"], "sis:", )
            if imgcaptcha["TTL"] <= 0:
                try:
                    print("Try to remove hash [%s]" % imgcaptcha["hash"])
                    r.srem(r_imgsetname,imgcaptcha["hash"])
                except Exception as e:
                    log_main.error(e)
                    print(e)
                index = imgcaptcha_list.index(imgcaptcha)
                imgcaptcha_list.pop(index)
                continue
            imgcaptcha["TTL"] -= 3
            # print(imgcaptcha["hash"],imgcaptcha["TTL"])
        for smscaptcha in smscaptcha_list:
            if r.sismember(r_smssetname, smscaptcha["hash"]) == False:
                print("smshash:[%s]had deleted" % smscaptcha["hash"])
                smscaptcha_list.remove(smscaptcha)
                continue
            if smscaptcha["TTL"] <= 0:
                try:
                    print("Try to remove hash [%s]" % smscaptcha["hash"])
                    r.srem(r_smssetname,smscaptcha["hash"])
                except Exception as e:
                    log_main.error(e)
                    print(e)
                index = smscaptcha_list.index(smscaptcha)
                smscaptcha_list.pop(index)
                continue
            smscaptcha["TTL"] -= 3
            # print(smscaptcha["hash"], smscaptcha["TTL"])
        time.sleep(3)

def SafeCheck(hash):
    """
    Check imgcaptcha hash
    :param hash:
    :return: int 0 as success , -1 as failed
    """
    flag = False
    for imgcaptcha in imgcaptcha_list :
        if imgcaptcha["hash"] == hash:
            flag = True
            imgcaptcha["TTL"] = 180
        else:
            pass
    for smscaptcha in smscaptcha_list :
        if smscaptcha["hash"] == hash:
            flag = True
            smscaptcha["TTL"] = 180
        else:
            pass
    if flag == True:
        return 0
    else:
        return -1

@app.route("/captcha",methods=["POST"])
def captcha():
    data = request.json
    print(data)

    # 先获取json里id的值，若不存在，默认值为-1
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})

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
            # code,addr = ImgCaptcha.CreatCode()
            code, b64_data = ImgCaptcha.CreatCode()
            code = code.lower()  # 将所有的验证码转成小写
            rand_str = ""
            for i in range(5):
                char1 = random.choice(
                    [chr(random.randint(65, 90)), chr(random.randint(48, 57)), chr(random.randint(97, 122))])
                rand_str += char1
            hash = MD5.md5(code,salt=rand_str)
            try:
                r.sadd(r_imgsetname,hash)
                imgcaptcha_list.append({"hash":hash,"TTL":180})
                # todo 加入验证机制
            except Exception as e:
                log_main.error(e)
                print(e)
                # status -404 Unkown Error
                return json.dumps({
                    "id": id,
                    "status": -404,
                    "message": "Unknown Error",
                    "data":{}
                })
            # status 0 ImgCaptcha生成成功
            # return json.dumps({
            #     "id":id,
            #     "status":0,
            #     "message":"Successful",
            #     "data":{"code":code,"addr":addr,"rand":rand_str}
            return json.dumps({
                "id": id,
                "status": 0,
                "message": "Successful",
                "data": {"imgdata": b64_data, "rand": rand_str}
                # 改动：将code字段删除
            })
        elif data["subtype"] == "validate":
            data = data["data"]
            for key in data.keys():
                if key not in ["hash"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            hash = data["hash"]
            result = SafeCheck(hash)
            if result == 0:
                # status 0 校验成功。
                return json.dumps({
                    "id":id,
                    "status":0,
                    "message":"successful",
                    "data":{}
                })
            elif result == -1:
                # status -1 验证码hash值不匹配(包括验证码过期)。
                return json.dumps({
                    "id": id,
                    "status": -1,
                    "message": "Error captcha hash",
                    "data": {}
                })
            else:
                # status -404 Unkown Error
                return json.dumps({
                    "id": id,
                    "status": -404,
                    "message": "Unknown Error",
                    "data": {}
                })
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status":-2, "message": "Error JSON value", "data": {}})
    elif data["type"] == "sms":
        if data["subtype"] == "generate":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone","hash"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            hash = data["hash"]
            result = SafeCheck(hash)
            if result != 0:
                # status -4 json的value错误。
                return json.dumps({"id": id, "status": -4, "message": "Error Hash", "data": {}})
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
                hash = MD5.md5(code, salt=rand_str)
                try:
                    r.sadd(r_smssetname,hash)  #todo
                    smscaptcha_list.append({"hash": hash, "TTL": 180})
                    # todo 加入验证机制
                except Exception as e:
                    log_main.error(e)
                    print(e)
                    # status -404 Unkown Error
                    return json.dumps({
                        "id": id,
                        "status": -404,
                        "message": "Unknown Error",
                        "data": {}
                    })
                # status 0 SmsCaptcha生成成功
                return json.dumps({
                    "id": id,
                    "status": status,
                    "message": message,
                    "data": {"rand": rand_str}
                })
                # 改动：将code字段删除
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

@app.route("/portrait",methods=["POST"])
def portrait():
    data = request.json
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})

    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    type = data["type"]
    subtype = data["subtype"]

    # 处理json
    if type == "portrait":
        if subtype == "upload":
            data = data["data"]
            name = data["name"]
            id2 = data["id"]  # 账号id
            img_base64 = str(data["base64"])
            img_base64 = img_base64.partition(";base64,")[2]
            # print("-------接收到数据-------\n", img_base64, "\n-------数据结构尾-------")
            type = data["type"]
            img_file = base64.b64decode(img_base64)
            try:
                COS.bytes_upload(img_file,"portrait/{}".format(id2))
            except Exception as e:
                print(e)
                log_main.error(e)


            # with open("./{}_{}.{}".format(id,name,type),"wb") as f:
            #     f.write(img_file)
            #     print("{}_{}.{}".format(id,name,type),"写出成功！")
            # status 0 成功。
            return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {
                "url": "./api/external/get/portrait/{}".format(id2)}})
        elif subtype == "updata":
            pass
@app.route("/get/portrait/<id>")
def get_portrait(id):
    ip = request.remote_addr
    # print("The client ip is :",ip)
    # srchead = "data:;base64,"
    # import base64
    print("id:", id)
    id = str(id)
    if id.isdigit():
        # print("Try to get portrait data:{}".format(id))
        try:
            data = COS.bytes_download("portrait/{}".format(id))
        except Exception as e:
            print(e)
            log_main.error(e)
            try:
                path = os.path.join(Main_filepath,"data/image/default.jpg")
                with open(path,"rb") as f :
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("Error:Can't load the default img.")
                log_main.error("Error:Can't load the default img.")
                data = ""
        return data
    else:
        try:
            path = os.path.join(Main_filepath, "data/image/error.jpg")
            with open(path,"rb") as f:
                data = f.read()
            # data = COS.bytes_download("portrait/error")
        except Exception as e:
            print("Error:Can't load the error img.")
            log_main.error("Error:Can't load the error img.")
            data = ""
        return data
# @app.route("/")
# def index():
#     return render_template("img.html")

if __name__ == '__main__':
    # -------------------主程序初始化-------------------
    Initialize(sys.argv[1:])
    thread_auto = MyThread(1,"AutoRemoveExpireCode",1)
    thread_auto.start()
    app.run(webhost,port=webport,debug=webdebug)