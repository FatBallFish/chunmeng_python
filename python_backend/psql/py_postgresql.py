# coding=utf-8
import psycopg2
import sys,os,configparser
import logging
from configparser import ConfigParser
import datetime
import time,random

log_psql = logging.getLogger("Postgres")
def Initialize(cfg_path:str,main_path:str):
    """
    初始化Postgresql模块
    :param cfg_path: 配置文件路径
    :param main_path: 主程序运行目录
    :return:
    """
    cf = ConfigParser()
    cf.read(cfg_path)
    global host,port,user,password,db,conn
    try:
        host = str(cf.get("PSQL","host"))
        port = int(cf.get("PSQL","port"))
        user = str(cf.get("PSQL","user"))
        password = str(cf.get("PSQL", "pass"))
        db = str(cf.get("PSQL", "db"))
        print("[PSQL]host:",host)
        print("[PSQL]port:", port)
        print("[PSQL]user:", user)
        print("[PSQL]pass:", password)
        print("[PSQL]db:", db)
    except Exception as e:
        log_psql.error("UnkownError:",e)
        print("UnkownError:",e)
        log_psql.info("Program Ended")
        sys.exit()
    try:
        conn = psycopg2.connect(database=db,user=user,password=password,host=host,port=port)
    except Exception as e:
        print("Failed to connect psql database")
        log_psql.error("Failed to connect psql database")
        sys.exit()
    else:
        print("Connect psql database successfully!")
    global Main_filepath
    Main_filepath = main_path

def CheckToken(token:str)->bool:
    """
检查token是否合法，只有当查询到token存在且唯一的时候返回True
    :param token: 用户登录凭证
    :return: 返回判断结果，token正确返回 True ，失败返回 False
    """
    cur = conn.cursor()
    sql = "SELECT * FROM tokens WHERE token = '{}'".format(token)
    try:
        cur.execute(sql)
        # cur.execute("SELECT * FROM tokens")
    except Exception as e:
        print("[CheckToken]Failed to execute sql:{}\nError:{}".format(sql,e))
        log_psql.error("[CheckToken]Failed to execute sql:{}\nError:{}".format(sql,e))
        return False
    # conn.commit()
    rows = cur.fetchall()
    num = len(rows)
    # for row in rows:
    #     #     print(row)
    #     # return True
    if num == 1:
        return True
    elif num == 0:
        print("[CheckToken]Error token")
        log_psql.info("Error token")
        return False
    else:
        print("[CheckToken]Illegal quantity of token")
        return False

def GetUserID(token:str)->int:
    """
    通过token获取用户id
    :param token: 用户token
    :return: 成功返回user_id,失败返回空文本
    """
    cur = conn.cursor()
    sql = "SELECT * FROM tokens WHERE token = '{}'".format(token)
    try:
        cur.execute(sql)
        # cur.execute("SELECT * FROM tokens")
    except Exception as e:
        print("[GetUserID]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[GetUserID]Failed to execute sql:{}\nError:{}".format(sql, e))
        return ""
    # conn.commit()
    rows = cur.fetchall()
    num = len(rows)
    # for row in rows:
    #     #     print(row)
    #     # return True
    if num == 1:
        # print(rows[0])
        user_id = rows[0][1]
        return user_id
    elif num == 0:
        print("[CheckToken]Error token")
        log_psql.info("Error token")
        return 0
    else:
        print("[CheckToken]Illegal quantity of token")
        return 0

def GetUserName(token:str=None,user_id:int=None)->str:
    """
    返回指定token或者user_id所对应的用户名，若两个参数都填写，则优先使用token
    :param token: 用户的token值
    :param user_id: 用户的id
    :return: 返回用户名称，无任何数据返回空文本
    """
    cur = conn.cursor()
    if token != None and token != "":
        sql = "SELECT name FROM users WHERE id = (SELECT user_id FROM tokens WHERE token = '{}')".format(token)
    elif user_id != None and user_id != 0:
        sql = "SELECT name FROM users WHERE id = {}".format(user_id)
    else:
        # 无任何数据，返回空文本
        return ""
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[GetUserName]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[GetUserName]Failed to execute sql:{}\nError:{}".format(sql, e))
        return ""
    if num == 0:
        return ""
    else:
        # 返回第一条记录，理论上也只有一条
        row = cur.fetchone()
        return row[0]
    #todo 2019-7-11 1:04
# 下面的全部要修改
def InsertProperty(**property_dict)->bool:
    """
    新增一条新启事
    :param find_dict: 寻物启事字典
    :return: 成功返回True，失败返回False
    """
    cur = conn.cursor()
    key_sql = ""
    value_sql = ""
    # 最后检查关键字段信息
    if property_dict["publish_time"] == "":
        property_dict["publish_time"] = time.strftime("%Y-%m-%d %H:%M:%S", property_dict["publish_time"])
    if property_dict["update_time"] == "":
        property_dict["update_time"] = property_dict["publish_time"]
    # 进行sql语句拼接
    for key in property_dict.keys():
        key_sql = key_sql + key + ","
        if type(property_dict[key]) == int:
            value_sql = value_sql + str(property_dict[key]) + ","
        elif type(property_dict[key]) == str:
            value_sql = value_sql + "'" + property_dict[key] + "'" + ","
        elif type(property_dict[key]) == time.struct_time:
            value_sql = value_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", property_dict[key]) + "'" + ","
        else:
            print("key:",key,"type:",type(property_dict[key]))
    else:
        # 删除最后多余的 , 符号
        key_sql = key_sql.rpartition(",")[0]
        value_sql = value_sql.rpartition(",")[0]
    sql = "INSERT INTO property ({0}) VALUES ({1})".format(key_sql,value_sql)
    # print(find_dict)
    print("新增启事:\n",sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[InsertProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[InsertProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return False
    else:
        return True

def UpdateProperty(**property_dict)->bool:
    """
    更新寻物启事信息。
    :param property_dict: 启事字典
    :return: 成功返回 True ，失败返回 False
    """
    cur = conn.cursor()
    update_sql = ""
    condition_sql = ""
    # 最后检查关键字段信息
    if property_dict["update_time"] == "" or "update_time" not in property_dict.keys():
        property_dict["update_time"] = time.localtime()
    # 进行sql语句拼接
    for key in property_dict.keys():
        if key == "id":
            if type(property_dict[key]) != str:
                condition_sql = "id = " + str(property_dict[key])
            else:
                condition_sql = "id = " + property_dict[key]
            continue
        update_sql = update_sql + key + "="
        if type(property_dict[key]) == int:
            update_sql = update_sql + str(property_dict[key])
        elif type(property_dict[key]) == str:
            update_sql = update_sql + "'" + property_dict[key] + "'"
        elif type(property_dict[key]) == time.struct_time:
            update_sql = update_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", property_dict[key]) + "'"
        else:
            print("Unknown key:", key, "type:", type(property_dict[key]))
            continue
        update_sql = update_sql + ","
    else:
        update_sql = update_sql.rpartition(",")[0]
    # print("DICT:",find_dict)
    condition_sql = condition_sql + " AND user_id = {}".format(property_dict["user_id"])
    # print("update_sql",update_sql)
    # print("condition_sql:",condition_sql)
    sql = "UPDATE property SET {0} WHERE {1}".format(update_sql, condition_sql)
    # print(find_dict)
    print("更新启事:\n", sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[UpdateProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[UpdateProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return False
    else:
        return True

def DeleteProperty(**property_dict)->bool:
    """
    删除寻物启事信息，只需传递 id、user_id 字段,user_id可缺省。
    :param property_dict: 寻物启事字典
    :return: 成功返回 True ，失败返回 False。
    """
    cur = conn.cursor()
    delete_sql = "DELETE FROM property WHERE "
    # 最后检查关键字段信息
    if "id" and "user_id" not in property_dict.keys():
        return False
    for key in property_dict.keys():
        if type(property_dict[key]) == int:
            delete_sql = delete_sql + key + " = " + str(property_dict[key]) + " AND "
        elif type(property_dict[key]) == str:
            delete_sql = delete_sql + key + " = '" + property_dict[key] + "' AND "
        else:
            print("Unknown key:", key, "type:", type(property_dict[key]))
            continue
    else:
        delete_sql = delete_sql.rpartition(" AND ")[0]
    print("删除启事:\n", delete_sql)

    try:
        cur.execute(delete_sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(delete_sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(delete_sql, e))
        return False
    else:
        return True

def GetProperty(property_type:int,key:str,**property_dict)->tuple:
    """
    获取寻物启事信息
    :param type: 信息类型，1为寻物启事，2为失物招领
    :param key: 关键字，不可与find_dict共存
    :param property_dict: 信息字典，不可与key共存
    :return: 成功返回元组。（记录数，寻物启事信息列表），失败返回（0,[]）
    """
    print("type:{}".format(property_type))
    if key == None or key == "":
        if len(property_dict.keys()) == 0:
            sql = "SELECT * FROM property WHERE type = {} ORDER BY update_time DESC ".format(property_type)
        else:
            sql = "SELECT * FROM property WHERE type = {} AND ".format(property_type)
            for key in property_dict.keys():
                if type(property_dict[key]) == int:
                    sql = sql + key + "=" + str(property_dict[key]) + " AND "
                elif type(property_dict[key]) == str:
                    sql = sql + key + " LIKE '%" + property_dict[key] + "%' AND "
                elif type(property_dict[key]) == time.struct_time:
                    sql = sql + key + "='" + time.strftime("%Y-%m-%d %H:%M:%S", property_dict[key]) + "' AND "
                else:
                    print("key:", key, "type:", type(property_dict[key]))
            else:
                sql = sql.rpartition("AND")[0]
                sql = sql + "ORDER BY update_time DESC"
    else:
        if len(property_dict.keys()) != 0:
            print("Error,key can't be used when other args appeared.")
            return (-1,"")
        sql = "SELECT * FROM property " \
              "WHERE type = {0} AND(lab LIKE '%{1}%' OR title LIKE '%{1}%' OR content LIKE '%{1}%')" \
              "ORDER BY update_time DESC".format(property_type,key)
    print("GetProperty_SQL:",sql)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return (0,[])
    rows = cur.fetchall()
    num = len(rows)
    print("总共有{}条记录".format(len(rows)))
    date_list = []
    for row in rows:
        # print(row)
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
            "pic_num":0,
            "pic_url1":"",
            "pic_url2":"",
            "pic_url3":"",
        }
        i = 0
        for key in property_dict:
            if key == "occurrence_time" or key == "publish_time" or key == "update_time":
                property_dict[key] = str(row[i])
                i += 1
                continue
            property_dict[key] = row[i]
            i += 1
        date_list.append(property_dict)
        # print("datalist：",date_list)
    print("datalist：", date_list)
    return (num,date_list)

# 学生自营平台
def CheckShopName(shopname:str)->bool:
    """
检查商店名是否存在，若不存在返回真
    :param shopname:
    :return:存在或无法查询返回假，不存在返回真
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(shop_name) AS num FROM shop WHERE shop_name = '{}'".format(shopname)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return False

    row = cur.fetchone()
    print("shop num:{}".format(row[0]))
    if row[0] == 0:
        return True
    else:
        return False

def CheckShopNum(user_id:int,num:int=3)->bool:
    """
检查用户开店数量，若店铺数量小于可创建数，返回真，否则假
    :param user_id: 用户id
    :param num: 可创建店铺数量，默认为3
    :return: 若店铺数量小于可创建数，返回真，否则假
    """
    cur = conn.cursor()
    sql = "SELECT COUNT(user_id) AS num FROM shop WHERE user_id = {}".format(user_id)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return False

    row = cur.fetchone()
    if row[0] < num :
        return True
    else:
        return False

def GetShopOwner(shop_id:int)->int:
    """
获取店铺所有者id
    :param shop_id:店铺id
    :return: 返回用户id
    """
    cur = conn.cursor()
    sql = "SELECT user_id FROM shop WHERE shop_id = {}".format(shop_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return -1
    row = cur.fetchone()
    print("row:",row)
    if row == None:  # 无此店铺
        return -1
    row2 = cur.fetchone()
    print("row2",row2)
    if row2 != None:
        print("店铺id：{} 有多条记录！".format(shop_id))
        log_psql.error("店铺id：{} 有多条记录！".format(shop_id))
        return -1
    user_id = row[0]
    return user_id

def CreatShop(shop_name:str,user_id:int,id:int=-1)->dict:
    """
创建一个店铺
    :param shop_name: 店铺名
    :param user_id: 用户id，作为店铺拥有者
    :param id: 请求传递过来的事件id
    :return: 返回结果字典
    """
    cur = conn.cursor()
    if CheckShopName(shop_name) == False:
        # status 100 店铺名已被注册
        return {"status": 100, "message": "The shop name was used","data":{}}
    if CheckShopNum(user_id) == False:
        # status 101 店铺数量已超上限
        return {"status":101,"message":"The number of shops has been capped","data":{}}

    # 生成 shop_id 并判断是否重复
    while True:
        shop_id = random.randint(10**8*2,10**9-1)  # 9位id
        check_sql = "SELECT COUNT(shop_id) as num FROM shop WHERE shop_id = {}".format(shop_id)
        try:
            cur.execute(check_sql)
            conn.commit()
        except Exception as e:
            print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
            log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
            # status -200 数据库操作失败。
            return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
        row = cur.fetchone()
        num = row[0]
        if num == 0 :
            break

    creat_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "INSERT INTO shop VALUES ({0},'{1}',{2},{3},'{4}')".format(shop_id,shop_name,"''",user_id,creat_time)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 创建店铺成功！返回shop_id
    return {"status":0,"message":"successful","data":{"shop_id":shop_id}}

def UpdateShop(shop_id:int,shop_content:str,user_id:int,pic_url:str,id:int=-1)->dict:
    """
更新店铺的内容
    :param shop_id: 店铺id
    :param shop_content: 店铺内容
    :param user_id: token中用户id
    :param id: 请求传递过来的事件id
    :return: json_dict
    """
    cur = conn.cursor()
    if GetShopOwner(shop_id) != user_id:
        # status 100 无权更新他人的店铺信息
        return {"status":100,"message":"No right to update","data":{}}
    sql = "UPDATE shop SET shop_content = '{0}' ,`pic_url`='{1}' WHERE shop_id = {2}".format(shop_content,pic_url,shop_id)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[UpdateShop]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[UpdateShop]Failed to execute sql:{}\nError:{}".format(sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 更新店铺信息成功！无返回
    return {"id":id,"status": 0, "message": "successful", "data": {}}

def GetShopList(shop_name:str,order:str="",id:int=-1)->dict:
    """
获取店铺列表，并以制定规则进行排序
    :param shop_name: 店铺名称关键字
    :param order: 排序规则，sql语句
    :param id: 请求传递过来的事件id
    :return: 返回json_dict
    """
    cur = conn.cursor()
    if shop_name == "" or shop_name == None:
        sql = "SELECT * FROM shop"
    else:
        sql = "SELECT * FROM shop WHERE shop_name LIKE '%{}%'".format(shop_name)
    if order != "":
        sql = sql + " ORDER BY {}".format(order)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    print(sql)
    # todo 这里的num无效
    if num == 0:
        # status 1 空记录
        return {"id": id, "status": 1, "message": "Empty records", "data": {}}
    else:
        shop_list = []
        rows = cur.fetchall()
        for row in rows:
            shop_dict = {}
            shop_dict["shop_id"] = row[0]
            shop_dict["shop_name"] = row[1]
            shop_dict["shop_content"] = row[2]
            shop_dict["user_id"] = row[3]
            shop_dict["user_name"] = GetUserName(user_id=row[3])
            shop_dict["creat_time"] = str(row[4])
            shop_dict["pic_url"] = str(row[5])
            shop_list.append(shop_dict)
        # status 0 成功获取店铺列表，返回列表数组
        return {"id":id,"status":0,"message":"successful","data":shop_list}

def GetShopInfo(shop_name:str="",shop_id:int=0,id:int=-1)->dict:
    """
获取店铺信息，不同于获取店铺列表，此命令对店铺名或店铺id进行全字匹配，且只返回一组结果。两个参数都传值选择店铺id
    :param shop_name: 店铺名称，默认为空
    :param shop_id: 店铺id，默认为0
    :param id: 请求传递过来的事件id
    :return: 返回json_dict
    """
    cur = conn.cursor()
    if shop_id != 0 and shop_id != None:
        sql = "SELECT * FROM shop WHERE shop_id  = {}".format(shop_id)
        try:
            num = cur.execute(sql)
            conn.commit()
        except Exception as e:
            print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
            log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
            # status -200 数据库操作失败。
            return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    elif shop_name != "" and shop_name != None:
        sql = "SELECT * FROM shop WHERE shop_name = '{}'".format(shop_name)
        try:
            num = cur.execute(sql)
            conn.commit()
        except Exception as e:
            print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
            log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
            # status -200 数据库操作失败。
            return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    else:
        # status -201 关键键值对值不可为空
        return {"id": id, "status": -201, "message": "Necessary key-value can't be empty", "data": {}}

    if num == 0:
        # status 1 空记录
        return {"id": id, "status": 1, "message": "Empty records", "data": {}}
    else:
        row = cur.fetchone()
        shop_info = {}
        shop_info["shop_id"] = row[0]
        shop_info["shop_name"] = row[1]
        shop_info["shop_content"] = row[2]
        shop_info["user_id"] = row[3]
        shop_info["creat_time"] = str(row[4])
        shop_info["pic_url"] = str(row[5])
        # status 0 成功获取店铺信息
        return {"id": id, "status": 0, "message": "successful", "data": shop_info}

def GetProductOwner(product_id:int)->int:
    """
获取产品所在shop_id
    :param product_id: 产品id
    :return: 返回店铺id
    """
    cur = conn.cursor()
    sql = "SELECT shop_id FROM product WHERE product_id = {}".format(product_id)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        return -1
    row = cur.fetchone()
    print("row:", row)
    if row == None:  # 无此店铺
        return -1
    row2 = cur.fetchone()
    print("row2", row2)
    if row2 != None:
        print("店铺id：{} 有多条记录！".format(product_id))
        log_psql.error("店铺id：{} 有多条记录！".format(product_id))
        return -1
    shop_id = row[0]
    return shop_id

def CreatProduct(user_id:int,id:int=-1,**product_dict):
    """
上架新商品
    :param user_id: 用户id，用于验证店铺是否属于该用户
    :param product_dict: 产品信息字典，其中必包含，product_name,shop_id
    :return: json字典
    """
    cur = conn.cursor()
    for key in ["product_name","shop_id","product_status"]:
        if key not in product_dict.keys():
            # status -202 缺少关键的键值对
            return {"id":id,"status":-202,"message":"Missing necessary data key-value","data":{}}
    product_name = product_dict["product_name"]
    shop_id = product_dict["shop_id"]
    owner_id = GetShopOwner(shop_id)
    print("user_id:",user_id,"owner_id:",owner_id)
    if user_id != owner_id:
        # status 100 操作者不是店铺所有人，无权操作。
        return {"id":id,"status":100,"message":"No right to operate","data":{}}

    # 生成 product_id 并判断是否重复
    while True:
        product_id = random.randint(10**6*2,10**7-1)  # 7位id
        check_sql = "SELECT COUNT(product_id) as num FROM product WHERE product_id = {}".format(product_id)
        try:
            cur.execute(check_sql)
            conn.commit()
        except Exception as e:
            print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
            log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
            # status -200 数据库操作失败。
            return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
        row = cur.fetchone()
        num = row[0]
        if num == 0 :
            break
    product_dict["product_id"] = product_id
    product_dict["creat_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    product_dict["product_sale"] = 0
    product_dict["product_click"] = 0
    product_dict["product_collection"] = 0
    key_sql = ""
    value_sql = ""
    for key in product_dict.keys():
        key_sql = key_sql + key + ","
        if type(product_dict[key]) == int or type(product_dict[key]) == float:
            value_sql = value_sql + str(product_dict[key]) + ","
        elif type(product_dict[key]) == str:
            value_sql = value_sql + "'" + product_dict[key] + "'" + ","
        elif type(product_dict[key]) == time.struct_time:
            value_sql = value_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", product_dict[key]) + "'" + ","
        else:
            print("key:",key,"type:",type(product_dict[key]))
    else:
        # 删除最后多余的 , 符号
        key_sql = key_sql.rpartition(",")[0]
        value_sql = value_sql.rpartition(",")[0]
    sql = "INSERT INTO product ({0}) VALUES ({1})".format(key_sql,value_sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(check_sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 成功上架产品,返回产品id
    return {"id":id,"status":0,"message":"successful","data":{"product_id":product_id}}

def UpdateProduct(user_id:int,id:int=-1,**product_dict):
    """
更新商品信息
    :param user_id: 用户id，用于验证店铺是否属于该用户
    :param product_dict: 产品信息字典，其中必包含，product_name,shop_id
    :return: json字典
    """
    cur = conn.cursor()
    for key in ["product_id", "shop_id"]:
        if key not in product_dict.keys():
            # status -202 缺少关键的键值对
            return {"id": id, "status": -202, "message": "Missing necessary data key-value", "data": {}}
    product_id = product_dict["product_id"]
    shop_id = product_dict["shop_id"]
    owner_id = GetShopOwner(shop_id)
    owner2_id = GetProductOwner(product_id)
    # todo 增加获取产品id所在店铺
    if user_id != owner_id:
        # status 100 操作者不是店铺所有人，无权操作。
        return {"id": id, "status": 100, "message": "No right to operate", "data": {}}
    if shop_id != owner2_id:
        # status 100 产品不是店铺所有，无权操作。
        return {"id": id, "status": 100, "message": "No right to operate", "data": {}}

    product_dict["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "UPDATE product SET "
    for key in product_dict.keys():
        if key == "product_id":
            continue
        if key == "shop_id":
            continue
        if key == "creat_time":
            continue
        if type(product_dict[key]) == int or type(product_dict[key]) == float:
            sql = sql + key + " = " + str(product_dict[key]) + " ,"
            # value_sql = value_sql + str(product_dict[key]) + ","
        elif type(product_dict[key]) == str:
            sql = sql + key + " = '" + product_dict[key] + "' ,"
            # value_sql = value_sql + "'" + product_dict[key] + "'" + ","
        elif type(product_dict[key]) == time.struct_time:
            sql = sql + key + " = '" + time.strftime("%Y-%m-%d %H:%M:%S", product_dict[key]) + "' ,"
            # value_sql = value_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", product_dict[key]) + "'" + ","
        else:
            print("key:", key, "type:", type(product_dict[key]))
    else:
        # 删除最后多余的 , 符号
        sql = sql.rpartition(",")[0]
        # key_sql = key_sql.rpartition(",")[0]
        # value_sql = value_sql.rpartition(",")[0]
    # todo 更改sql语句
    sql = sql + " WHERE product_id = {} AND shop_id = {}".format(product_id,shop_id)
    # sql = "INSERT INTO product ({0}) VALUES ({1})".format(key_sql, value_sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 成功上架产品,返回产品id
    return {"id": id, "status": 0, "message": "successful", "data": {}}

def GetProductList(product_name:str="",product_key:str="",shop_id:int=0,order:str="",type:str="up",id:int=-1):
    """
获取商品列表
    :param product_name: 商品名称关键字，为空代表检索全部
    :param shop_id: 店铺id，如果此值非 0 则与 product_name 进行 与 运算
    :param order: 排序规则，SQL语句
    :param type: 可被检索的商品类型，up 已上架商品，down 已下架商品， del 已删除商品，all除已删除外全部商品。默认 up
    :param id: 事件传递id
    :return: json结果字典
    """
    cur = conn.cursor()
    sql = "SELECT * FROM product WHERE"
    if product_name != "":
        sql = sql + " product_name LIKE '%{}%' AND".format(product_name)
    if product_key != "":
        sql = sql + " product_key LIKE '%{}%' AND".format(product_key)
    if shop_id != 0 :
        sql = sql + " shop_id = {} AND".format(shop_id)
    if type == "up":
        sql = sql + " product_status = 1 "
    elif type == "down":
        sql = sql + " product_status = 0 "
    elif type == "all":
        sql = sql + " (product_status = 1 OR product_status = 0) "
    elif type == "del":
        sql = sql + " product_status = 2 "
    else:
        # status -204 键值对数据错误
        return {"id":id,"status":-204,"message":"Arg's value error","data":{}}
    if order != "":
        sql = sql + "ORDER BY {}".format(order)
    try:
        num = cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        log_psql.error("[DeleteProperty]Failed to execute sql:{}\nError:{}".format(sql, e))
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    print(sql)
    # todo 这里的num无效
    if num == 0:
        # status 1 空记录
        return {"id": id, "status": 1, "message": "Empty records", "data": {}}
    else:
        product_list = []
        rows = cur.fetchall()
        for row in rows:
            product_dict = {}
            product_dict["product_id"] = row[0]
            product_dict["product_name"] = row[1]
            product_dict["product_content"] = row[2]
            product_dict["product_key"] = row[3]
            print(row[4],row[5])
            product_dict["product_price"] = float(row[4])
            if row[5] == None:
                product_dict["product_disprice"] = row[5]
            else:
                product_dict["product_disprice"] = float(row[5])
            product_dict["product_sale"] = row[6]
            product_dict["product_click"] = row[7]
            product_dict["product_collection"] = row[8]
            product_dict["shop_id"] = row[9]
            product_dict["creat_time"] = str(row[10])
            product_dict["update_time"] = str(row[11])
            product_dict["product_pic"] = row[12]
            product_dict["product_status"] = row[13]
            product_list.append(product_dict)
        # status 0 成功获取店铺列表，返回列表数组
        return {"id": id, "status": 0, "message": "successful", "data": product_list}


if __name__ == '__main__':
    Initialize("../config.ini",os.path.dirname(os.path.abspath(__file__)))
    # result = CheckToken("9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac")
    result = CheckShopName("微凉的第一个店铺")
    print(result)
    # find_dict = {
    #     "state": -1,
    #     "lab": "a",
    #     "title": "b",
    #     "content": "c",
    #     "find_time": "d",
    #     "loser_name": "e",
    #     "loser_phone": "f",
    #     "loser_qq": "g",
    #     "finder_name": "h",
    #     "finder_phone": "i",
    #     "finder_qq": "j",
    #     "user_id": "k",
    #     "publish_time": time.localtime(),
    #     "update_time": "m",
    # }
    # InsertFindProperty(**find_dict)
    # print(GetProperty(1,"我丢了个许淳皓"))

    conn.close()