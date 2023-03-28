import requests as rq
import json
import re
from bs4 import BeautifulSoup
import os
from tqdm import tqdm

host = 'http://agora.ex.nii.ac.jp'

def get_one_page(url,path):

    resp = rq.get(url)
    resp.encoding='utf-8'
    text = resp.text
    srcs = re.findall(r'src="(.*.jpg)',text)

    for i,tmp in enumerate(srcs[:-1]):
        pic_url = host + tmp
        resp = rq.get(pic_url)
        name = re.findall(r'/(.*)/\w+x\w+/',tmp)[0].split('/')[-1]
        # print(i)
        with open(f'{path}/{name}.png','wb') as fp:
            fp.write(resp.content)
    return
def get_one_ty(url,path):
    resp = rq.get(url)
    resp.encoding='utf-8'
    text = resp.text
    detail_url = host + re.findall(r'<a href="(.*)">詳細経路情報</a>',text)[0]

    resp = rq.get(detail_url)
    resp.encoding='utf-8'
    text = resp.text
    soup = BeautifulSoup(text,'html.parser')
    a = soup.find('table',class_='TRACKINFO')
    ls = a.findAll('tr')[1:]
    for i,item in enumerate(tqdm(ls)):

        pic_url = host + item.find_all('td')[9].find('a').get('href')
        infos = [a.text for a in item.find_all('td')]
        year = infos[0]
        month = infos[1]
        day = infos[2]
        time = infos[3]
        lat = infos[4]
        lon = infos[5]
        p = infos[6]
        speed = infos[7]

        name = path + f'{i}'
        dic = {
        'time' : f'{year}-{month}-{day}-{time}',
        'lontitude' : lon,
        'latitude' : lat,
        'pressure' : p,
        'speed' : speed,
        }
        if not os.path.exists(name):
            os.mkdir(name)
        with open(name+'/info.json','w') as fp:
            json.dump(dic,fp)
        get_one_page(pic_url,name)
    return

def get_one_year(url):
    #language must!!!! be in japanese!!!
    year = re.findall(r'/([0-9]*).html',url)[0]
    dir_name = f'./{year}'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    resp = rq.get(url)
    resp.encoding = 'utf-8'
    text = resp.text
    soup = BeautifulSoup(text,'html.parser')
    a = soup.find('table',class_='TABLELIST')
    ls = a.find_all('tr')[1:]
    for item in ls:
        index = item.find_all('td')[1].text
        ty_url = host + item.find_all('td')[1].find('a').get('href')

        dir_name = f'./{year}/{index}/'
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        print(f'Crawling {index} in {year}...')
        get_one_ty(ty_url,dir_name)
        print('Done.')
    return

if __name__ == '__main__':
    year = input('输入要爬取的年份:')
    #默认爬取西北太平洋，要爬取西南太平洋将下面的参数改成url2
    url = f'http://agora.ex.nii.ac.jp/digital-typhoon/year/wnp/{year}.html.ja'
    url2 = f'http://agora.ex.nii.ac.jp/digital-typhoon/year/wsp/{year}.html.ja'
    get_one_year(url)