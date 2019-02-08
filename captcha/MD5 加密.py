import hashlib
def md5_passwd(str,salt='bluezone'):
    #satl是盐值，默认是123456
    str=str+salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(str.encode())
    res = md.hexdigest()
    return res

md5_data = md5_passwd("N4Fsx")
print(md5_data)