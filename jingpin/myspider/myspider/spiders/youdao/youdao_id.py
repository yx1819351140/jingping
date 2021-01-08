# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import time
import json
from myspider.utils import safe_json_loads, get_data, dingding_alert, get_end_time
from myspider.items import TagItem
from scrapy import Request
from datetime import datetime
from myspider.settings import TAGS, REDIS_URI_, REDIS_PASSWORD_, handler
import redis

logger = logging.getLogger(__name__)


class YoudaoTagSpider(scrapy.Spider):
    name = 'youdao_id'
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
        for tag in TAGS:
            if tag == '考研':
                url = 'https://ke.youdao.com/course3/api/vertical2?tag=424'
            elif tag == '四六级':
                url = 'https://ke.youdao.com/course3/api/vertical2?tag=870'
            else:
                url = None
            yield Request(url=url, meta={'tag': tag}, callback=self.parse)

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                logger.error(f'[youdao_id]获取id失败,res:{response.text}')
            if response.meta['tag'] == '考研':
                tag_dict = {}
                for temp in dict_data['data']['subTag'][:2]:
                    try:
                        tag_dict[temp['id']] = temp['name']
                    except:
                        continue
                for id in tag_dict.keys():
                    url = f'https://ke.youdao.com/course3/api/vertical2?tag={id}'
                    season = tag_dict[id]
                    yield Request(url, meta={'season': season, 'id': id}, callback=self.parse1)
            elif response.meta['tag'] == '四六级':
                tag_dict = {}
                for temp in dict_data['data']['subTag'][1:3]:
                    try:
                        tag_dict[temp['id']] = temp['name']
                    except:
                        continue
                for id in tag_dict.keys():
                    url = f'https://ke.youdao.com/course3/api/vertical2?tag={id}'
                    season = tag_dict[id]
                    yield Request(url, meta={'season': season, 'id': id}, callback=self.parse2)
        except Exception as e:
            text = f'[youdao_id]id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_id]id获取失败,error_msg:{e},res:{response.text}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                logger.error(f'[youdao_id]获取id失败,res:{response.text}')
            try:
                course_list = dict_data['data']['courses']
            except:
                course_list = dict_data['data']['course']
            if not course_list:
                return
            for course in course_list:
                course_id = str(course['id'])
                if course_id.encode() not in self.course_id_set:
                    self.connection.sadd('youdao_course_id', course_id)
                logger.info(f'[youdao_id]考研id获取成功, course_id:{course["id"]}')
            rank = course_list[-1]['rank']
            url = f'https://ke.youdao.com/course3/api/content/course?tag={response.meta["id"]}&rank={rank}'
            # print(url)
            yield Request(url, meta={'season': response.meta['season'], 'id': response.meta['id']}, callback=self.parse1)
        except Exception as e:
            text = f'[youdao_id]考研id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_id]考研id获取失败,error_msg:{e},res:{response.text}')

    def parse2(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                logger.error(f'[youdao_id]获取id失败,res:{response.text}')
            try:
                course_list = dict_data['data']['courses']
            except:
                course_list = dict_data['data']['course']
            if not course_list:
                return
            for course in course_list:
                course_id = str(course['id'])
                if course_id.encode() not in self.course_id_set:
                    self.connection.sadd('youdao_course_id', course_id)
                # print(json.dumps(dict(item)))
                logger.info(f'[youdao_id]四六级id获取成功, course_id:{course["id"]}')
            rank = course_list[-1]['rank']
            url = f'https://ke.youdao.com/course3/api/content/course?tag={response.meta["id"]}&rank={rank}'
            # print(url)
            yield Request(url, meta={'season': response.meta['season'], 'id': response.meta['id']},
                          callback=self.parse1)
        except Exception as e:
            text = f'[youdao_id]四六级id获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_id]四六级id获取失败,error_msg:{e},res:{response.text}')

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

