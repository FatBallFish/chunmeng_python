# 引用 postgresql 模块
import psycopg2
# 定义数据库连接
conn = psycopg2.connect(database="bluezone_db",user="postgres",password="wlc570Q0",host="127.0.0.1",port="5432")
print("Opened database successfully")
# 创建游标，用于之后所有的数据库操作
cur = conn.cursor()
# cur.execute() 执行SQL语句，SQL语句可被参数化，即 cur.execute("SELECT * FROM %s where id=1",tabel_name)


# 添加纪录
cur.execute("INSERT INTO students (name,nickname,phone,email,number) "
            "VALUES ('杨凯威','Sakura','13750687010','893721708@qq.com','1180310082')")
conn.commit()
print("Records create successfully")

# 更新记录
cur.execute("UPDATE students SET phone = '123456' WHERE number = '1180310082'")

# 查找记录
cur.execute("SELECT * FROM students")
rows = cur.fetchall()
print("学号\t姓名\t网名\t手机\t邮箱")
for row in rows:
    print(row[4],end="\t")
    print(row[0],end="\t")
    print(row[1],end="\t")
    print(row[2],end="\t")
    print(row[3],end="\t")
    print("")
print("OVER")
conn.close()
