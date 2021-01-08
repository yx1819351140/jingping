# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import json
import time
from myspider.utils import safe_json_loads, get_end_time, dingding_alert
from myspider.settings import REDIS_URI_, REDIS_PASSWORD_, handler
import redis
from scrapy import Request

logger = logging.getLogger(__name__)


class KoolearnDelIdSpider(scrapy.Spider):
    name = 'koolearn_del_id'
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
            text = f'[koolearn_del_id]删除id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_del_id]删除id获取失败,error_msg:{e},res:{data}')

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
            text = f'[koolearn_del_id]删除id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_del_id]删除id获取失败,error_msg:{e},res:{response.text}')


if __name__ == '__main__':
    pass

