import os

import pandas as pd
import requests


def download_img(img_url,img_name, place_id):
    r = requests.get(img_url,stream=True)
    if r.status_code == 200:
        imgname = img_name + '.jpg'
        dirpath = os.path.join(r'E:\2-Codes\Project\bishe\data\weibopic', place_id)
        if os.path.exists(dirpath):
            pass
        else:
            os.mkdir(dirpath)
            
        imgpath = os.path.join(dirpath, imgname)
        open(imgpath, 'wb').write(r.content) 
        print(imgname+'   done!!!')
        del r
    else:
        print(img_url+'  出错啦！！')


if __name__ == '__main__':
    # 读取文件
    image_url=pd.read_csv(r'E:\2-Codes\Project\bishe\data\Result_1.csv')
    
    # 文件行数太多，可限制行数先测试看看
    # image_url_a=image_url.iloc[:10, :]

    # 遍历image_url
    for index,row in image_url.iterrows():
        download_img(row['img_large'], row['picid'], row['place'])
