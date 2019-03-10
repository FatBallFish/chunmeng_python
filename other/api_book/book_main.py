# 这个版本打算不使用LOCK，用线程池读取完信息后再拼接数据。
import threading
import queue
from bs4 import BeautifulSoup
import requests,json
import sys,logging
import time
import psycopg2
import MD5

LOG_FORMAT = "[%(asctime)-15s] - [%(name)10s]\t- [%(levelname)s]\t- [%(funcName)-20s:%(lineno)3s]\t- [%(message)s]"
DATA_FORMAT = "%Y.%m.%d %H:%M:%S %p "
logging.basicConfig(filename="my.log", level=logging.INFO,
                    format=LOG_FORMAT.center(30),
                    datefmt=DATA_FORMAT)
log_main = logging.getLogger(__name__)
exitFlag = 0
address_List = []
title_List = []
ebook_list = []
Error_list = []
class downloader(object):
    def __init__(self):
        self.link_list = []
        self.num = 0  # 章节数
        self.content = ""
        self.bookid = 0
        self.bookname = ""
        self.author = ""
        self.introduce = ""

    def start(self,content):
        self.content = content
        req = requests.get(url=self.content)
        req.encoding = "gbk"
        html = req.text
        bf = BeautifulSoup(html, "html.parser")
        indexs = bf.find("meta", property="og:novel:book_name")
        self.bookname = indexs.get("content")
        indexs = bf.find("meta",property="og:novel:author")
        self.author = indexs.get("content")
        indexs = bf.find("meta", property="og:description")
        self.introduce = indexs.get("content")
        print(self.bookname,self.author,self.introduce)

    def get_index(self):
        req = requests.get(url = self.content)
        req.encoding = "gbk"
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        indexs = str(bf.find_all('div', id = 'list')[0])
        indexs = indexs.partition("正文</dt>")[2]
        indexs = indexs.partition("</dl>")[0]
        bf = BeautifulSoup(indexs, "html.parser")
        indexs = bf.find_all("a")

        for index in indexs:
            # content,a,title = title.partition(" ")
            # content = content.partition("第")[2].partition("章")[0]
            # # print("第%s章 %s" % (index,title))
            link_dict = {"title":index.string,"link":self.content+index.get("href")}
            self.link_list.append(link_dict)
        self.num = len(self.link_list)
        # self.num = 1
        # print(indexs)

    def get_text(self,target):
        # target = 'https://www.booktxt.net/0_595/128833.html'
        try:
            req = requests.get(url = target)
        except:
            #print("Get Error: %s")
            return "Get Error"
        req.encoding = "gbk"
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        texts = bf.find_all('div', id = 'content')
        # print(len(texts))
        # print(texts)
        if len(texts)>0:
            passage = str(texts[0])
            passage = passage.replace("<br/>","\n").replace("&nbsp;"," ")
            passage = passage.partition('<div id="content">')[2]
            passage = passage.partition("</div>")[0]
            passage.strip()
            return passage
        else:
            return "Get Error"

    def writer(self,path,title,text):
        write_flag = True
        with open(path, 'a', encoding='utf-8') as f:
            f.write(title + '\n')
            f.writelines(text)
            f.write('\n\n')
        # f.close()


class MyThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print("开启线程：" + self.name)
        process_data(self.name,self.q)
        print("退出进程：" + self.name)

def post_chapter(bookid,chapterid,title,text):
    md5 = MD5.md5(text, salt="lcworkroom")
    headers = {'content-type': 'application/json'}
    json_data = json.dumps({
        "id": time.time(),
        "type": "add",
        "subtype": "chapter",
        "data":
            {"bookid": bookid, "chapterid": chapterid, "title": title, "text": text, "md5": md5}
    })
    response = requests.post("https://www.lcworkroom.cn/book/api/%s" % MD5.md5("wlc570Q0", salt="BOOK"), data=json_data,
                             headers=headers)
    try:
        data = json.loads(response.text)
    except Exception as e:
        print(response.text)
        logging.error(e)
        return "Get Error"
    if not "status" in data.keys():
        logging.error("response type error")
        print("response type error")
        sys.exit()
    if data["status"] == 0:
        pass
        #print("add this new chapter")
    else:
        logging.error(data["message"])
        print(data["message"])
        sys.exit()

def process_data(threadname, q):
    while not exitFlag:
        #queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            # print("%s processing %s" % (threadname, data))
            index = address_List.index(data)
            text = dl.get_text(data)
            title = title_List[index]
            if text == "Get Error":
                print("Get Error:章节 %s 下载失败" % title)
                Error_list.append((index,title,data))
            else:
                ebook_list.append((index,title,text))
            post_chapter(bookid=dl.bookid,chapterid=index,title=title,text=text)
            # dl.writer("全职法师.txt", title, text)
            sys.stdout.write("  已下载:%.3f%%" % float(index / dl.num * 100) + '\r')
            sys.stdout.flush()
            # queueLock.release()
        else:
            pass

        #queueLock.release()
        time.sleep(1)

if __name__ == "__main__":
    conn = psycopg2.connect(database="BOOK", user="postgres", password="wlc570Q0", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    ebook_address = input("请输入小说目录网址：\n")
    dl = downloader()
    dl.start(ebook_address)
    # print(dl.bookname)

    confirm = input("Do you want to download <%s>?(Y/N):" % dl.bookname)
    if not(confirm == "Y" or confirm == "y"):
        print("请求被中断")
        sys.exit()
    # --------POST--------
    headers = {'content-type': 'application/json'}
    json_data = json.dumps({
        "id":time.time(),
        "type":"add",
        "subtype":"book",
        "data":
            {"bookname":dl.bookname,"author":dl.author,"introduce":dl.introduce}
    })
    response = requests.post("https://www.lcworkroom.cn/book/api/%s"%MD5.md5("wlc570Q0",salt="BOOK"), data=json_data, headers=headers)
    try:
        data = json.loads(response.text)
    except Exception as e:
        print(response.text)
        logging.error(e)
        sys.exit()
    for key in ["status","message"]:
        if not key in data.keys():
            logging.error("response type error")
            print("response type error")
            sys.exit()
    if data["status"] == 0 or data["status"] == 1:
        data = data["data"]
        dl.bookid = data["bookid"]
        print("add this new book:%d"%dl.bookid)
    else:
        logging.error(data["message"])
        print(data["message"])
        sys.exit()
    # --------------------
    thread_len = input("请选择要使用的线程数:")
    if thread_len.isdecimal() == False:
        thread_len = 5
    else:
        thread_len = int(thread_len)
    print("正在获取目录...")
    dl.get_index()
    print("获取目录，总共 %d 章" % dl.num)
    print("《%s》开始下载..." % dl.bookname)
    threadName_List = ["Thread-%d" % (i+1) for i in range(thread_len)]
    print(threadName_List)
    #queueLock = threading.Lock()
    workQueue = queue.Queue(thread_len)
    thread_List = []
    threadID = 1
    for i in range(dl.num):
        address_List.append(dl.link_list[i]["link"])
        title_List.append(dl.link_list[i]["title"])

    # 创建新线程
    for tName in threadName_List:
        thread = MyThread(threadID, tName, workQueue)
        thread.start()
        thread_List.append(thread)
        threadID += 1

    # 填充队列
    #queueLock.acquire()
    for word in address_List:
        workQueue.put(word)
    #queueLock.release()

    # 等待队列清空
    while not workQueue.empty():
        pass

    # 通知线程退出
    exitFlag = 1

    # 等待所有线程完成
    for t in thread_List:
        t.join(30)

    # 处理错误信息
    if len(Error_list) != 0:
        print("尝试重新下载失败章节")
        count = 0
        for error in Error_list:
            num = 1
            while num <= 5:
                # print("正在第 %d 次重新获取章节 %s 的内容" %(num,error[1]))
                text = dl.get_text(error[2])
                if text != "Get Error":
                    count += 1
                    ebook_list.append((error[0],error[1],text))
                    sys.stdout.write("  已下载:%.3f%%" % float(count / len(Error_list) * 100) + '\r')
                    sys.stdout.flush()
                    post_chapter(dl.bookid, error[0], error[1], text)
                    break
                num += 1
            else:
                print("重新下载章节 %s 下载失败" % error[1])

    # 完成下载，拼接文本
    print("完成下载，正在拼接文本")
    ebook_list.sort(key=lambda x: x[0])

    for passage in ebook_list:
        bookid = dl.bookid
        chapterid = passage[0]
        title = passage[1]
        text = passage[2]
        #post_chapter(bookid,chapterid,title,text)
        dl.writer("%s.txt" % dl.bookname, "{|"+passage[1]+"|}", passage[2])
    print("《%s》下载完成" % dl.bookname)
    input("按回车键结束程序")