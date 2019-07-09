# coding=utf-8
import psycopg2
import sys,os,configparser
import logging
from configparser import ConfigParser
import datetime
import time

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
    try:
        cur.execute("SELECT * FROM tokens WHERE token = '{}'".format(token))
        # cur.execute("SELECT * FROM tokens")
    except Exception as e:
        print("[CheckToken]Error:",e)
        log_psql.error(e)
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

def GetUserID(token:str)->str:
    """
    通过token获取用户id
    :param token: 用户token
    :return: 成功返回user_id,失败返回空文本
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM tokens WHERE token = '{}'".format(token))
        # cur.execute("SELECT * FROM tokens")
    except Exception as e:
        print("[CheckToken]Error:", e)
        log_psql.error(e)
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
        return ""
    else:
        print("[CheckToken]Illegal quantity of token")
        return ""

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
        print(e)
        log_psql.error(e)
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
    condition_sql = condition_sql + " AND user_id = '" + str(property_dict["user_id"]) + "'"
    # print("update_sql",update_sql)
    # print("condition_sql:",condition_sql)
    sql = "UPDATE property SET {0} WHERE {1}".format(update_sql, condition_sql)
    # print(find_dict)
    print("更新启事:\n", sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("Database Error:",e)
        log_psql.error(e)
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
        print("Database Error:",e)
        log_psql.error(e)
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
    if key == None or key == "":
        if len(property_dict.keys()) == 0:
            sql = "SELECT * FROM property WHERE type={} ORDER BY update_time DESC ".format(property_type)
        else:
            sql = "SELECT * FROM property WHERE "
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
              "WHERE type={0} AND(lab LIKE '%{1}%' OR title LIKE '%{1}%' OR content LIKE '%{1}%')" \
              "ORDER BY update_time DESC".format(property_type,key)
    print("GetProperty_SQL:",sql)
    cur = conn.cursor()
    cur.execute(sql)
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
            "user_id": "",
            "user_name": "",
            "user_phone": "",
            "user_qq": "",
            "user2_id": "",
            "user2_name": "",
            "user2_phone": "",
            "user2_qq": "",
            "publish_time": "",
            "update_time": "",
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
        print(e)
        log_psql.error(e)
        return False

    row = cur.fetchone()
    if row[0] == 1:
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
        print(e)
        log_psql.error(e)
        return False

    row = cur.fetchone()
    if row[0] <= num :
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
        print(e)
        log_psql.error(e)
        return -1
    if num == 1:
        row = cur.fetchone()
        user_id = row[0]
        return user_id
    if num == 0:  # 无此店铺
        return -1
    else:
        print("店铺id：{} 有多条记录！".format(shop_id))
        log_psql.error("店铺id：{} 有多条记录！".format(shop_id))
        return -1

def CreatShop(shop_name:str,user_id:int)->dict:
    """
    创建一个店铺
    :param shopname: 店铺名
    :return: 返回结果字典
    """
    cur = conn.cursor()
    if CheckShopName(shop_name) == False:
        # status 100 店铺名已被注册
        return {"status": 100, "message": "The shop name was used","data":{}}
    if CheckShopNum(user_id) == False:
        # status 101 店铺数量已超上限
        return {"status":101,"message":"The number of shops has been capped","data":{}}
    shop_id = int(time.time()*10**8)
    creat_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "INSERT INTO shop VALUES ({0},{1},{2},{3},{4})".format(shop_id,shop_name,"",user_id,creat_time)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        log_psql.error(e)
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 创建店铺成功！返回shop_id
    return {"status":0,"message":"successful","data":{"shop_id":shop_id}}

def UpdateShop(shop_id:int,content:str,user_id:int)->dict:
    """
    更新店铺的内容
    :param shopid: 店铺id
    :param content: 店铺内容
    :param user_id: token中用户id
    :return: json_dict
    """
    cur = conn.cursor()
    if GetShopOwner(shop_id) != user_id:
        # status 100 无权更新他人的店铺信息
        return {"status":100,"message":"No right to update","data":{}}
    sql = "UPDATE shop SET content = '{0}' WHERE shop_id = {1}}".format(content,shop_id)
    try:
        cur.execute()
        conn.commit()
    except Exception as e:
        print(e)
        log_psql.error(e)
        # status -200 数据库操作失败。
        return {"id": id, "status": -200, "message": "Failure to operate database", "data": {}}
    # status 0 更新店铺信息成功！无返回
    return {"status": 0, "message": "successful", "data": {}}


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