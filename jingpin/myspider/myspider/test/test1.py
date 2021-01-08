# -*- coding: utf-8 -*-
import random
import json
import subprocess

from myspider.utils import safe_json_loads, get_data
from myspider.items import TagItem
from scrapy import Request
from datetime import datetime
import re, os
import requests
from lxml import etree
import time
import redis

# url = 'https://m.koolearn.com/product/c_19_82460.html'
# headers = {
#             'Host': 'm.koolearn.com',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv; Koolearn; kooup/4.13.2; B/160/30000504) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045410 Mobile Safari/537.36',
#             'Sec-Fetch-Mode': 'navigate',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#             'X-Requested-With': 'com.kooup.student',
#             'Sec-Fetch-Site': 'same-site',
#             'Referer': 'https://cet4.koolearn.com/zhuanti/cet_wap/?scene=appjgq',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
#             }

# res = requests.get(url, headers=headers)
# print(res.text)
a = """
<div class="summary">
                    <h2 class="title">大学英语四级寒假全程班【适用2021年06月考试】<a href="//item.koolearn.com/product/productProtocol/86413" class="link"> 查看协议</a></h2>
                    <p class="describer"></p>
                    <p class="money">
                            <span class="price">¥ <span class="jg-control-price">179.10</span></span>
                                <span class="origin">价格：¥<span class="jg-control-price">199</span></span>
                    </p>
					<div id="jp-summer-happy"></div>
                </div>
"""

b = """
<p class="money">
                        <span class="sign">¥</span>
                        <span class="price jg-control-price">1290</span>
                            <span class="price-add-surprise jg-control-price">1290</span>

                </p>
"""

c = """
<div class="status">
                       <span class="stock">
                            <span>已报人数：</span>
                            <span style="color:#ff5d50;">182 人</span>&nbsp;&nbsp;&nbsp;
                            <span>限报人数：</span>
                            <span style="color:#ff5d50;">5000 人</span>&nbsp;&nbsp;&nbsp;
                   </span></div>
"""
# response = etree.HTML(c)
# print(response.xpath('//span[@class="stock"]/span[2]/text()'))
# price_list = response.xpath('//*[@class="money"]//text()')
# for temp in price_list:
#     if not temp.strip() or '¥' in temp:
#         continue
#     original_price = temp
#     print(original_price)
#     break
# for temp in price_list[::-1]:
#     if not temp.strip() or '¥' in temp:
#         continue
#     original_price = temp
#     print(original_price)
#     break

# url = '//www.koolearn.com/product/c_92_84303.html'
# result = re.search('\/\/www\.koolearn\.com\/guonei\/product\/c_[0-9]_(.*).html', url)
# if result:
#     print(result.group(1))

# headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9',
#             'Connection': 'keep-alive',
#             'Host': 'www.koolearn.com',
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': 'same-origin',
#             'Sec-Fetch-Dest': 'document',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
#         }
# # url = 'https://gnitem.koolearn.com/api/productDetail/common-by-productid?productId=74447&isPreView=1&pageType=2'
# url = 'https://gnitem.koolearn.com/api/productDetail/common-by-productid?productId=26836&isPreView=1&pageType=2'
# res = requests.get(url)
# print(res.text)

# from selenium import webdriver
# driver = webdriver.Chrome()
# driver.get('https://cet4.koolearn.com/zhuanti/cet/')
# type = driver.find_element_by_xpath('//a[@class="i_name fl"]').text
# print(type)
# for i in range(1, 10):
# res = requests.get(f'https://m.koolearn.com/product/c_{i}_81075.html', headers=headers)
# if '页面飞走了' in res.text:
#     continue
# else:
#     print(res.text, i)
#     break

# url = 'https://m.koolearn.com/product/c_19_84124.html'
# html = requests.get(url, headers=headers)
# response = etree.HTML(html.text)
# sell = response.xpath('//div[@class="status"]/span//text()')
# print(sell)

# import datetime
# import time
# # timeStamp = 1557502800
# # dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
# # print(type(dateArray))
#
# timeStamp = 1557502800
# dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
# threeDayAgo = dateArray - datetime.timedelta(days=3)
# print(threeDayAgo)

# url = 'https://ke.youdao.com/'
# headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9',
#             'Connection': 'keep-alive',
#             'Host': 'ke.youdao.com',
#             'If-None-Match': 'W/"4b20f-ReG06qvjMmppSfwnGzdmKXJdf9E"',
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': None,
#             'Sec-Fetch-Dest': 'document',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
#         }
# res = requests.get('https://ke.youdao.com', headers=headers)
# response = etree.HTML(res.text)
# # print(res.text)
# url_list = response.xpath('//*[contains(text(), "热门课程")]/following-sibling::div[1]/a/@href')
# print(url_list)
# for url in url_list:
#     result = re.search('https:\/\/ke\.youdao\.com\/course\/detail\/([0-9]*)\?.*', url)
#     if result:
#         print(result.group(1))

# url = 'https://gnitem.koolearn.com/api/product/search-product'
# data = {
#     'basicCourseType': [1],
#     'displayName': "",
#     'examSeasonIds': [78, 163],
#     # 'orderBy': "firstOnlineTime",
#     'orderBy': "buyNumber",
#     'pageNo': 1,
#     'pageSize': 15,
#     'squadtypeId': [],
#     'subjectInfoId': [1008, 1009, 1010, 1012],
# }
# headers = {
#             'Accept': 'application/json, text/javascript, */*; q=0.01',
#             'Content-Type': 'application/json',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9',
#             'Connection': 'keep-alive',
#             'Host': 'gnitem.koolearn.com',
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': 'same-origin',
#             'Sec-Fetch-Dest': 'document',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
#         }
# res = requests.post(url, json=data, headers=headers)
# print(res.text)

# url = 'http://study.koolearn.com/api/product/\?productIds\=82966 --referer http://www.koolearn.com/'
# url = 'http://study.koolearn.com/api/product/?productIds=82966'
# headers = {
#         'Host': 'study.koolearn.com',
#         'User-Agent': 'curl/7.71.1',
#         'Accept': '*/*',
#         'Referer': 'http://www.koolearn.com/',
#         'Content-Type': 'application/json;charset=UTF-8',
#         'Connection': 'keep-alive',
#         'Vary': 'Accept-Encoding',
#         'X-Cache': 'bypass'
#         }
# res = requests.get(url, headers=headers)
# print(res.text)

# url = 'https://cet4.koolearn.com/zhuanti/cet/'
# headers = {
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept-Language': 'zh-CN,zh;q=0.9',
#         'Connection': 'keep-alive',
#         'Host': 'cet4.koolearn.com',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': None,
#         'Sec-Fetch-Dest': 'document',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
#     }
# res = requests.get(url, headers=headers)
#
# result = re.search('data: \[\{.*\}\);', res.content.decode())
# print('{"data"' + result.group()[4:-2])

# url = 'http://search.neea.edu.cn/Imgs.do?act=verify&t=0.9959927743878891'
# headers = {
#     'Referer': 'http://search.neea.edu.cn/QueryMarkUpAction.do?act=doQueryCond&pram=results&community=Home&sid=2nasVMoohJ6cFnsQEIjGYmh'
# }
# print(requests.get(url, headers=headers).content)
# with open('aaa.jpeg', 'wb') as f:
#     f.write(requests.get(url, headers=headers).content)
# print(requests.get('https://ke.youdao.com/course3/api/vertical2?tag=1792&rank=1585377386').text)
# res1 = requests.get('https://ke.youdao.com/course3/api/vertical2?tag=2248')


# def aaa(res=res1):
#     dict_data = safe_json_loads(res.text)
#     if not dict_data['data']['courses']:
#         return
#     rank = dict_data['data']['courses'][-1]['rank']
#     print(rank)
#     url = res.request.url + f'&rank={rank}'
#     response = requests.get(url)
#     print(response.text)
#     # time.sleep(5)
#     return aaa(response)
#
#
# print(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.dirname(__file__))
# print(os.getcwd())
# print(os.path.dirname(os.path.dirname(__file__)))

# headers = {
#             'Host': 'study.koolearn.com',
#             'User-Agent': 'curl/7.71.1',
#             'Accept': '*/*',
#             'Referer': 'https://ke.youdao.com/',
#             'Content-Type': 'application/json;charset=UTF-8',
#             'Connection': 'keep-alive',
#             'Vary': 'Accept-Encoding',
#             'X-Cache': 'bypass'
#         }
# for i in range(90000):
# res = requests.get(f'http://study.koolearn.com/api/product/?productIds=26836', headers=headers)
headers = {
    'Content-Type': 'text/plain;charset=UTF-8',
    'Transfer-Encoding': 'chunked',
    'Connection': 'keep-alive',
    'Vary': 'Accept-Encoding',
    # 'Set-Cookie': 'keoutvendor=""; Expires=Sat, 19-Nov-2050 10:24:22 GMT; Path=/',
    # 'Set-Cookie': 'ke_inLoc=""; Expires=Sat, 19-Nov-2050 10:24:22 GMT; Path=/',
    # 'Set-Cookie': 'ke_ccId=""; Expires=Sat, 19-Nov-2050 10:24:22 GMT; Path=/',
    # 'Set-Cookie': 'OUTFOX_SEARCH_USER_ID=1458013385@10.108.160.127; Domain=youdao.com; Expires=Sat, 19-Nov-2050 10:24:22 GMT; Path=/',
}
# res = requests.get(f'https://ke.youdao.com/course/api/detail.json?courseId=76687',)
# print(res.text)

# url = 'https://www.koolearn.com/'
# headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Accept-Language': 'zh-CN,zh;q=0.9',
#             'Connection': 'keep-alive',
#             'Host': 'www.koolearn.com',
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': 'same-origin',
#             'Sec-Fetch-Dest': 'document',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
#         }
# res = requests.get(url, headers=headers)
# print(res.text)

# connection = redis.Redis('localhost', port=6379, db=1)
# id_list = connection.smembers('course_id')
# print('75720'.encode() in id_list)

# temp={"course_id": 12393, "url": "https://ke.youdao.com/course/detail/12393", "title": None, "start_time": "2020-11-27 14:00", "end_time": "2019-06-09 23:59", "sell": "200", "original_price": "5489", "current_price": "5489", "teacher": ["\u5218\u6770", ""], "student": None, "course_hour": "146", "course_format": None, "course_service": None, "course_info": None, "com": "youdao", "create_time": "2020-11-27 12:10:28"}
# start_time = temp['start_time']
# print(start_time)
# a = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M")))
# b = int(time.time())
# print(a)
# print(b)

# with open('youdao_course.json', 'r') as f:
#     with open('youdao_course1.json', 'a') as g:
#         a = f.readlines()
#         for i in a:
#             end_time = json.loads(i)['end_time']
#             try:
#                 a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))
#             except:
#                 try:
#                     a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M")))
#                 except:
#                     pass
#             b = int(time.time())
#             if a >= b:
#                 g.write(i)


with open('../koolearn_course.json', 'r') as f:
    aaa = f.readlines()
conn = redis.Redis('localhost', port=6379, db=1)
for i in aaa:
    id = json.loads(i)['course_id']
    conn.lpush('koolearn:urls', f'http://study.koolearn.com/api/product/?productIds={id}')
    print(id)

# for i in range(10):
#     subprocess.run(['scrapy', 'runspider', 'spiders/koolearn/koolearn_sell.py'])

