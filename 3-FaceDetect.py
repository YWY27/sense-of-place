import os
import re
import sqlite3
import uuid
import gc
import time

import cv2


def face_detect(filepath, outfilepath):

    face_detector = cv2.CascadeClassifier(r'model\haarcascade_frontalface_alt.xml')

    # 遍历该目录下的所有图片文件
    for imgname in os.listdir(filepath):
        imgpath = filepath + '\\' + imgname
        picid = re.findall('([0-9A-Za-z]+)\.jpg', imgpath)[0]

        try:
            # 读取图片
            img = cv2.imread(imgpath)
            # haar 灰度转化
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            # 人脸检测
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(5,5), flags=cv2.CASCADE_SCALE_IMAGE)
            
            if len(faces) > 0:
                for face in faces:
                    (fX, fY, fW, fH) = face
                    (row, col, dim) = img.shape
                    # 人脸裁剪
                    start_row, end_row = max(0, int(fY-fH*0.25)), min(row, int(fY+fH*1.25))
                    start_col, end_col = max(0, int(fX-fW*0.25)), min(col, int(fX+fW*1.25))
                    face_img = img[start_row:end_row, start_col:end_col]
                    faceid = str(uuid.uuid1())
                    cv2.imwrite(outfilepath+'/'+faceid+'.jpg', face_img)

                    ins="INSERT INTO picface(faces_id, picid) VALUES ('%s', '%s')"%(faceid, picid)
                    cur.execute(ins)
                    conn.commit()
            os.remove(imgpath)
            print(imgname+'    done!!!')
            del img, gray, faces
            gc.collect()
            
        except Exception as e:
            print(e)
            continue

def picfacetable():
    create_picfacetable='''CREATE TABLE IF NOT EXISTS picface(faces_id TEXT,
                                    picid TEXT,
                                    PRIMARY KEY (faces_id, picid))'''
    cur.execute(create_picfacetable)
    conn.commit()

if __name__ == '__main__':

    conn = sqlite3.connect('weibo.sqlite',check_same_thread=False)
    cur = conn.cursor()

    picfacetable()

    path = r'E:\2-Codes\Project\bishe\data\demo' 
    outpath = r'E:\2-Codes\Project\bishe\data\face'
    for folder in os.listdir(path):
        filepath = path+'\\'+folder
        outfilepath = outpath+'\\'+folder

        if os.path.exists(outfilepath):
            pass
        else:
            os.mkdir(outfilepath)

        print('正在处理---  '+filepath)
        try:
            face_detect(filepath, outfilepath)
            print('处理完成---   '+filepath)
            time.sleep(180)
        except:
            print(filepath+'  出错啦!!!') 
            continue
    
    cur.close()
    conn.close()
