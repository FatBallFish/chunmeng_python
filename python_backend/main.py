from flask import Flask,request,render_template
from img import py_captcha_main as ImgCaptcha
from sms import py_sms_main as SmsCaptcha
from COS import py_cos_main as COS
from psql import py_postgresql as PSQL
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
        print("[Main]log_outpath:",log_outpath)
        print("[Main]webhost:",webhost)
        print("[Main]webport:", webport)
        print("[Main]webdebug:", webdebug)
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
        print("[Redis]Host:",r_host)
        print("[Redis]Port:", r_port)
        print("[Redis]DB:", r_db)
        print("[Redis]Imgsetname:", r_imgsetname)
        print("[Redis]Smssetname:", r_smssetname)
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
    PSQL.Initialize(config_addr,Main_filepath)


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
                # todo 优化验证机制
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
                    r.sadd(r_smssetname,hash)
                    smscaptcha_list.append({"hash": hash, "TTL": 180})
                    # todo 优化验证机制
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
                print("Add portrait for id:{}".format(id2))
                log_main.info("Add portrait for id:{}".format(id2))
            except Exception as e:
                print("Failed to add portrait for id:{}".format(id2))
                print(e)
                log_main.error("Failed to add portrait for id:{}".format(id2))
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
    """
获取头像API。GET请求。
    :param id: 用户id
    :return: 见开发文档
    """
    print("-" * 10)
    try:
        realip = request.headers.get("X-Real-Ip")
        # print("real ip:{},type:{}".format(realip,type(realip)))
    except Exception as e:
        print(e)
    try:
        referer = str(request.headers.get("Referer"))
        # print("referer:{},type:{}".format(referer, type(referer)))
        index1 = referer.find("https://www.zustservice.cn/")
        index2 = referer.find("http://localhost/")
        if index1 == -1 and index2 == -1:
            print("External Domain Name : {} Reference Pictures Prohibited".format(referer))
            try:
                path = os.path.join(Main_filepath, "data/image/ban.jpg")
                with open(path, "rb") as f:
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("Error:Can't load the ban img.")
                log_main.error("Error:Can't load the ban img.")
                data = ""
        return data

    except Exception as e:
        print(e)

    # print("The client ip is :",ip)
    # srchead = "data:;base64,"
    # import base64
    print("id:", id)
    print("-"*10)
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
@app.route("/property/find",methods=["POST"])
def findproperty():
    try:
        token = request.args["token"]
        print("token:",token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id":-1,"status":-100,"message":"Missing necessary args","data":{}})
    token_check_result = PSQL.CheckToken(token)
    if token_check_result == False:
        # status -101 token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
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

    ## 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
    find_dict = {
        "id": -1,
        "state": -1,
        "lab": "",
        "title": "",
        "content": "",
        "lost_time": "",
        "loser_name": "",
        "loser_phone": "",
        "loser_qq": "",
        "finder_id": "",
        "finder_name": "",
        "finder_phone": "",
        "finder_qq": "",
        "user_id": "",
        "publish_time": "",
        "update_time": "",
    }
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    if type == "property":
        if subtype == "add":
            # todo add
            data = data["data"]
            # find_dict字典模版已放在外部

            # -------定义缺省字段初始值-------
            find_dict["state"] = 0
            uid = int(time.time())
            print("uid:", uid)
            find_dict["id"] = uid
            user_id = PSQL.GetUserID(token)
            print("user_id:",user_id)
            if user_id == None or user_id == "":
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            else:
                find_dict["user_id"] = user_id
            find_dict["update_time"] = time.localtime()
            # -------开始读取其他信息-------
            for key in data.keys():
                if key not in find_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})

                if key == "lab":
                    if data["lab"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps({"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    find_dict["lab"] = data["lab"]
                elif key == "title":
                    if data["title"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps({"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    find_dict["title"] = data["title"]
                elif key == "content":
                    if data["content"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps({"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    find_dict["content"] = data["content"]
                elif key == "lost_time":
                    if data["lost_time"] == "":
                        data["lost_time"] = time.localtime()
                    find_dict["lost_time"] = data["lost_time"]
                elif key == "loser_name":
                    if data["loser_name"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps({"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    find_dict["loser_name"] = data["loser_name"]
                elif key == "loser_phone":
                    find_dict["loser_phone"] = data["loser_phone"]
                elif key == "loser_qq":
                    find_dict["loser_qq"] = data["loser_qq"]
                elif key == "finder_name":
                    find_dict["finder_name"] = data["finder_name"]
                elif key == "finder_phone":
                    find_dict["finder_phone"] = data["finder_phone"]
                elif key == "finder_qq":
                    find_dict["finder_qq"] = data["finder_qq"]
                elif key == "user_id":
                    if data["user_id"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps({"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    find_dict["user_id"] = data["user_id"]
                elif key == "publish_time":
                    if data["publish_time"] == "":
                        data["publish_time"] = time.localtime()
                    find_dict["publish_time"] = data["publish_time"]
                elif key == "update_time":
                    if data["update_time"] == "":
                        data["update_time"] = data["publish_time"]
                    find_dict["update_time"] = data["update_time"]
                else:
                    find_dict[key] = data[key]
                    print("Unkown key and value:[{},{}]".format(key,data[key]))
                    log_main.warning("Unkown key and value:[{},{}]".format(key,data[key]))

            try:
                result = PSQL.InsertFindProperty(**find_dict)
            except:
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
            if result == True :
                # status 0 添加记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {"uid":uid}})
            else:
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
        elif subtype == "update":
            # todo update
            data = data["data"]
            # find_dict字典模版已放在外部

            # -------定义缺省字段初始值-------
            update_dict = {}
            # find_dict["state"] = 0
            user_id = PSQL.GetUserID(token)
            print("user_id:", user_id)
            if user_id == None or user_id == "":
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            else:
                # find_dict["user_id"] = user_id
                update_dict["user_id"] = user_id
            if "id" not in data.keys():
                # status -202 Missing necessary data key-value
                return json.dumps(
                    {"id": id, "status": -202, "message": "Missing necessary data key-value", "data": {}})
            # find_dict["update_time"] = time.localtime()
            update_dict["update_time"] = time.localtime()
            # -------开始读取其他信息-------
            for key in data.keys():
                if key not in find_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
                if key == "id":
                    uid = str(data["id"])
                    if uid.isdigit():
                        uid = int(uid)
                        # find_dict["id"] = uid
                        update_dict["id"] = uid
                    else:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    continue
                elif key == "state":
                    state = str(data["state"])
                    if state.isdigit():
                        state = int(state)
                        # find_dict["state"] = state
                        update_dict["state"] = state
                    else:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    continue
                elif key == "lab":
                    if data["lab"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # find_dict["lab"] = data["lab"]
                    update_dict["lab"] = data["lab"]
                    continue
                elif key == "title":
                    if data["title"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # find_dict["title"] = data["title"]
                    update_dict["title"] = data["title"]
                    continue
                elif key == "content":
                    if data["content"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # find_dict["content"] = data["content"]
                    update_dict["content"] = data["content"]
                    continue
                elif key == "lost_time":
                    if data["lost_time"] == "":
                        data["lost_time"] = time.localtime()
                    # find_dict["lost_time"] = data["lost_time"]
                    update_dict["lost_time"] = data["lost_time"]
                    continue
                elif key == "loser_name":
                    if data["loser_name"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # find_dict["loser_name"] = data["loser_name"]
                    update_dict["loser_name"] = data["loser_name"]
                    continue
                elif key == "loser_phone":
                    # find_dict["loser_phone"] = data["loser_phone"]
                    update_dict["loser_phone"] = data["loser_phone"]
                    continue
                elif key == "loser_qq":
                    # find_dict["loser_qq"] = data["loser_qq"]
                    update_dict["loser_qq"] = data["loser_qq"]
                    continue
                elif key == "finder_name":
                    # find_dict["finder_name"] = data["finder_name"]
                    update_dict["finder_name"] = data["finder_name"]
                    continue
                elif key == "finder_phone":
                    # find_dict["finder_phone"] = data["finder_phone"]
                    update_dict["finder_phone"] = data["finder_phone"]
                    continue
                elif key == "finder_qq":
                    # find_dict["finder_qq"] = data["finder_qq"]
                    update_dict["finder_qq"] = data["finder_qq"]
                    continue
                elif key == "user_id":
                    if data["user_id"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # find_dict["user_id"] = data["user_id"]
                    update_dict["user_id"] = data["user_id"]
                    continue
                elif key == "update_time":
                    if data["update_time"] == "":
                        data["update_time"] = data["publish_time"]
                    # find_dict["update_time"] = data["update_time"]
                    update_dict["update_time"] = data["update_time"]
                    continue
                else:
                    find_dict[key] = data[key]
                    print("Unkown key and value:[{},{}]".format(key, data[key]))
                    log_main.warning("Unkown key and value:[{},{}]".format(key, data[key]))
            try:
                result = PSQL.UpdateFindProperty(**update_dict)
            except Exception as e:
                print("Unknown Error:",e)
                log_main.error(e)
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
            if result == True:
                # status 0 更新记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {}})
            else:
                print("操作失败")
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
            # todo 设计数据更新api
        elif subtype == "delete":
            data = data["data"]
            # find_dict字典模版已放在外部

            # -------定义缺省字段初始值-------
            user_id = PSQL.GetUserID(token=token)
            if user_id == "" or user_id == None:
                # status -102 Get userid failed for the token
                return json.dumps({"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            print("user_id:", user_id)
            delete_dict = {}
            # 获取字段信息
            if "user_id" in data.keys():
                delete_dict["user_id"] = str(data["user_id"])
            else:
                delete_dict["user_id"] = str(user_id)
            if "id" in data.keys():
                uid = str(data["id"])
                if uid.isdigit():
                    delete_dict["id"] = int(uid)
                else:
                    # status -203 Arg's value type error
                    return json.dumps(
                        {"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
            else:
                # status -201 Necessary key-value can't be empty
                return json.dumps(
                    {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
            try:
                result = PSQL.DeleteProperty(**delete_dict)
            except Exception as e:
                print("Unknown Error:",e)
                log_main.error(e)
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
            if result == True:
                # status 0 删除记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {}})
            else:
                print("操作失败")
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Connect Database Failed", "data": {}})
            # todo 设计数据删除api
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})

@app.route("/get/property/find",methods=["GET"])
def get_findproperty():
    try:
        token = request.args["token"]
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necesxsary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
    token_check_result = PSQL.CheckToken(token)
    if token_check_result == False:
        # status -101 token不正确
        return json.dumps({"id": -1, "status": -101, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    find_dict = {
        "id": -1,
        "state": -1,
        "lab": "",
        "title": "",
        "content": "",
        "lost_time": "",
        "loser_name": "",
        "loser_phone": "",
        "loser_qq": "",
        "finder_id": "",
        "finder_name": "",
        "finder_phone": "",
        "finder_qq": "",
        "user_id": "",
        "publish_time": "",
        "update_time": "",
    }
    args_dict = dict(request.args)
    # print("value:",args_dict.keys(),"type:",type(args_dict))
    num = len(args_dict.keys())
    print("have {} args".format(num))
    if num == 1 :
        record_num, data_list = PSQL.GetFindProperty("")
        print("GET find proerty all,totally: {} record".format(record_num))
        # status 0 成功处理数据
        return json.dumps({"id":-1,"status":0,"message":"successful","data":data_list},ensure_ascii=False)
    else:
        # 情况一
        if num == 2 and "key" in args_dict.keys():
            record_num, data_list = PSQL.GetFindProperty(args_dict["key"])
            print("GET find proerty,totally: {} record".format(record_num))
            # status 0 成功处理数据
            return json.dumps({"id": -1, "status": 0, "message": "successful", "data": data_list}, ensure_ascii=False)
        # 情况二
        if num > 2 and "key" in args_dict.keys():
            # status -103 Args conflict
            return json.dumps({"id": -1, "status": -103, "message": "Args conflict", "data": {}})
        # 情况三
        sql_dict = {}
        for key in args_dict.keys():
            if key == "token":
                continue
            if key not in find_dict.keys():
                # status -100 Args Error
                return json.dumps({"id":-1,"status":-100,"message":"Args Error","data":{}})
            sql_dict[key] = str(args_dict[key])
            if key == "id" or key == "state":
                if sql_dict[key].isdigit():
                    sql_dict[key] = int(sql_dict[key])
                else:
                    # status -101 Args Type Error
                    return json.dumps({"id": -1, "status": -101, "message": "Args Type Error", "data": {}})
        record_num, data_list = PSQL.GetFindProperty("",**sql_dict)
        print("GET find proerty,totally: {} record".format(record_num))
        # status 0 成功处理数据
        return json.dumps({"id": -1, "status": 0, "message": "successful", "data": data_list},ensure_ascii=False)



# @app.route("/")
# def index():
#     return render_template("img.html")

if __name__ == '__main__':
    # -------------------主程序初始化-------------------
    Initialize(sys.argv[1:])
    thread_auto = MyThread(1,"AutoRemoveExpireCode",1)
    thread_auto.start()
    app.run(webhost,port=webport,debug=webdebug)