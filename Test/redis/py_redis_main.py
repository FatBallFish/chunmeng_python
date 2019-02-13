# 引用 redis 模块
import redis
import time
# 创建客户端
redis = redis.StrictRedis(password="wlc570Q0")

# r.srt(name,value) 设置普通键值对
response = redis.set("name","王凌超")
print(response)
# r.get(name) 取键对应的值
response = redis.get("name")
print(response)
print(bytes.decode(response))
""" Redis 取到的信息皆为 bytes 型数据，需用 byte.decode(object) 进行转码操作"""
# r.delete(name) 删除普通键值对。(对应redis命令 del)
redis.delete("name")

# r.incr(name.amount) 将值自增 amount 个数值
redis.set("num",10)  # 值可为文本型数字。
redis.incr("num",amount=11)
num = redis.get("num")
print(bytes.decode(num))

# r.expire(name,time) 设置键值对的有效时间，time按秒计。
redis.expire("num",2)
# r.ttl(name) 获取键值对还剩下的有效时间。-1表示永不过期，-2表示已过期。
"""注意：如果在等待过期过程中对键值对重新赋值，那么键值对的TTL将被刷新，即默认永不过期"""
while True:
    ttl = redis.ttl("num")
    print("TTL:",ttl)
    num = redis.get("num")
    if num == None:
        print("the num value:",num)
        break
    print("the num value:",bytes.decode(num))
    time.sleep(1)

# r.persist(name) 将临时密钥转换为持久密钥,TTL变为 None
redis.set("num",1234)
redis.expire("num",5)
ttl = redis.ttl("num")
print("TTL2:",ttl)
redis.persist("num")
ttl = redis.ttl("num")
print("TTL2:",num)
redis.delete("num")


# 设置有序列表
# r.rpush(name,value) 在列表右侧插入数据
redis.rpush("name_list","Denny")  # 在列表右侧插入数据
redis.rpush("name_list","Alice")
# r.lpush(name,value) 在列表左侧插入数据
redis.lpush("name_list","Lisa")  # 在列表左侧插入数据
redis.lpush("name_list","Fuck")

# r.lindex(name, index) 根据索引获取列表内元素
name = redis.lindex("name_list",-1)
print("lindex:",bytes.decode(name))

# ----对整个列表进行超时处理----
redis.expire("name_list",5)
print(redis.ttl("name_list"))
time.sleep(5)
# -----------------------------

# r.lpop(name) 弹出并获取列表左侧第一个元素；
redis.lpop("name_list")  # 删除列表第一个元素
# r.rpop(name) 弹出并获取列表右侧第一个元素；
redis.rpop("name_list")  # 删除列表最后一个元素

## r.lrem(name,count,value) 删除name对应的list中的指定值
# redis.lrem("name_list",0,"Lisa")
# redis.lrem("name_list",0,"Denny")
''' 参数：
    name:  redis的name
    count: count=0 删除列表中所有的指定值；
           count=2 从前到后，删除2个符合的指定值；
           count=-2 从后向前，删除2个符合的指定值；
    value: 要删除的值'''


# r.llen(name) 取列表元素数
name_count= redis.llen("name_list")
# r.lrange(name,start:int,end:int) 获取列表元素从序列 start 到 end 的所有元素内容，-1 表示最后一个元素
name_list = redis.lrange("name_list",0,-1)
# --------输出列表内容---------
print("列表元素数",name_count)
print("列表元素内容:\n",name_list)
name_list = list(name_list)
for name in name_list:
    name = bytes.decode(name)  # 转码
    print(name)
# ----------------------------

# r.ltrim(name,start:int,end:int)  保留从 start 到 end 之间的元素。[start,end]
redis.ltrim("name_list",0,0)
redis.lpop("name_list")
"""上面两句连用可以清空列表"""
