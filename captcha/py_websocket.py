from sms import py_sms_main as SmsCaptcha
from img import py_captcha_main as ImgCaptcha
import asyncio
import websockets
import json
import logging
import random

ID = 0
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

def event_getcode():
    log_main.info("Get Imgcaptcha")
    code, addr = ImgCaptcha.CreatCode()
    CAPTCHA["id"] = str(ID)
    CAPTCHA["code"] = code
    CAPTCHA["addr"] = addr
    code_list.append(CAPTCHA)
    return json.dumps({"type": "getcode", **CAPTCHA})


def event_captcha(data):
    # data["code"]
    pass


def event_users():
    log_main.info("Get users information")
    return json.dumps({"type": "users", "count": len(USERS)})

def event_sms(phone):
    log_main.info("Get Smscaptcha")
    captcha = str(random.randint(1000,9999))
    result = SmsCaptcha.SendCaptchaCode(phone,captcha)
    result["type"] = "sms_back"
    return json.dumps(result)


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
        await websocket.send(event_getcode())
        async for message in websocket:
            print(message)
            data = json.loads(message)
            if data["action"] == "getcode":
                await websocket.send(event_getcode())
            elif data["action"] == "captcha":
                await websocket.send(event_captcha(data))
            elif data["action"] == "sms":
                await websocket.send(event_sms(data["phone"]))
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregistor(websocket)
        log_main.info("Customer [%s] Disconnected",websocket_id)


asyncio.get_event_loop().run_until_complete(
    websockets.serve(main, "0.0.0.0", 10086))
asyncio.get_event_loop().run_forever()
