# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import time
import json
from myspider.utils import safe_json_loads, dingding_alert, get_end_time
from myspider.items import TagItem
from scrapy import Request
from datetime import datetime
from myspider.settings import TAGS, REDIS_URI_, REDIS_PASSWORD_, handler
import redis

logger = logging.getLogger(__name__)


class YoudaoDelTagSpider(scrapy.Spider):
    name = 'youdao_del_id'
    logger.addHandler(handler)
    allowed_domains = ['youdao.com']
    # start_urls = ['https://www.koolearn.com/']

    def __init__(self):
        self.dict = {
            44: '考研英语',
            46: '考研政治',
            48: '考研数学',
        }
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'ke.youdao.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': None,
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }
        self.connection = redis.Redis(host=REDIS_URI_, port=6379, password=REDIS_PASSWORD_)
        super().__init__()

    def start_requests(self):
        self.course_id_set = self.connection.smembers('youdao_course_id')
        if self.course_id_set:
            for course_id in self.course_id_set:
                yield Request(f'https://ke.youdao.com/course/detail/{course_id.decode()}', headers=self.headers, meta={'course_id': course_id.decode()}, callback=self.del_id)

    def del_id(self, response):
        try:
            try:
                start_time = response.xpath('//*[contains(text(),"开课时间")]/text()').extract_first().replace('开课时间：',
                                                                                                           '').strip()
            except:
                start_time = None
            try:
                end_time = response.xpath('//*[contains(text(),"有效期")]/text()').extract_first().replace('有效期至：',
                                                                                                        '').strip()
                if start_time:
                    end_time = get_end_time(start_time, end_time)
            except:
                end_time = None
            if end_time == None:
                return
            else:
                try:
                    a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S")))
                except:
                    try:
                        a = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M")))
                    except:
                        return
                b = int(time.time())
                if a < b:
                    self.connection.srem('youdao_course_id', response.meta['course_id'])
        except Exception as e:
            text = f'[youdao_id]删除id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_id]删除id获取失败,error_msg:{e},res:{response.text}')

