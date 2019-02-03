# -*- coding:GBK -*-
from bs4 import BeautifulSoup
import requests
import sys

class downloader(object):
    def __init__(self):
        self.link_list = []
        self.num = 0  # �½���
        self.content = ""

    def start(self,content):
        self.content = content

    def get_index(self):
        req = requests.get(url = self.content)
        req.encoding = "gbk"
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        indexs = str(bf.find_all('div', id = 'list')[0])
        indexs = indexs.partition("<dt>��ȫְ��ʦ������</dt>")[2]
        indexs = indexs.partition("</dl>")[0]
        bf = BeautifulSoup(indexs, "html.parser")
        indexs = bf.find_all("a")

        for index in indexs:
            # content,a,title = title.partition(" ")
            # content = content.partition("��")[2].partition("��")[0]
            # # print("��%s�� %s" % (index,title))
            link_dict = {"title":index.string,"link":self.content+index.get("href")}
            self.link_list.append(link_dict)
        self.num = len(self.link_list)
        # print(indexs)

    def get_text(self,target):
        # target = 'https://www.booktxt.net/0_595/128833.html'
        req = requests.get(url = target)
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


if __name__ == "__main__":
    confirm = input("Do you want to download <ȫְ��ʦ>?(Y/N)")
    if not(confirm == "Y" or confirm == "y"):
        print("�����ж�")
        sys.exit()

    dl = downloader()
    dl.start("https://www.booktxt.net/0_595/")
    print("���ڻ�ȡĿ¼...")
    dl.get_index()
    print("��ȡĿ¼���ܹ� %d ��" % dl.num)
    print("��ȫְ��ʦ����ʼ����...")
    for i in range(dl.num):
        text = dl.get_text(dl.link_list[i]["link"])
        # print(text)
        dl.writer("ȫְ��ʦ.txt",dl.link_list[i]["title"],text)
        # print(dl.link_list[i]["title"]+"�������")
        sys.stdout.write("  ������:%.3f%%" % float(i / dl.num * 100) + '\r')
        sys.stdout.flush()
    print("��ȫְ��ʦ���������")