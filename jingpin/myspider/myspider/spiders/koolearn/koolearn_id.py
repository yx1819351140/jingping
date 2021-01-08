# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import json
import time
from myspider.utils import safe_json_loads, get_end_time, dingding_alert, get_data
from myspider.settings import TAGS, REDIS_URI_, REDIS_PASSWORD_, handler
import redis
from scrapy import Request
from datetime import datetime

logger = logging.getLogger(__name__)


class KoolearnIdSpider(scrapy.Spider):
    name = 'koolearn_id'
    logger.addHandler(handler)
    allowed_domains = ['koolearn.com']

    def __init__(self):
        self.connection = redis.Redis(host=REDIS_URI_, port=6379, password=REDIS_PASSWORD_)
        super().__init__()

    def start_requests(self):
        self.course_id_set = self.connection.smembers('koolearn_course_id')
        if self.course_id_set:
            for course_id in self.course_id_set:
                yield Request(url=f'https://gnitem.koolearn.com/api/productDetail/common-by-productid?productId={course_id.decode()}&isPreView=1&pageType=2', meta={'product_id': course_id}, callback=self.del_id)
        for tag in TAGS:
            if tag == '考研':
                subject_dict = {
                    '英语': ['1008', '1009', '1010', '1011', '1012'],
                    '政治': ['1007', '1011', '1012'],
                    '数学': ['1006', '1010', '1012'],
                    '专业课': {
                        '经济类联考': ['1023'],
                        '电子信息': ['1024'],
                        '二外日语': ['1025'],
                        '法律硕士（法学）': ['1026'],
                        '法律硕士（非法学）': ['1027'],
                        '翻译硕士': ['1028'],
                        '公共日语': ['1029'],
                        '管理学': ['1030'],
                        '汉硕': ['1031'],
                        '计算机': ['1032'],
                        '教育硕士': ['1033'],
                        '教育学': ['1034'],
                        '金融': ['1035'],
                        '经济学': ['1036'],
                        '历史学': ['1037'],
                        '数学': ['1038'],
                        '西医学硕': ['1039'],
                        '西医在职': ['1040'],
                        '西医专硕': ['1041'],
                        '心理学': ['1042'],
                        '艺术': ['1043'],
                        '应用心理': ['1044'],
                        '中医': ['1045'],
                    },
                    '管综': {
                        'MBA': ['1013', '1014', '1022'],
                        'MPA': ['1014', '1015', '1022'],
                        '会计': ['1016', '1018', '1019', '1022'],
                        '审计': ['1017', '1018', '1019', '1022'],
                        '旅游': ['1014', '1020', '1022'],
                        '工程': ['1014', '1021', '1022'],
                    }
                }
                # subject_dict = {'政治': ['1007', '1011', '1012']}
                season_dict = {
                    '2021': ['78', '107'],
                    '2022': ['78', '163']
                }
                type_dict = {
                    '大咖全程班': [['2', '3', '4', '5', '6', '7', '10'], ['10']],
                    '直通车大咖版': [['2', '3', '4', '5', '6', '7', '10'], ['2', '3', '7']],
                    '无忧计划': [['2', '3', '4', '5', '6', '7', '10'], []],
                    '免费课': [['1'], []],
                }
                url = 'https://gnitem.koolearn.com/api/product/search-product'
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Content-Type': 'application/json',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'gnitem.koolearn.com',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                }
                for subject in subject_dict.keys():
                    for season in season_dict.keys():
                        for class_type in type_dict.keys():
                            if isinstance(subject_dict[subject], list):
                                data = get_data(type_dict[class_type][0], season_dict[season], type_dict[class_type][1],
                                                subject_dict[subject])
                                yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data}, callback=self.parse1)
                            else:
                                for sub_subject in subject_dict[subject].keys():
                                    data = get_data(type_dict[class_type][0], season_dict[season],
                                                    type_dict[class_type][1], subject_dict[subject][sub_subject])
                                    yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data}, callback=self.parse1)
            elif tag == '四六级':
                url = 'https://cet4.koolearn.com/zhuanti/cet/'
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'cet4.koolearn.com',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': None,
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                }
                yield Request(url, headers=headers, callback=self.parse2)

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['data']
            for product in product_list:
                course_id = str(product.get('productId', ''))
                if course_id.encode() not in self.course_id_set:
                    self.connection.sadd('koolearn_course_id', course_id)
                logger.info(f'[koolearn_id]考研id获取成功, course_id:{course_id}')
            current_page = int(dict_data['pageNum'])
            total_page = int(dict_data['pages'])
            if current_page < total_page:
                data = response.meta['data']
                data['pageNo'] = str(current_page + 1)
                url = 'https://gnitem.koolearn.com/api/product/search-product'
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Content-Type': 'application/json',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'gnitem.koolearn.com',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                }
                try:
                    yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data}, callback=self.parse1)
                except:
                    yield Request(url, method='POST', headers=headers, body=json.dumps(data),  meta={'data': data}, callback=self.parse1)
        except Exception as e:
            text = f'[koolearn_id]考研id获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_id]考研id获取失败, err_msg:{e}, res:{response.text}')

    def parse2(self, response):
        result = re.search('data: \[\{.*\}\);', response.text)
        try:
            if result:
                dict_data = safe_json_loads('{"data"' + result.group()[4:-2])
                for data in dict_data['data']:
                    if data['parent'] == 1819:
                        for course in data['content']:
                            course_id = str(course['p_id'])
                            if course_id.encode() not in self.course_id_set:
                                self.connection.sadd('koolearn_course_id', course_id)
                            logger.info(f'[koolearn_id]四六级id获取成功, course_id:{course["p_id"]}')
            else:
                text = f'[koolearn_id]四六级id获取失败, err_msg:获取页面内json数据失败\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[koolearn_id]四六级id获取失败, res:{response.text}')
        except Exception as e:
            text = f'[koolearn_id]四六级id获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_id]四六级id获取失败, err_msg:{e}, res:{response.text}')

    def del_id(self, response):
        data = safe_json_loads(response.text)
        code = data['code']
        if code == 0:
            self.del_id1(response.meta['product_id'], data)
        elif code == 10005:
            for i in [2, 19, 20]:
                url = f'https://m.koolearn.com/product/c_{i}_{response.meta["product_id"].decode()}.html'
                headers = {
                    'Host': 'm.koolearn.com',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv; Koolearn; kooup/4.13.2; B/160/30000504) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045410 Mobile Safari/537.36',
                    'Sec-Fetch-Mode': 'navigate',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'X-Requested-With': 'com.kooup.student',
                    'Sec-Fetch-Site': 'same-site',
                    'Referer': 'https://cet4.koolearn.com/zhuanti/cet_wap/?scene=appjgq',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                yield Request(url=url, headers=headers, meta={'course_id': response.meta["product_id"], 'i': i},
                              callback=self.del_id2)

    def del_id1(self, course_id, data):
        try:
            try:
                end_time = data['data']['headVo']['expirationDate']
            except:
                end_time = None
            if not end_time:
                return
            else:
                try:
                    a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))
                except:
                    return
                b = int(time.time())
                if a < b:
                    self.connection.srem('koolearn_course_id', course_id)
        except Exception as e:
            text = f'[koolearn_id]删除id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_id]删除id获取失败,error_msg:{e},res:{data}')

    def del_id2(self, response):
        try:
            try:
                start_time = response.xpath('//*[contains(text(),"开课时间")]/text()').extract_first().replace('开课时间：',
                                                                                                           '').strip()
            except:
                start_time = None
            try:
                end_time = response.xpath('//*[contains(text(),"有效期")]/text()').extract_first().replace('课程',
                                                                                                        '').replace(
                    '有效期：', '').strip()
                if start_time:
                    end_time = get_end_time(start_time, end_time)
            except:
                end_time = None
            if not end_time:
                return
            else:
                try:
                    a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))
                except:
                    return
                b = int(time.time())
                if a < b:
                    self.connection.srem('koolearn_course_id', response.meta['course_id'])
        except Exception as e:
            text = f'[koolearn_id]删除id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_id]删除id获取失败,error_msg:{e},res:{response.text}')


if __name__ == '__main__':
    pass

