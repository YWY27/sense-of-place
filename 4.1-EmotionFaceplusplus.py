import json
import os
import re
import sqlite3
import time
from tkinter import EXCEPTION
import urllib.error
import urllib.request

import cv2


def facedetect_api(imgpath, key, secret):
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)
    fr = open(imgpath, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(fr.read())
    fr.close()
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append("gender,age,emotion")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = json.load(resp)
        # print(qrcont)
    except urllib.error.HTTPError as e:
        print(e.read().decode('utf-8'))
        
    return qrcont

def writeface(imgpath, qrcont):
    faces_id = re.findall('([-0-9A-Za-z]+)\.jpg', imgpath)[0]
    pid = re.findall('[0-9A-Z]{10,}', imgpath)[0]

    if qrcont['faces']:
        for face in qrcont['faces']:
            token = face['face_token']
            gender = face['attributes']['gender']['value']
            age = face['attributes']['age']['value']
            emotions = face['attributes']['emotion']
            happiness = emotions['happiness']
            neutral = emotions['neutral']
            sadness = emotions['sadness']
            surprise = emotions['surprise']
            disgust = emotions['disgust']
            anger = emotions['anger']
            fear = emotions['fear']
            emotion = max(emotions, key = emotions.get)
            ins = ("INSERT INTO emotionpro VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
            %(token, faces_id, pid, gender, age, happiness, neutral, sadness, surprise, disgust, anger, fear, emotion))
            cur.execute(ins)
            conn.commit()
            # print(imgpath+'   done!!!')
    else:
        # print(imgpath+' 没有人脸呐！！')
        pass


def get_imgsize(imgpath):
    img = cv2.imread(imgpath)  
    w, h = img.shape[0:2]
    image = open(imgpath, 'rb').read()
    size = len(image)/1e6
    return w, h, size

def emotiontable():
    create_picfacetable='''CREATE TABLE IF NOT EXISTS emotionpro(face_token TEXT,
                                    faces_id TEXT,
                                    pid TEXT, 
                                    gender TEXT, 
                                    age INTEGER, 
                                    happiness FLOAT, 
                                    neutral FLOAT, 
                                    sadness FLOAT, 
                                    surprise FLOAT, 
                                    disgust FLOAT, 
                                    anger FLOAT, 
                                    fear FLOAT, 
                                    emotion TEXT, 
                                    PRIMARY KEY (face_token, faces_id))'''
    cur.execute(create_picfacetable)
    conn.commit()

def img_process(filepath):

    key = "u9X98Xa3t4vwMh2m-S_VUXH_gTMTw-Dy"
    secret = "dcaUu4bovBU7nWFU2v-YnW9hv9Wt_HkW"

    # key = "KlTfZ4g0flqByH01KxHyZRkpePJ27N-_"
    # secret = "p-CarOtU5nhhoYXAdwSfd73P-UZIlg1k"

    count = 1

    for imgname in os.listdir(filepath):

        imgpath = filepath + '\\' + imgname
        w,h, size = get_imgsize(imgpath)

        try:
            if w<48 or h<48 or w>4096 or h>4096 or size>2:
                # print(imgpath+'   invalid image size!!!')
                pass
            else:
                try:
                    qrcont = facedetect_api(imgpath, key, secret)
                    writeface(imgpath, qrcont)
                except:
                    # print('可能超过并发数了，等一下！！！')
                    time.sleep(5)
                    qrcont = facedetect_api(imgpath, key, secret)
                    writeface(imgpath, qrcont)
        except Exception as e:
            print(e)
            print(imgname+'  出错啦!!!')
            continue

        if count % 100 == 0:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'正在处理第{0}张图片'.format(count))
        count = count + 1

if __name__ == '__main__':

    conn = sqlite3.connect('weibo.sqlite',check_same_thread=False)
    cur = conn.cursor()

    emotiontable()

    path = r'E:\2-Codes\Project\bishe\data\face'

    for folder in os.listdir(path):
        filepath = path+'\\'+folder

        print('正在处理---  '+filepath)
        try:
            img_process(filepath)
            print('处理完成---   '+filepath)
            time.sleep(30)
        except:
            print(filepath+'  出错啦!!!')
            break
    
    cur.close()
    conn.close()
