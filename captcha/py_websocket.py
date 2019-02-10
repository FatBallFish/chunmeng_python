from sms import py_sms_main as SmsCaptcha
from img import py_captcha_main as ImgCaptcha
from configparser import ConfigParser
import asyncio,websockets,json
import logging
import random
import sys,getopt

def Initialize(argv):
    # print("Enter the function")
    global ImgCaptchaAddr,ApiConfigAddr
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
            print("-i or --imgaddr   Necessary argv to fix img captcha files address ")
            print("-"*80)
            sys.exit()
        elif opt in ("-i","--imgaddr"):
            ImgCaptchaAddr = str(arg)
            # log_main.info("Located ImgCaptcha address:[%s]",ImgCaptchaAddr)
        else:
            log_main.error("Error argv:[%s|%s]",opt,arg)
            print("Error argv")
            sys.exit()
    cf = ConfigParser()
    cf.read("./config.ini")
    sections = cf.sections()
    for section in sections:
        if section == "Main":
            break
    else:
        cf.add_section("Main")
    cf.set("Main","ImgCaptchaAddr",ImgCaptchaAddr   )
    cf.write(open("./config.ini","w"))
    # ------模块初始化------
    ImgCaptcha.Initialize()
    SmsCaptcha.Initialize()

def event_img_generate(subid):
    log_main.info("Get Imgcaptcha")
    code, addr = ImgCaptcha.CreatCode()
    CAPTCHA["title"] = code
    CAPTCHA["addr"] = addr
    code_list.append(CAPTCHA)
    return json.dumps({"id": subid,"status":0,"message":"Successful","data":{**CAPTCHA}})


def event_captcha(data):
    # data["code"]
    pass


def event_users():
    log_main.info("Get users information")
    return json.dumps({"id": "sys", "status": 0, "message": "Successful", "data": {"count":len(USERS)}})

def event_sms_generate(subid,phone):
    log_main.info("Get Smscaptcha")
    captcha = str(random.randint(1000,9999))
    result = SmsCaptcha.SendCaptchaCode(phone,captcha)
    back = {"id":subid,"status":result["result"],"message":result["errmsg"],"data":{}}
    return json.dumps(back)


async def flush_custom():
    if USERS:
        message = event_users()
        await asyncio.wait([user.send(message) for user in USERS])


async def registor(webscoket):
    USERS.add(webscoket)
    await flush_custom()


async def unregistor(webscoket):
    USERS.remove(webscoket)
    await flush_custom()


async def main(websocket, path):
    websocket_str = str(websocket)
    websocket_id = websocket_str.partition("at ")[2].partition(">")[0]
    log_main.info("Customer [%s] Connected",websocket_id)
    await registor(websocket)
    try:
        await websocket.send(event_img_generate("imgcaptcha"))
        async for message in websocket:
            print(message)
            info = json.loads(message)
            subid = info["id"]
            data = info["data"]
            if info["type"] == "captcha":
                if info["subtype"] == "img":
                    if data["action"] == "generate":
                        await websocket.send(event_img_generate(subid))
                elif info["subtype"] == "sms":
                    if data["action"] == "generate":
                        await websocket.send(event_sms_generate(subid,data["phone"]))
                # elif info["subtype"] == "captcha":
                #     if data["action"] == "generate"
                #         await websocket.send(event_captcha(data))
            else:
                logging.error(
                    "unsupported event: %s", info)
    except Exception as err:
        log_main.error(err)
    finally:
        await unregistor(websocket)
        log_main.info("Customer [%s] Disconnected",websocket_id)

if __name__ == '__main__':
    # -------------------主程序初始化-------------------
    ImgCaptchaAddr = ""
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
    logging.basicConfig(filename="my.log", level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        datefmt=DATA_FORMAT)
    log_main = logging.getLogger(__name__)

    CAPTCHA = {"id": "", "addr": "", "code": ""}
    code_list = []
    USERS = set()
    log_main.info("Websockets Started")
    # --------------------------------------------------
    Initialize(sys.argv[1:])

    asyncio.get_event_loop().run_until_complete(websockets.serve(main, "0.0.0.0", 10086))
    asyncio.get_event_loop().run_forever()
