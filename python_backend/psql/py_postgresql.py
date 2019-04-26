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

def InsertFindProperty(**find_dict)->bool:
    """
    新增一条新寻物启事
    :param find_dict: 寻物启事字典
    :return: 成功返回True，失败返回False
    """
    cur = conn.cursor()
    key_sql = ""
    value_sql = ""
    # 最后检查关键字段信息
    if find_dict["publish_time"] == "":
        find_dict["publish_time"] = time.strftime("%Y-%m-%d %H:%M:%S", find_dict["publish_time"])
    if find_dict["update_time"] == "":
        find_dict["update_time"] = find_dict["publish_time"]
    # 进行sql语句拼接
    for key in find_dict.keys():
        key_sql = key_sql + key + ","
        if type(find_dict[key]) == int:
            value_sql = value_sql + str(find_dict[key]) + ","
        elif type(find_dict[key]) == str:
            value_sql = value_sql + "'" + find_dict[key] + "'" + ","
        elif type(find_dict[key]) == time.struct_time:
            value_sql = value_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", find_dict[key]) + "'" + ","
        else:
            print("key:",key,"type:",type(find_dict[key]))
    else:
        key_sql = key_sql.rpartition(",")[0]
        value_sql = value_sql.rpartition(",")[0]
    sql = "INSERT INTO findproperty ({0}) VALUES ({1})".format(key_sql,value_sql)
    # print(find_dict)
    print("新增寻物启事:\n",sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        log_psql.error(e)
        return False
    else:
        return True

def UpdateFindProperty(**find_dict)->bool:
    """
    更新寻物启事信息。
    :param find_dict: 寻物启事字典
    :return: 成功返回 True ，失败返回 False
    """
    cur = conn.cursor()
    update_sql = ""
    condition_sql = ""
    # 最后检查关键字段信息
    if find_dict["update_time"] == "" or "update_time" not in find_dict.keys():
        find_dict["update_time"] = time.localtime()
    # 进行sql语句拼接
    for key in find_dict.keys():
        if key == "id":
            if type(find_dict[key]) != str:
                condition_sql = "id = " + str(find_dict[key])
            else:
                condition_sql = "id = " + find_dict[key]
            continue
        update_sql = update_sql + key + "="
        if type(find_dict[key]) == int:
            update_sql = update_sql + str(find_dict[key])
        elif type(find_dict[key]) == str:
            update_sql = update_sql + "'" + find_dict[key] + "'"
        elif type(find_dict[key]) == time.struct_time:
            update_sql = update_sql + "'" + time.strftime("%Y-%m-%d %H:%M:%S", find_dict[key]) + "'"
        else:
            print("Unknown key:", key, "type:", type(find_dict[key]))
            continue
        update_sql = update_sql + ","
    else:
        update_sql = update_sql.rpartition(",")[0]
    # print("DICT:",find_dict)
    condition_sql = condition_sql + " AND user_id = '" + str(find_dict["user_id"]) + "'"
    # print("update_sql",update_sql)
    # print("condition_sql:",condition_sql)
    sql = "UPDATE findproperty SET {0} WHERE {1}".format(update_sql, condition_sql)
    # print(find_dict)
    print("更新寻物启事:\n", sql)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print("Database Error:",e)
        log_psql.error(e)
        return False
    else:
        return True

def DeleteProperty(**find_dict)->bool:
    """
    删除寻物启事信息，只需传递 id、user_id 字段,user_id可缺省。
    :param find_dict: 寻物启事字典
    :return: 成功返回 True ，失败返回 False。
    """
    cur = conn.cursor()
    delete_sql = "DELETE FROM findproperty WHERE "
    # 最后检查关键字段信息
    if "id" and "user_id" not in find_dict.keys():
        return False
    for key in find_dict.keys():
        if type(find_dict[key]) == int:
            delete_sql = delete_sql + key + " = " + str(find_dict[key]) + " AND "
        elif type(find_dict[key]) == str:
            delete_sql = delete_sql + key + " = '" + find_dict[key] + "' AND "
        else:
            print("Unknown key:", key, "type:", type(find_dict[key]))
            continue
    else:
        delete_sql = delete_sql.rpartition(" AND ")[0]
    print("删除寻物启事:\n", delete_sql)

    try:
        cur.execute(delete_sql)
        conn.commit()
    except Exception as e:
        print("Database Error:",e)
        log_psql.error(e)
        return False
    else:
        return True

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

def GetFindProperty(key:str,**find_dict)->tuple:
    """
    获取寻物启事信息
    :param key: 关键字，不可与find_dict共存
    :param find_dict: 寻物启事字典，不可与key共存
    :return: 成功返回元组。（记录数，寻物启事信息列表），失败返回（0,[]）
    """
    if key == None or key == "":
        if len(find_dict.keys()) == 0:
            sql = "SELECT * FROM findproperty ORDER BY update_time DESC "
        else:
            sql = "SELECT * FROM findproperty WHERE "
            for key in find_dict.keys():
                if type(find_dict[key]) == int:
                    sql = sql + key + "=" + str(find_dict[key]) + " AND "
                elif type(find_dict[key]) == str:
                    sql = sql + key + " LIKE '%" + find_dict[key] + "%' AND "
                elif type(find_dict[key]) == time.struct_time:
                    sql = sql + key + "='" + time.strftime("%Y-%m-%d %H:%M:%S", find_dict[key]) + "' AND "
                else:
                    print("key:", key, "type:", type(find_dict[key]))
            else:
                sql = sql.rpartition("AND")[0]
                sql = sql + "ORDER BY update_time DESC"
    else:
        if len(find_dict.keys()) != 0:
            print("Error,key can't be used when other args appeared.")
            return (-1,"")
        sql = "SELECT * FROM findproperty WHERE lab LIKE '%{0}%' OR title LIKE '%{0}%' OR content LIKE '%{0}%' " \
              "ORDER BY update_time DESC".format(key)
    print("GetFindProperty_SQL:",sql)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    num = len(rows)
    # print("总共有{}条记录".format(len(rows)))
    date_list = []
    for row in rows:
        # print(row)
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
        i = 0
        for key in find_dict:
            if key == "lost_time" or key == "publish_time" or key == "update_time":
                find_dict[key] = str(row[i])
                i += 1
                continue
            find_dict[key] = row[i]
            i += 1
        date_list.append(find_dict)
        # print("datalist：",date_list)
    print("datalist：", date_list)
    return (num,date_list)





if __name__ == '__main__':
    Initialize("../config.ini",os.path.dirname(os.path.abspath(__file__)))
    result = CheckToken("9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac")
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
    print(GetFindProperty("我丢了个许淳皓"))

    conn.close()