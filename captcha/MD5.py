import hashlib
def md5(str,salt='bluezone'):
    #satl是盐值，默认是123456
    str=str+salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(str.encode())
    res = md.hexdigest()
    return res
if __name__ == "__main__":
    print(md5("nDtg4"))