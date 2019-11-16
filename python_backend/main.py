# coding=utf-8
from flask import Flask, request, render_template
from img import py_captcha_main as ImgCaptcha
from sms import py_sms_main as SmsCaptcha
from COS import py_cos_main as COS
from psql import py_postgresql as PSQL
from configparser import ConfigParser
import random, MD5
import json, redis
import logging
import sys, getopt
import threading, time
import os
import base64

app = Flask(__name__)
imgcaptcha_list = []  # {"hash":hash,"TTL":180}
smscaptcha_list = []  # {"hash":hash,"TTL":180}

LOG_FORMAT = "[%(asctime)-15s] - [%(name)10s]\t- [%(levelname)s]\t- [%(funcName)-20s:%(lineno)3s]\t- [%(message)s]"
DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
log_outpath = "./my.log"
Main_filepath = os.path.dirname(os.path.abspath(__file__))
print("Main FilePath:", Main_filepath)


def Initialize(argv: list):
    """
模块初始化，此函数应在所有命令之前调用
    :param argv: 命令行参数表
    """
    # print("Enter the function")
    global r, config_addr
    try:
        opts, args = getopt.getopt(argv, "hc:", ["config", "help"])
    except getopt.GetoptError:
        print("test.py -c <ConfigFilePath> -h <help>")
        sys.exit(2)
    for opt, arg in opts:
        # print("opt,arg",opt,arg)
        if opt in ("-h", "--help"):
            print("-" * 80)
            print("-h or --help      Show this passage.")
            print("-c or --config    Configuration file path")
            print("-" * 80)
            sys.exit()
        elif opt in ("-c", "--config"):
            config_addr = str(arg)
            print("config_addr:", config_addr)
            break
        else:
            # log_main.warning("Useless argv:[%s|%s]",opt,arg)
            print("Useless argv:[%s|%s]" % (opt, arg))
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
        if section in ["Log", "Redis", "SmsCaptcha"]:
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
        global log_outpath, webhost, webport, webdebug, allowurl
        log_outpath = cf.get("Main", "logoutpath")
        webhost = cf.get("Main", "webhost")
        webport = cf.get("Main", "webport")
        intdebug = cf.get("Main", "webdebug")
        allowurl = str(cf.get("COS", "allowurl")).split(",")
        print("allowurl:{}".format(allowurl))
        if intdebug == 1:
            webdebug = True
        else:
            webdebug = False
        print("[Main]log_outpath:", log_outpath)
        print("[Main]webhost:", webhost)
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
        r_host = cf.get("Redis", "host")
        r_port = cf.get("Redis", "port")
        r_db = cf.get("Redis", "db")
        r_pass = cf.get("Redis", "pass")
        global r_imgsetname, r_smssetname
        r_imgsetname = cf.get("Redis", "img_setname")  # TODO global setname
        r_smssetname = cf.get("Redis", "sms_setname")
        print("[Redis]Host:", r_host)
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
        r = redis.StrictRedis(host=r_host, port=r_port, db=r_db, password=r_pass)
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
    ImgCaptcha.Initialize(config_addr, Main_filepath)
    SmsCaptcha.Initialize(config_addr, Main_filepath)
    COS.Initialize(config_addr, Main_filepath)
    PSQL.Initialize(config_addr, Main_filepath)


class MyThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        log_main.info("Start thread 【%s】 to auto del outtime code" % self.name)
        print("开始线程：" + self.name)
        auto_del_code()
        log_main.info("End thread 【%s】 to auto del outtime code" % self.name)
        print("退出线程：" + self.name)


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
                    r.srem(r_imgsetname, imgcaptcha["hash"])
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
                    r.srem(r_smssetname, smscaptcha["hash"])
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
    for imgcaptcha in imgcaptcha_list:
        if imgcaptcha["hash"] == hash:
            flag = True
            imgcaptcha["TTL"] = 180
        else:
            pass
    for smscaptcha in smscaptcha_list:
        if smscaptcha["hash"] == hash:
            flag = True
            smscaptcha["TTL"] = 180
        else:
            pass
    if flag == True:
        return 0
    else:
        return -1


@app.route("/captcha", methods=["POST"])
def captcha():
    data = request.json
    print(data)

    # 判断键值对是否存在
    try:
        keys = data.keys()
    except Exception as e:
        # status -1 json的key错误。此处id是因为没有进行读取，所以返回默认的-1。
        return json.dumps({"id": -1, "status": -1, "message": "Error JSON key", "data": {}})
    # 先获取json里id的值，若不存在，默认值为-1
    if "id" in data.keys():
        id = data["id"]
    else:
        id = -1

    # 判断指定所需字段是否存在，若不存在返回status -1 json。
    for key in ["type", "subtype", "data"]:
        if not key in data.keys():
            # status -1 json的key错误。
            return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})

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
            hash = MD5.md5(code, salt=rand_str)
            try:
                r.sadd(r_imgsetname, hash)
                imgcaptcha_list.append({"hash": hash, "TTL": 180})
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
                    "id": id,
                    "status": 0,
                    "message": "successful",
                    "data": {}
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
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    elif data["type"] == "sms":
        if data["subtype"] == "generate":
            data = data["data"]
            for key in data.keys():
                if key not in ["phone", "hash"]:
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            hash = data["hash"]
            result = SafeCheck(hash)
            if result != 0:
                # status -4 json的value错误。
                return json.dumps({"id": id, "status": -4, "message": "Error Hash", "data": {}})
            phone = str(data["phone"])
            code = random.randint(10000, 99999)
            result = SmsCaptcha.SendCaptchaCode(phone, code, ext=str(id))
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
                    r.sadd(r_smssetname, hash)
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


@app.route("/portrait", methods=["POST"])
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
                COS.bytes_upload(img_file, "portrait/{}".format(id2))
                print("Add portrait for id:{}".format(id2))
                log_main.info("Add portrait for id:{}".format(id2))
            except Exception as e:
                print("Failed to add portrait for id:{}".format(id2))
                print(e)
                log_main.error("Failed to add portrait for id:{}".format(id2))
                log_main.error(e)
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
        print("[get_portrait]{}".format(e))
        log_main.error("[get_portrait]{}".format(e))
    try:
        referer = str(request.headers.get("Referer"))
        # print("referer:{}".format(referer))
        # print("referer:{},type:{}".format(referer, type(referer)))
        for url in allowurl:
            # print("Allow Url:{}".format(url))
            # todo 服务器上有bug
            index = referer.find(url)
            if index != -1:
                break
        else:
            log_main.warning("[get_portrait]External Domain Name : {} Reference Pictures Prohibited".format(referer))
            try:
                path = os.path.join(Main_filepath, "data/image/ban.jpg")
                with open(path, "rb") as f:
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("[get_portrait]Error:Can't load the ban img.")
                log_main.error("Error:Can't load the ban img.")
                data = b""
            return data
    except Exception as e:
        print(e)
        print("[get_portrait]Error:Can't get real ip.")
        log_main.error("Error:Can't get real ip.")
        data = b""
        return data
    except Exception as e:
        print(e)

    # print("The client ip is :",ip)
    # srchead = "data:;base64,"
    # import base64
    print("id:", id)
    print("-" * 10)
    id = str(id)
    if id.isdigit():
        # print("Try to get portrait data:{}".format(id))
        try:
            data = COS.bytes_download("portrait/{}".format(id))
        except Exception as e:
            print(e)
            log_main.error(e)
            try:
                path = os.path.join(Main_filepath, "data/image/default.jpg")
                with open(path, "rb") as f:
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
            with open(path, "rb") as f:
                data = f.read()
            # data = COS.bytes_download("portrait/error")
        except Exception as e:
            print("Error:Can't load the error img.")
            log_main.error("Error:Can't load the error img.")
            data = ""
        return data


@app.route("/property", methods=["POST"])
def property():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    property_dict = {
        "id": -1,
        "type": -1,
        "state": -1,
        "lab": "",
        "title": "",
        "content": "",
        "occurrence_time": "",
        "user_id": 0,
        "user_name": "",
        "user_phone": "",
        "user_qq": "",
        "user2_id": "",
        "user2_name": "",
        "user2_phone": "",
        "user2_qq": "",
        "publish_time": "",
        "update_time": "",
        "pic_num": -1,
        "pic_url1": "",
        "pic_url2": "",
        "pic_url3": "",
    }
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    if type == "property":  ## 失物招领api
        if subtype == "add":
            # todo add
            # property_dict 字典模版已放在外部
            # -------定义缺省字段初始值-------
            # uid
            uid = int(time.time())
            print("uid:", uid)
            property_dict["id"] = uid
            # type
            if "type" not in data.keys():
                # status -202 Missing necessary data key-value
                return json.dumps({"id": id, "status": -202, "message": "Missing necessary data key-value", "data": {}})
            else:
                property_type = str(data["type"])
                if property_type.isdigit():
                    int_property_type = int(property_type)
                    if int_property_type not in [1, 2]:
                        # status -204 键值对数据错误
                        return json.dumps(
                            {"id": id, "status": -204, "message": "Arg's value error", "data": {}})
                    property_dict["type"] = int_property_type  # 1表示寻物启事，2表示失物招领
                else:
                    print("type is empty")
                    # status -201 Necessary key-value can't be empty
                    return json.dumps(
                        {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
            # state
            property_dict["state"] = 0
            # user_id
            user_id = PSQL.GetUserID(token)
            print("user_id:", user_id)
            if user_id == None or user_id == 0:
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            else:
                property_dict["user_id"] = user_id
            property_dict["update_time"] = time.localtime()
            # -------开始读取其他信息-------
            for key in data.keys():
                print("{}:{}".format(key, data[key]))
                if key not in property_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
                if key == "type":
                    continue
                if key == "lab":
                    if data["lab"] == "":
                        print("lab is empty")
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    property_dict["lab"] = data["lab"]
                    continue
                elif key == "title":
                    if data["title"] == "":
                        print("title is empty")
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    property_dict["title"] = data["title"]
                    continue
                elif key == "content":
                    if data["content"] == "":
                        print("content is empty")
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    property_dict["content"] = data["content"]
                    continue
                elif key == "occurrence_time":
                    if data["occurrence_time"] == "":
                        data["occurrence_time"] = time.localtime()
                    property_dict["occurrence_time"] = data["occurrence_time"]
                    continue
                elif key == "user_id":
                    if data["user_id"] == None or data["user_id"] == "" or data["user_id"] == 0:
                        print("user_id is empty")
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    property_dict["user_id"] = data["user_id"]
                    continue
                elif key == "user_name":
                    if data["user_name"] == "":
                        print("user_name is empty")
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    property_dict["user_name"] = data["user_name"]
                    continue
                elif key == "user_phone":
                    property_dict["user_phone"] = data["user_phone"]
                    continue
                elif key == "user_qq":
                    property_dict["user_qq"] = data["user_qq"]
                    continue
                elif key == "user2_name":
                    property_dict["user2_name"] = data["user2_name"]
                    continue
                elif key == "user2_phone":
                    property_dict["user2_phone"] = data["user2_phone"]
                    continue
                elif key == "user2_qq":
                    property_dict["user2_qq"] = data["user2_qq"]
                    continue
                elif key == "publish_time":
                    if data["publish_time"] == "":
                        data["publish_time"] = time.localtime()
                    property_dict["publish_time"] = data["publish_time"]
                    continue
                elif key == "update_time":
                    if data["update_time"] == "":
                        data["update_time"] = data["publish_time"]
                    property_dict["update_time"] = data["update_time"]
                    continue
                elif key == "pic_num":
                    num_str = str(data["pic_num"])
                    if num_str.isdigit():
                        num = int(num_str)
                        property_dict[key] = num
                        for i in range(num):
                            filed = "pic_url" + str(i + 1)  # 字段名
                            print(filed)
                            property_dict[filed] = data[filed]
                    else:
                        # status -203 键值对数据类型错误
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                elif key == "pic_url1" or key == "pic_url2" or key == "pic_url3":
                    continue
                else:
                    property_dict[key] = data[key]
                    print("Unkown key and value:[{},{}]".format(key, data[key]))
                    log_main.warning("Unkown key and value:[{},{}]".format(key, data[key]))
                    continue
            try:
                result = PSQL.InsertProperty(**property_dict)
            except:
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})
            if result == True:
                # status 0 添加记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {"uid": uid}})
            else:
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})
        elif subtype == "update":
            # todo update
            # property_dict 字典模版已放在外部
            # -------定义缺省字段初始值-------
            update_dict = {}
            # lost_dict["state"] = 0
            user_id = PSQL.GetUserID(token)
            print("user_id:", user_id)
            if user_id == None or user_id == 0:
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            else:
                # lost_dict["user_id"] = user_id
                update_dict["user_id"] = user_id
            if "id" not in data.keys():
                # status -202 Missing necessary data key-value
                return json.dumps(
                    {"id": id, "status": -202, "message": "Missing necessary data key-value", "data": {}})
            # lost_dict["update_time"] = time.localtime()
            update_dict["update_time"] = time.localtime()
            # -------开始读取其他信息-------
            for key in data.keys():
                if key not in property_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
                if key == "id":
                    uid = str(data["id"])
                    if uid.isdigit():
                        uid = int(uid)
                        # lost_dict["id"] = uid
                        update_dict["id"] = uid
                    else:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    continue
                if key == "type":
                    property_type = str(data["type"])
                    if property_type.isdigit():
                        int_property_type = int(property_type)
                        if int_property_type not in [1, 2]:
                            # status -204 键值对数据错误
                            return json.dumps(
                                {"id": id, "status": -204, "message": "Arg's values error", "data": {}})
                        # lost_dict["type"] = uid
                        update_dict["type"] = int_property_type
                    else:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    continue
                elif key == "state":
                    state = str(data["state"])
                    if state.isdigit():
                        state = int(state)
                        # lost_dict["state"] = state
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
                    # lost_dict["lab"] = data["lab"]
                    update_dict["lab"] = data["lab"]
                    continue
                elif key == "title":
                    if data["title"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # lost_dict["title"] = data["title"]
                    update_dict["title"] = data["title"]
                    continue
                elif key == "content":
                    if data["content"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # lost_dict["content"] = data["content"]
                    update_dict["content"] = data["content"]
                    continue
                elif key == "occurrence_time":
                    if data["occurrence_time"] == "":
                        data["occurrence_time"] = time.localtime()
                    # lost_dict["occurrence_time"] = data["occurrence_time"]
                    update_dict["occurrence_time"] = data["occurrence_time"]
                    continue
                elif key == "user_id":
                    if data["user_id"] == None or data["user_id"] == "" or data["user_id"] == 0:
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # lost_dict["user_id"] = data["user_id"]
                    update_dict["user_id"] = data["user_id"]
                    continue
                elif key == "user_name":
                    if data["user_name"] == "":
                        # status -201 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    # lost_dict["user_name"] = data["user_name"]
                    update_dict["user_name"] = data["user_name"]
                    continue
                elif key == "user_phone":
                    # lost_dict["user_phone"] = data["user_phone"]
                    update_dict["user_phone"] = data["user_phone"]
                    continue
                elif key == "user_qq":
                    # lost_dict["user_qq"] = data["user_qq"]
                    update_dict["user_qq"] = data["user_qq"]
                    continue
                elif key == "user2_name":
                    # lost_dict["user2_name"] = data["user2_name"]
                    update_dict["user2_name"] = data["user2_name"]
                    continue
                elif key == "user2_phone":
                    # lost_dict["user2_phone"] = data["user2_phone"]
                    update_dict["user2_phone"] = data["user2_phone"]
                    continue
                elif key == "user2_qq":
                    # lost_dict["user2_qq"] = data["user2_qq"]
                    update_dict["user2_qq"] = data["user2_qq"]
                    continue

                elif key == "update_time":
                    if data["update_time"] == "":
                        data["update_time"] = data["publish_time"]
                    # lost_dict["update_time"] = data["update_time"]
                    update_dict["update_time"] = data["update_time"]
                    continue
                else:
                    update_dict[key] = data[key]
                    print("Unkown key and value:[{},{}]".format(key, data[key]))
                    log_main.warning("Unkown key and value:[{},{}]".format(key, data[key]))
            try:
                result = PSQL.UpdateProperty(**update_dict)
            except Exception as e:
                print("Unknown Error:", e)
                log_main.error(e)
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})

            if result == True:
                # status 0 更新记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {}})
            else:
                print("操作失败")
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})
            # todo 设计数据更新api
        elif subtype == "delete":
            # lost_dict字典模版已放在外部

            # -------定义缺省字段初始值-------
            user_id = PSQL.GetUserID(token=token)
            if user_id == 0 or user_id == None:
                # status -102 Get userid failed for the token
                return json.dumps({"id": id, "status": -102, "message": "Get userid failed for the token", "data": {}})
            print("user_id:", user_id)
            delete_dict = {}
            # 获取字段信息
            if "user_id" in data.keys():
                delete_dict["user_id"] = data["user_id"]
            else:
                delete_dict["user_id"] = user_id
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
                print("Unknown Error:", e)
                log_main.error(e)
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})
            if result == True:
                # status 0 删除记录成功
                return json.dumps({"id": id, "status": 0, "message": "successful", "data": {}})
            else:
                print("操作失败")
                # status -200 数据库操作失败。
                return json.dumps({"id": id, "status": -200, "message": "Failure to operate database", "data": {}})
            # todo 设计数据删除api
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/pic", methods=["POST"])
def pic():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    data = data["data"]
    if type == "pic":
        if subtype == "upload":
            for key in ["from", "base64"]:
                if key not in data.keys():
                    # status -3 json的value错误。
                    return json.dumps({"id": id, "status": -3, "message": "Error data key", "data": {}})
            j_from = data["from"]
            if j_from not in ["property", "shop", "product", "portrait"]:
                # status -204 Arg's value error 键值对数据错误。
                return json.dumps({"id": id, "status": -204, "message": "Arg's value error", "data": {}})
            img_base64 = str(data["base64"])
            base64_head_index = img_base64.find(";base64,")
            if base64_head_index != -1:
                print("进行了替换")
                img_base64 = img_base64.partition(";base64,")[2]
            # print("-------接收到数据-------\n", img_base64, "\n-------数据结构尾-------")
            img_file = base64.b64decode(img_base64)
            if "name" in data.keys():
                pic_name = data["name"]
                if pic_name == "":
                    # status -204 Arg's value error 键值对数据错误。
                    return json.dumps({"id": id, "status": -204, "message": "Arg's value error", "data": {}})
            else:
                pic_name = MD5.md5_bytes(img_file)
            try:
                COS.bytes_upload(img_file, "{}/{}".format(j_from, pic_name))
                print("Add pic for {}:{}".format(j_from, pic_name))
                log_main.info("Add pic for {}:{}".format(j_from, pic_name))
            except Exception as e:
                print("Failed to add pic for {}:{}".format(j_from, pic_name))
                print(e)
                log_main.error("Failed to add pic for {}:{}".format(j_from, pic_name))
                log_main.error(e)
                # status -500 COS upload Error
                return {"id": id, "status": -500, "message": "COS upload Error", "data": {}}
            # status 0 successful
            return json.dumps({"id": id, "status": 0, "message": "Successful", "data": {
                "url": "./api/external/get/pic/{}/{}".format(j_from, pic_name)}})

        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/get/pic/<j_from>/<pic_name>")
def get_pic(j_from: str, pic_name: str):
    try:
        realip = request.headers.get("X-Real-Ip")
        # print("real ip:{},type:{}".format(realip,type(realip)))
    except Exception as e:
        print("[get_pic]{}".format(e))
        log_main.error("[get_pic]{}".format(e))
    try:
        referer = str(request.headers.get("Referer"))
        # print("referer:{}".format(referer))
        # print("referer:{},type:{}".format(referer, type(referer)))
        for url in allowurl:
            # print("Allow Url:{}".format(url))
            # todo 服务器上有bug
            index = referer.find(url)
            if index != -1:
                break
        else:
            log_main.warning("[get_pic]External Domain Name : {} Reference Pictures Prohibited".format(referer))
            try:
                path = os.path.join(Main_filepath, "data/image/ban.jpg")
                with open(path, "rb") as f:
                    data = f.read()
                # data = COS.bytes_download("portrait/error")
            except Exception as e:
                print("[get_pic]Error:Can't load the ban img.")
                log_main.error("Error:Can't load the ban img.")
                data = b""
            return data
    except Exception as e:
        print(e)
        print("[get_pic]Error:Can't get real ip.")
        log_main.error("Error:Can't get real ip.")
        data = b""
        return data
    # print("The client ip is :",ip)
    # srchead = "data:;base64,"
    # import base64
    # print("[get_porttrait]user_id:", user_id)
    j_from = str(j_from)
    pic_name = str(pic_name)
    if j_from not in ["property", "shop", "product", "portrait"]:
        try:
            path = os.path.join(Main_filepath, "data/image/error.jpg")
            with open(path, "rb") as f:
                data = f.read()
            # data = COS.bytes_download("portrait/error")
        except Exception as e:
            print("[get_porttrait]Error:Can't load the error img.")
            log_main.error("Error:Can't load the error img.")
            data = b""
            return data
    try:
        data = COS.bytes_download("{}/{}".format(j_from, pic_name))
    except Exception as e:
        msg = str(e)
        code = msg.partition("<Code>")[2].partition("</Code>")[0]
        message = msg.partition("<Message>")[2].partition("</Message>")[0]
        # todo 以后要做一个判断机制
        print("[get_portrait]{}:{}".format(code, message))
        try:
            path = os.path.join(Main_filepath, "data/image/error.jpg")
            with open(path, "rb") as f:
                data = f.read()
            # data = COS.bytes_download("portrait/error")
        except Exception as e:
            print("[get_porttrait]Error:Can't load the error img.")
            log_main.error("Error:Can't load the error img.")
            data = b""
    return data


@app.route("/get/property", methods=["GET"])
def get_property():
    try:
        token = request.args["token"]
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necesxsary agrs")
        # status -104 缺少必要的参数
        return json.dumps({"id": -1, "status": -104, "message": "Missing necessary args", "data": {}})
    token_check_result = PSQL.CheckToken(token)
    if token_check_result == False:
        # status -105 token不正确
        return json.dumps({"id": -1, "status": -105, "message": "Error token", "data": {}})
    # 验证身份完成，处理数据
    property_dict = {
        "id": -1,
        "type": -1,
        "state": -1,
        "lab": "",
        "title": "",
        "content": "",
        "occurrence_time": "",
        "user_id": -1,
        "user_name": "",
        "user_phone": "",
        "user_qq": "",
        "user2_id": "",
        "user2_name": "",
        "user2_phone": "",
        "user2_qq": "",
        "publish_time": "",
        "update_time": "",
        "pic_num": 0,
        "pic_url1": "",
        "pic_url2": "",
        "pic_url3": "",
    }
    args_dict = dict(request.args)
    # print("value:",args_dict.keys(),"type:",type(args_dict))
    num = len(args_dict.keys())
    print("have {} args".format(num))
    if num == 1:
        # status -104 缺少必要的参数
        return json.dumps({"id": -1, "status": -104, "message": "Missing necessary args", "data": {}})
    if num == 2:
        if "type" in args_dict.keys():
            property_type = str(args_dict["type"])
            if property_type.isdigit():
                int_property_type = int(property_type)
                if int_property_type not in [1, 2]:
                    # status -106 参数值错误
                    return json.dumps({"id": -1, "status": -106, "message": "Args Error", "data": {}})
                args_dict["type"] = int_property_type
            else:
                # status -101 参数值类型错误
                return json.dumps({"id": -1, "status": -101, "message": "Args Type Error", "data": {}})
        else:
            # status -104 缺少必要的参数
            return json.dumps({"id": -1, "status": -104, "message": "Missing necessary args", "data": {}})
        record_num, data_list = PSQL.GetProperty(args_dict["type"], "")
        print("GET proerty all,totally: {} record".format(record_num))
        # status 0 成功处理数据
        try:
            return json.dumps({"id": -1, "status": 0, "message": "successful", "data": data_list}, ensure_ascii=False)
        except Exception as e:
            print(e)
    else:
        # 情况一，只有token、type和key参数
        if "type" in args_dict.keys():
            property_type = str(args_dict["type"])
            if property_type.isdigit():
                args_dict["type"] = int(property_type)
            else:
                # status -101 参数值类型错误
                return json.dumps({"id": -1, "status": -101, "message": "Args Type Error", "data": {}})
        else:
            # status -104 缺少必要的参数
            return json.dumps({"id": -1, "status": -104, "message": "Missing necessary args", "data": {}})

        if num == 3 and "key" in args_dict.keys():
            record_num, data_list = PSQL.GetProperty(args_dict["type"], args_dict["key"])
            print("GET find proerty,totally: {} record".format(record_num))
            # status 0 成功处理数据
            return json.dumps({"id": -1, "status": 0, "message": "successful", "data": data_list}, ensure_ascii=False)
        # 情况二，key与其他非token及type参数并存
        if num > 3 and "key" in args_dict.keys():
            # status -103 Args conflict
            return json.dumps({"id": -1, "status": -103, "message": "Args conflict", "data": {}})
        # 情况三，无key参数
        sql_dict = {}
        for key in args_dict.keys():
            if key == "token":
                continue
            if key == "type":
                continue
            if key not in property_dict.keys():
                # status -100 Args Error
                return json.dumps({"id": -1, "status": -100, "message": "Args Error", "data": {}})
            sql_dict[key] = str(args_dict[key])
            if key == "id" or key == "state":
                if sql_dict[key].isdigit():
                    sql_dict[key] = int(sql_dict[key])
                else:
                    # status -101 Args Type Error
                    return json.dumps({"id": -1, "status": -101, "message": "Args Type Error", "data": {}})
        record_num, data_list = PSQL.GetProperty(args_dict["type"], "", **sql_dict)
        print("GET find proerty,totally: {} record".format(record_num))
        # status 0 成功处理数据
        return json.dumps({"id": -1, "status": 0, "message": "successful", "data": data_list}, ensure_ascii=False)


@app.route("/shop", methods=["POST"])
def shop():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    if type == "shop":  ## 店铺api
        if subtype == "creat":
            if "shop_name" not in data.keys():
                # status -1 json的key错误。
                return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
            shop_name = data["shop_name"]
            user_id = PSQL.GetUserID(token=token)
            if user_id == None or user_id == 0:
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get user_id failed for the token", "data": {}})
            json_dict = PSQL.CreatShop(shop_name=shop_name, user_id=user_id, id=id)
            return json.dumps(json_dict)
        elif subtype == "update":
            for key in data.keys():
                if key not in ["shop_content", "shop_id"]:
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
            shop_id = data["shop_id"]
            shop_content = data["shop_content"]
            user_id = PSQL.GetUserID(token)
            if user_id == None or user_id == 0:
                # status -102 Necessary args can't be empty
                return json.dumps(
                    {"id": id, "status": -102, "message": "Get user_id failed for the token", "data": {}})
            json_dict = PSQL.UpdateShop(shop_id=shop_id, shop_content=shop_content, user_id=user_id, id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/get/shop", methods=["POST"])
def get_shop():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    if type == "shop":  ## 店铺api
        if subtype == "list":
            if "shop_name" not in data.keys():
                # status -1 json的key错误。
                return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
            shop_name = data["shop_name"]
            order = ""
            if "order" in data.keys():
                order = data["order"]
            json_dict = PSQL.GetShopList(shop_name=shop_name, order=order, id=id)
            # status 0 1
            return json.dumps(json_dict)
        elif subtype == "info":
            if "shop_id" in data.keys():
                shop_id = data["shop_id"]
                json_dict = PSQL.GetShopInfo(shop_id=shop_id, id=id)
            elif "shop_name" in data.keys():
                shop_name = data["shop_name"]
                json_dict = PSQL.GetShopInfo(shop_name=shop_name, id=id)
            return json.dumps(json_dict)
        elif subtype == "delete":
            pass
            # todo Delete shop
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/product", methods=["POST"])
def product():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    user_id = PSQL.GetUserID(token)
    key_dict = {
        "product_id": -1,
        "product_name": "",
        "product_content": "",
        "product_key": "",
        "product_price": -1.0,
        "product_disprice": -1.0,
        "product_sale": -1,
        "product_click": -1,
        "product_collection": -1,
        "shop_id": -1,
        "creat_time": "",
        "update_time": "",
        "product_pic": "",
        "product_status": -1,
    }
    product_dict = {}
    if type == "product":  ## 店铺api
        if subtype == "creat":
            # TODO 判断非空字段是否存在
            for key in data.keys():
                if key not in key_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
            for key in data.keys():
                # print("key:[{}],type:[{}]".format(key,type(data[key])))
                if key == "product_id":
                    continue
                elif key == "product_name":
                    if not isinstance(data[key], str):
                        # if type(data[key]) is not str:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == "":
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_content":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -201, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_key":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -201, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_price":
                    if (not isinstance(data[key], float)) and (not isinstance(data[key], int)):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    data[key] = float(data[key])
                    if data[key] == 0.0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_disprice":
                    continue
                elif key == "product_sale":
                    continue
                elif key == "product_click":
                    continue
                elif key == "product_collection":
                    continue
                elif key == "shop_id":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == 0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "creat_time":
                    continue
                elif key == "update_time":
                    continue
                elif key == "product_pic":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == "":
                        pass
                        # todo 设置一张默认图片
                    product_dict[key] = data[key]
                    continue
                elif key == "product_status":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] not in [0, 1, 2]:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
            json_dict = PSQL.CreatProduct(user_id=user_id, id=id, **product_dict)
            return json.dumps(json_dict)
        elif subtype == "update":
            for key in data.keys():
                if key not in key_dict.keys():
                    # status -1 json的key错误。
                    return json.dumps({"id": id, "status": -1, "message": "Error JSON key", "data": {}})
            for key in data.keys():
                if key == "product_id":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == 0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                elif key == "product_name":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == "":
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_content":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -201, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_key":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -201, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_price":
                    if (not isinstance(data[key], float)) and (not isinstance(data[key], int)):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    data[key] = float(data[key])
                    if data[key] == 0.0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_disprice":
                    if (not isinstance(data[key], float)) and (not isinstance(data[key], int)):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    data[key] = float(data[key])
                    if data[key] == 0.0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_sale":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_click":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "product_collection":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "shop_id":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == 0:
                        # status -204 Necessary args can't be empty
                        return json.dumps(
                            {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}})
                    product_dict[key] = data[key]
                    continue
                elif key == "creat_time":
                    continue
                elif key == "update_time":
                    # todo 在psql里配置
                    continue
                elif key == "product_pic":
                    if not isinstance(data[key], str):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] == "":
                        pass
                        # todo 设置一张默认图片
                    product_dict[key] = data[key]
                    continue
                elif key == "product_status":
                    if not isinstance(data[key], int):
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    if data[key] not in [0, 1, 2]:
                        # status -203 Arg's value type error
                        return json.dumps({"id": id, "status": -203, "message": "Arg's value type error", "data": {}})
                    product_dict[key] = data[key]
            json_dict = PSQL.UpdateProduct(user_id=user_id, id=id, **product_dict)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/get/product", methods=["POST"])
def get_product():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    if type == "product":
        if subtype == "list":
            product_name = ""
            if "product_name" in data.keys():
                product_name = data["product_name"]
            product_key = ""
            if "product_key" in data.keys():
                product_key = data["product_key"]
            type = "up"
            if "type" in data.keys():
                type = data["type"]
            shop_id = 0
            if "shop_id" in data.keys():
                shop_id = data["shop_id"]
            order = ""
            if "order" in data.keys():
                order = data["order"]
            json_dict = PSQL.GetProductList(product_name=product_name, product_key=product_key, shop_id=shop_id,
                                            order=order, type=type, id=id)
            return json.dumps(json_dict)
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


@app.route("/purchase", methods=["POST"])  # 订单api
def purchase():
    try:
        token = request.args["token"]
        print("token:", token)
    except Exception as e:
        print("Missing necessary args")
        log_main.error("Missing necessary agrs")
        # status -100 缺少必要的参数
        return json.dumps({"id": -1, "status": -100, "message": "Missing necessary args", "data": {}})
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
    type = data["type"]
    subtype = data["subtype"]
    ## -------正式处理事务-------
    data = data["data"]
    user_id = PSQL.GetUserID(token)
    if type == "purchase":
        if subtype == "apply":  # 申请订单
            pass
        elif subtype == "pay":  # 支付中
            pass
        elif subtype == "cancel":  # 取消订单
            pass
        elif subtype == "finish":  # 完成订单
            pass
        elif subtype == "get":  # 获取订单
            pass
        else:
            # status -2 json的value错误。
            return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})
    else:
        # status -2 json的value错误。
        return json.dumps({"id": id, "status": -2, "message": "Error JSON value", "data": {}})


# @app.route("/")
# def index():
#     return render_template("img.html")

if __name__ == '__main__':
    # -------------------主程序初始化-------------------
    Initialize(sys.argv[1:])
    thread_auto = MyThread(1, "AutoRemoveExpireCode", 1)
    thread_auto.start()
    app.run(webhost, port=webport, debug=webdebug)
