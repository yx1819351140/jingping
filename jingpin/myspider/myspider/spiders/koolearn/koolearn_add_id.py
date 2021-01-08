# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import json
import time
from myspider.utils import safe_json_loads, dingding_alert, get_data
from myspider.settings import TAGS, REDIS_URI_, REDIS_PASSWORD_, handler
import redis
from scrapy import Request
from datetime import datetime

logger = logging.getLogger(__name__)


class KoolearnAddIdSpider(scrapy.Spider):
    name = 'koolearn_add_id'
    logger.addHandler(handler)
    allowed_domains = ['koolearn.com']

    def __init__(self):
        self.connection = redis.Redis(host=REDIS_URI_, port=6379, password=REDIS_PASSWORD_)
        super().__init__()

    def start_requests(self):
        self.course_id_set = self.connection.smembers('koolearn_course_id')
        for tag in TAGS:
            if tag == '考研':
                for id in [8, 12]:
                    url = f'https://kebiao.koolearn.com/v1/timeTableCommonSplit/query-time-table?id={id}'
                    yield Request(url, callback=self.parse1)
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
            product_list = dict_data['data']['data']
            if not product_list:
                return
            product_url = 'https://kebiao.koolearn.com/v1/timeTableCommonSplit/query-productList?timetableId=12&version=312&classifyId={}&style=1'
            for product in product_list:
                if not product['data']:
                    yield Request(product_url.format(product['id']), callback=self.parse3)
                else:
                    for product1 in product['data']:
                        if not product1['data']:
                            yield Request(product_url.format(product1['id']), callback=self.parse3)
                        else:
                            for product2 in product1['data']:
                                yield Request(product_url.format(product2['id']), callback=self.parse3)
        except Exception as e:
            text = f'[koolearn_add_id]考研id获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_add_id]考研id获取失败, err_msg:{e}, res:{response.text}')

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
                text = f'[koolearn_add_id]四六级id获取失败, err_msg:获取页面内json数据失败\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[koolearn_add_id]四六级id获取失败, res:{response.text}')
        except Exception as e:
            text = f'[koolearn_add_id]四六级id获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_add_id]四六级id获取失败, err_msg:{e}, res:{response.text}')

    def parse3(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['data']
            if not product_list:
                return
            for product in product_list:
                course_id = str(product.get('productId', ''))
                if course_id.encode() not in self.course_id_set:
                    self.connection.sadd('koolearn_course_id', course_id)
        except Exception as e:
            text = f'[koolearn_add_id]考研id获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_add_id]考研id获取失败, err_msg:{e}, res:{response.text}')


if __name__ == '__main__':
    pass

