import json
import itertools
import urllib
import requests
import os
import re
import codecs

import sys

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#    "Accept-Encoding": "gzip, deflate",
#    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "image.baidu.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
}

img_types = ["bmp", "BMP", "jpg", "JPG", "png",
             "PNG", "jpeg", "JPEG", "tif", "TIF", "gif", "GIF"]


str_table = {
    '_z2C$q': ':',
    '_z&e3B': '.',
    'AzdH3F': '/'
}

char_table = {
    'w': 'a',
    'k': 'b',
    'v': 'c',
    '1': 'd',
    'j': 'e',
    'u': 'f',
    '2': 'g',
    'i': 'h',
    't': 'i',
    '3': 'j',
    'h': 'k',
    's': 'l',
    '4': 'm',
    'g': 'n',
    '5': 'o',
    'r': 'p',
    'q': 'q',
    '6': 'r',
    'f': 's',
    'p': 't',
    '7': 'u',
    'e': 'v',
    'o': 'w',
    '8': '1',
    'd': '2',
    'n': '3',
    '9': '4',
    'c': '5',
    'm': '6',
    '0': '7',
    'b': '8',
    'l': '9',
    'a': '0'
}
char_table = {ord(key): ord(value) for key, value in char_table.items()}


def decode(url):
    for key, value in str_table.items():
        url = url.replace(key, value)
    return url.translate(char_table)


re_url = re.compile(r'"objURL":"(.*?)"')


def GetImgUrls(html):
    imgUrls = [decode(x) for x in re_url.findall(html)]
    return imgUrls


def DownloadImg(imgUrl, save_path, imgName):
    try:
        res = requests.get(imgUrl, timeout=15)
        if str(res.status_code)[0] == "4":
            print(str(res.status_code), ":", imgUrl)
            return False
    except Exception as e:
        print("抛出异常 ", imgUrl)
        print(e)
        return False
    try:
        index = imgUrl.rfind(".")
        img_raw_type = imgUrl[index + 1:]
        suf = None
        for img_type in img_types:
            if img_raw_type.startswith(img_type):
                suf = "." + img_type
                break
        imgName = os.path.join(save_path, imgName + suf)
        if not suf:
            return False
    except Exception as e:
        print("抛出异常 ", imgUrl)
        print(e)
        return False
    print(imgName)
    with open(imgName, "wb") as f:
        f.write(res.content)
    return True


def GenerateUrls(keyword):
    url = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
    urls = (url.format(word=keyword, pn=x)
            for x in itertools.count(start=0, step=60))
    return urls


if __name__ == '__main__':
    keywords = ["铅笔画"]
    numbers = [5000]
    print("百度图片爬取开始")
    for keyword, number in zip(keywords, numbers):
        print("\n\n开始爬取关键字为 \"{}\" 的图片，数量为 {} 张\n\n".format(keyword, number))
        save_path = os.path.join(os.getcwd(), keyword)
        print("保存路径为 {}\n".format(save_path))
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        urls = GenerateUrls(keyword)
        cnt = 0
        for url in urls:
            print("正在请求 ", url)
            html = requests.get(
                url, timeout=10, headers=headers).text
            imgUrls = GetImgUrls(html)
            if len(imgUrls) == 0:  # 没有图片则结束
                break
            for imgUrl in imgUrls:
                if DownloadImg(imgUrl, save_path, keyword + str(cnt)):
                    cnt += 1
                    print("已下载 %s 张" % cnt)
                if cnt >= number:
                    break
            if cnt >= number:
                break
