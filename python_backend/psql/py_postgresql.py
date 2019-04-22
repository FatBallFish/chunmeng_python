# coding=utf-8
import psycopg2
import sys,os,configparser
import logging
from configparser import ConfigParser
import datetime
import time

log_psql = logging.getLogger("Postgres")
def Initialize(cfg_path,main_path):
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
    :return: 返回判断结果
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

def GetUserID(token)->str:
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


if __name__ == '__main__':
    Initialize("../config.ini",os.path.dirname(os.path.abspath(__file__)))
    result = CheckToken("9763393e42ef2b8f051caefbec8a522f31a38663a7180d69d1a9cb1addaa76ac")
    find_dict = {
        "state": -1,
        "lab": "a",
        "title": "b",
        "content": "c",
        "find_time": "d",
        "loser_name": "e",
        "loser_phone": "f",
        "loser_qq": "g",
        "finder_name": "h",
        "finder_phone": "i",
        "finder_qq": "j",
        "user_id": "k",
        "publish_time": time.localtime(),
        "update_time": "m",
    }
    InsertFindProperty(**find_dict)
    print(result)
    conn.close()