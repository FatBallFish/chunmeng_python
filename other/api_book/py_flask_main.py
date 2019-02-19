from flask import Flask,request
import json,MD5
import logging
import psycopg2


app = Flask(__name__)
# 定义数据库连接
conn = psycopg2.connect(database="BOOK",user="postgres",password="wlc570Q0",host="127.0.0.1",port="5432")
print("Opened database successfully")
# 创建游标，用于之后所有的数据库操作
cur = conn.cursor()

home_html = """
    <div>
    <h2><a href="[BOOKID]">[BOOKNAME]</a></h2>
    <p>作者：[AUTHOR]</p>
    <p>简介：[INTRODUCE]</p>
    </div>
    <hr>
"""
book_html = """<li><a href="[CHAPTERID]">[TITLE]</a></li>
"""
@app.route("/")
def home():
    with open('./web/home.html', 'r') as f:
        html = f.read()
    cur.execute("SELECT * FROM book_list")
    rows = cur.fetchall()
    temp =""
    for row in rows:
        temp = temp + home_html
        temp = temp.replace("[BOOKID]",str(row[0])).replace("[BOOKNAME]",row[1]).replace("[INTRODUCE]",row[2]).replace("[AUTHOR]",row[3])
    return html.replace("[BODY]",temp)
@app.route("/ping")
def ping():
    return "<h1><b>pong</b></h1>"
@app.route("/<bookid>",methods=["GET"])
def book(bookid):
    with open('./web/book.html', 'r') as f:
        html = f.read()
    cur.execute("SELECT * FROM book_list WHERE bookid = %d"% int(bookid))
    rows = cur.fetchall()
    num = len(rows)
    if num == 0:
        return "<h1>404 NOT FOUND</h1>"
    elif num >1:
        return "<h1>BOOKID Error.</h1>"
    for row in rows:
        html = html.replace("[BOOKNAME]", row[1]).replace("[INTRODUCE]", row[2]).replace("[AUTHOR]", row[3])
    cur.execute("SELECT * FROM book_text WHERE bookid = %d ORDER BY chapterid ASC" % int(bookid))
    rows = cur.fetchall()
    num = len(rows)
    temp = ""
    for row in rows:
        temp = temp + book_html
        temp = temp.replace("[CHAPTERID]",str(row[1])).replace("[TITLE]",row[2])
    return html.replace("[INDEX]", temp)
@app.route("/<bookid>/<chapterid>",methods=["GET"])
def chapterid(bookid,chapterid):
    with open('./web/chapter.html', 'r') as f:
        html = f.read()
    cur.execute("SELECT * FROM book_list WHERE bookid = %d"%int(bookid))
    rows = cur.fetchall()
    num = len(rows)
    if num == 0:
        return "<h1>404 NOT FOUND</h1>"
    elif num >1:
        return "<h1>BOOKID Error.</h1>"
    for row in rows:
        html = html.replace("[BOOKNAME]", row[1])
    cur.execute("SELECT * FROM book_text WHERE bookid = %d and chapterid = %d ORDER BY chapterid ASC" %
                (int(bookid),int(chapterid)))
    rows = cur.fetchall()
    num = len(rows)
    if num == 1:
        html = html.replace("[TITLE]",rows[0][2])
        # 上一章节
        cur.execute(
            "SELECT * FROM book_text WHERE bookid = %d and chapterid = %d ORDER BY chapterid ASC" %
            (int(bookid), int(chapterid)-1))
        rows = cur.fetchall()
        num = len(rows)
        if num == 1:
            html = html.replace("[UP]", "./"+str(rows[0][1]))
        elif num == 0:
            html = html.replace("[UP]", "###")
        else:
            print("upaddr:有一样的章节id")
            html = html.replace("[UP]", "###")
        # 下一章节
        cur.execute(
            "SELECT * FROM book_text WHERE bookid = %d and chapterid = %d ORDER BY chapterid ASC" %
            (int(bookid), int(chapterid)+1))
        rows = cur.fetchall()
        num = len(rows)
        if num == 1:
            html = html.replace("[DOWN]", "./"+str(rows[0][1]))
        elif num == 0:
            html = html.replace("[DOWN]", "###")
        else:
            print("upaddr:有一样的章节id")
            html = html.replace("[DOWN]", "###")
        # 目录
        html = html.replace("[INDEX]", "./")
    elif num == 0:
        return "<h1>404 NOT FOUND</h1>"
    else:
        return "<h1>CHAPTERID Error</h1>"
    temp = str(rows[0][3])
    temp = temp.replace("\n","<br>")
    return html.replace("[TEXT]",temp)
@app.route("/api/<token>",methods=["POST"])
def api(token):
    if token == MD5.md5("wlc570Q0",salt="BOOK"):
        data = request.json
        #print(data)
        for key in ["id","type","subtype","data"]:
            if not key in data.keys():
                # status -4 parameter type error
                return json.dumps({
                    "id": id,
                    "status": -4,
                    "message": "parameter type error",
                    "data": {}
                })
        id = data["id"]
        if data["type"] == "add":
            if data["subtype"] == "book":
                data = data["data"]
                for key in ["bookname", "author"]:
                    if not key in data.keys():
                        # status -4 parameter type error
                        return json.dumps({
                            "id": id,
                            "status": -4,
                            "message": "parameter type error",
                            "data": {}
                        })
                bookname = data["bookname"]
                author = data["author"]
                if "introduce" in data.keys():
                    introduce = data["introduce"]
                else:
                    introduce = ""
                cur.execute("SELECT * FROM book_list WHERE bookname = '%s' AND author = '%s'"%(bookname,author))
                rows = cur.fetchall()
                num = len(rows)
                if num == 0:
                    import random
                    bookid = random.randint(100000, 999999)
                    try:
                        cur.execute("INSERT INTO book_list (bookid,bookname,introduce,author) "
                                    "VALUES (%d,'%s','%s','%s')" % (bookid, bookname, introduce, author))
                        conn.commit()
                    except Exception as e:
                        logging.error("INSERT record falied,[bookid:%s][bookname:%s]"%(bookid,bookname))
                        # status 3 insert book record failed
                        return json.dumps({
                            "id": id,
                            "status": 3,
                            "message": "insert book record failed",
                            "data":{}
                        })
                    print("add this new book:%d" % bookid)
                    return json.dumps({
                        "id": id,
                        "status": 0,
                        "message": "OK",
                        "data":
                            {"bookid": bookid}
                    })
                elif num == 1:
                    bookid = rows[0][0]
                    # status 1 have this book already,introduce not updated
                    return json.dumps({
                        "id": id,
                        "status": 1,
                        "message": "have this book already,introduce not updated",
                        "data":
                            {"bookid": bookid}
                    })
                else:
                    # status 2 more than 1 records about this book
                    return json.dumps({
                        "id": id,
                        "status": 2,
                        "message": "more than 1 records about this book",
                        "data": {}
                    })
            elif data["subtype"] == "chapter":
                data = data["data"]
                for key in ["bookid", "chapterid","title","text","md5"]:
                    if not key in data.keys():
                        # status -4 parameter type error
                        return json.dumps({
                            "id": id,
                            "status": -4,
                            "message": "parameter type error",
                            "data": {}
                        })
                bookid = data["bookid"]
                try:
                    bookid = int(bookid)
                except Exception as e:
                    # status -4 type parameter type error
                    return json.dumps({
                        "id": id,
                        "status": -4,
                        "message": "parameter type error",
                        "data": {}
                    })
                chapterid = data["chapterid"]
                try:
                    chapterid = int(chapterid)
                except Exception as e:
                    # status -4 type parameter type error
                    return json.dumps({
                        "id": id,
                        "status": -4,
                        "message": "parameter type error",
                        "data": {}
                    })
                title = str(data["title"]).replace("'","\\'")
                text = str(data["text"]).replace("'","\\'")
                md5 = str(data["md5"])
                # 判断章节是否存在
                try:
                    cur.execute(
                        "SELECT * FROM book_text WHERE bookid = %d and chapterid = %d" % (bookid, chapterid))
                except Exception as e:
                    # status 8 select book_text database falied
                    logging.error(e)
                    return json.dumps({
                        "id": id,
                        "status": 8,
                        "message": "select book_text database falied",
                        "data": {}
                    })
                rows = cur.fetchall()
                num = len(rows)
                md5_check = MD5.md5(text, salt="lcworkroom")
                if md5 != md5_check:
                    # status 4 md5 error
                    return json.dumps({
                        "id": id,
                        "status": 4,
                        "message": "md5 error",
                        "data": {}
                    })
                if num == 0:
                    try:
                        cur.execute("INSERT INTO book_text (bookid,chapterid,title,text,md5) "
                                    "VALUES (%d,%d,'%s','%s','%s')" % (
                                        bookid, chapterid, title, text, md5))
                        conn.commit()
                    except Exception as e:
                        # status 5 insert chapter failed
                        logging.error(e)
                        return json.dumps({
                            "id": id,
                            "status": 5,
                            "message": "insert chapter record failed",
                            "data": {}
                        })
                    return json.dumps({
                        "id": id,
                        "status": 0,
                        "message": "OK",
                        "data": {}
                    })
                elif num == 1:
                    if rows[0][4] != md5:
                        # print(text)
                        # print(rows[0][4])
                        # print(md5)
                        print(title, "存在，且md5不一样")
                        try:
                            cur.execute(
                                "UPDATE book_text SET title = '%s',text = '%s',md5 = '%s' WHERE chapterid = %d" % (
                                    title,text,md5,chapterid))
                        except Exception as e:
                            # status 6 update chapter record failed
                            logging.error(e)
                            return json.dumps({
                                "id": id,
                                "status": 6,
                                "message": "update chapter record failed",
                                "data": {}
                            })
                        return json.dumps({
                            "id": id,
                            "status": 0,
                            "message": "OK",
                            "data": {}
                        })
                    else:
                        return json.dumps({
                            "id": id,
                            "status": 0,
                            "message": "OK",
                            "data": {}
                        })
                else:
                    # status 7 more than 1 record of chapter.
                    logging.error("Error,more than 1 record in same chapterid of one book")
                    return json.dumps({
                        "id": id,
                        "status": 7,
                        "message": "more than 1 record about this chapter",
                        "data": {}
                    })
            else:
                # status -3 unkown post subtype
                logging.error("unkown post subtype")
                return json.dumps({
                    "id": id,
                    "status": -3,
                    "message": "unknown post subtype",
                    "data": {}
                })
        elif data["type"] == "delete":
            # status -2 unknown post type
            logging.error("unkown post type")
            return json.dumps({
                "id": id,
                "status": -2,
                "message": "unknown post type",
                "data": {}
            })
        else:
            # status -2 unknown post type
            logging.error("unkown post type")
            return json.dumps({
                "id": id,
                "status": -2,
                "message": "unknown post type",
                "data": {}
            })
    else:
        # status -1 token not allowed
        logging.error("token not allowed")
        return json.dumps({
            "id": id,
            "status": -1,
            "message": "token not allowed",
            "data": {}
        })

if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s"
    DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
    logging.basicConfig(filename="my.log",level=logging.DEBUG,
                        format=LOG_FORMAT,
                        datefmt=DATA_FORMAT)
    app.run(debug=True,host="0.0.0.0",port=5000)