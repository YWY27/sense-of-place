import json
import random
import re
import sqlite3
import time

import pandas as pd
import requests
from fake_useragent import FakeUserAgent

from buildip import build_ippool


def get_tweets(URL, page, ippool):

    proxy_ip = random.choice(ippool)
    ua = FakeUserAgent()

    headers={'User-Agent': ua.random}
    res = requests.get(URL, proxies=proxy_ip, headers=headers)
    print('状态码为：',str(res.status_code))
    print('请求头为： ',headers['User-Agent'])
    print('代理为： ',proxy_ip['http'])
    print('url: ',URL)

    ok=''
    if res.status_code == 200:    
        # 将获取到的文件转为json
        info = json.loads(res.text)
        ok = info['ok']
        if ok == 1:
            pass
        else:
            print('这里还没有内容')
            return 0
        cards = info['data']['cards']

        cardsLength = len(cards)
        card_group = {}

        print('---第', page, '页---')
        # page=1时从下标2开始，page>=2时下标从0开始，坑：有的地点第一页的cards长度只有1
        if page == 1 and cardsLength == 2:
            card_group = cards[1]['card_group']
        else: 
            card_group = cards[0]['card_group']
        return card_group

    else:
        print('------------出错啦！！--------------')
        print(res.status_code)
        return 1


def write_tweets(card_group, pname):
    for tweet in card_group:
        if 'mblog' in tweet and tweet['mblog']['user']:
            mblog = tweet['mblog']

            temp = [0 for i in range(10)]
            temp[0] = mblog['id']

            # 不记录重复的微博
            temp_pd = pd.read_sql_query("SELECT weibo_id FROM weibo",conn)
            all_id = temp_pd['weibo_id'].values

            if temp[0] in all_id:
                print('这条微博爬过啦，跳过！')
                continue

            temp[1] = mblog['created_at']
            temp[2] = mblog['user']['id']
            temp[3] = mblog['user']['gender']

            temp[4] = mblog['source']
            temp[4]=temp[4].replace("'","")
            temp[4]=temp[4].replace('"','')

            text = re.sub('(武汉·.*?)</span>', '', mblog['text'])
            text = re.sub('<[^>]*?>', '',text)
            temp[5] = re.sub('[\s\'\"]', '', text)
            print(temp[5])
            
            temp[6] = mblog['reposts_count']
            temp[7] = mblog['comments_count']
            temp[8] = mblog['attitudes_count']
            temp[9] = pname

            print('---正在写入一条微博---')
            ins="INSERT INTO weibo VALUES (null,"+",".join(["'%s'" %x for x in temp])+");"

            cur.execute(ins)
            conn.commit()

            # 如果存在图片的话，就更新图片表和联立表
            if 'pics' in mblog.keys():
                for img in mblog['pics']:
                    # 向图片和微博联立表中插入数据
                    ins="INSERT INTO picweibo(picid, weibo_id) VALUES ('%s', '%s')"%(img['pid'], mblog['id'])
                    cur.execute(ins)
                    conn.commit()

                    # 整理图片表的数据
                    temp_pic = [0 for i in range(3)]  # 初始化一行，一共有4列

                    temp_pic[0] = img['pid']
                    temp_pic[1] = img['url']
                    temp_pic[2] = img['large']['url']

                    # 向图片表中插入数据
                    ins="INSERT INTO pic VALUES (null,"+",".join(["'%s'" %x for x in temp_pic])+")"
                    cur.execute(ins)
                    conn.commit()
        else:
            print('这条微博有问题，跳过！')


def weibotable():
    #cur.execute("DROP TABLE IF EXISTS weibo")
    create_weibotable='''CREATE TABLE IF NOT EXISTS weibo(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    weibo_id TEXT UNIQUE,
                                    created_time TEXT,
                                    user_id TEXT,
                                    gender TEXT, 
                                    source TEXT,
                                    content TEXT,
                                    reposts_count INTEGER,
                                    comments_count INTEGER,
                                    attitudes_count INTEGER,
                                    pname TEXT)'''
    cur.execute(create_weibotable)
    conn.commit()


def pictable():
    #cur.execute("DROP TABLE IF EXISTS pic")
    create_pictable='''CREATE TABLE IF NOT EXISTS pic(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    picid TEXT NOT NULL,
                                    img TEXT,
                                    img_large TEXT)'''
    cur.execute(create_pictable)
    conn.commit()


def picweibotable():
    #cur.execute("DROP TABLE IF EXISTS picweibo")
    create_picweibotable='''CREATE TABLE IF NOT EXISTS picweibo(picid TEXT,
                                    weibo_id TEXT,
                                    PRIMARY KEY (picid, weibo_id))'''
    cur.execute(create_picweibotable)
    conn.commit()


def db_init():
    weibotable()
    pictable()
    picweibotable()

def main():
    global conn, cur

    conn = sqlite3.connect('weibo.sqlite',check_same_thread=False)
    cur = conn.cursor()

    f = pd.read_csv(r'data\pid1.csv') 

    # 初始化数据库
    db_init()

    ippool = build_ippool()


    for pname,pid in zip(f['pname'], f['pid']):
        print('------开始爬'+pname+'的微博-----')
        page = 1
        while True:
            url = 'https://m.weibo.cn/api/container/getIndex?containerid='+pid+'&luicode=10000011&lfid='+pid+'&page=%d'%(page)
            tweets = get_tweets(url, page, ippool)

            if tweets == 0:
                print('已经到第',page,'页了，没有内容了')
                break
            elif tweets == 1:
                print('------------出错啦！！--------------')
                time.sleep(10)
                continue

            write_tweets(tweets, pname)
            print('第', page, '页爬完了！')
            page = page + 1

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
