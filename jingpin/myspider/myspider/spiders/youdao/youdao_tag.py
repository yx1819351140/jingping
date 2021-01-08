# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import time
import json
from myspider.utils import safe_json_loads, get_data, dingding_alert
from myspider.items import TagItem
from scrapy import Request
from datetime import datetime
from myspider.settings import TAGS, handler

logger = logging.getLogger(__name__)


class YoudaoTagSpider(scrapy.Spider):
    name = 'youdao_tag'
    allowed_domains = ['youdao.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def __init__(self):
        self.dict = {
            44: '考研英语',
            46: '考研政治',
            48: '考研数学',
        }
        super().__init__()

    def start_requests(self):
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
                logger.error(f'[youdao_tag]获取Tag_id失败,res:{response.text}')
            if response.meta['tag'] == '考研':
                tag_dict = {}
                for temp in dict_data['data']['subTag']:
                    if temp['name'] == '四六级':
                        continue
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
            text = f'[youdao_tag]tags获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_tag]tags获取失败,error_msg:{e},res:{response.text}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                logger.error(f'[youdao_tag]获取Tag_id失败,res:{response.text}')
            try:
                course_list = dict_data['data']['courses']
            except:
                course_list = dict_data['data']['course']
            if not course_list:
                return
            for course in course_list:
                item = TagItem()
                item['com'] = 'youdao'
                item['type'] = '考研'
                item['course_id'] = str(course['id'])
                item['url'] = f'https://ke.youdao.com/course/detail/{course["id"]}'
                item['season'] = response.meta['season']
                item['class_type'] = None
                item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if course['subCategories']:
                    if self.dict.__contains__(course['subCategories'][0]['id']):
                        item['subject'] = self.dict[course['subCategories'][0]['id']]
                        item['sub_subject'] = None
                    else:
                        if '管综' in course['courseTitle']:
                            item['sub_subject'] = '考研管综'
                        elif '西医' in course['courseTitle']:
                            item['sub_subject'] = '考研西医'
                        elif '计算机' in course['courseTitle']:
                            item['sub_subject'] = '考研计算机'
                        else:
                            item['sub_subject'] = course['subCategories'][0]['name']
                        item['subject'] = None
                else:
                    item['subject'] = dict_data['data']['name']
                    item['sub_subject'] = None
                # print(json.dumps(dict(item)) )
                logger.info(f'[youdao]考研tags获取成功, course_id:{course["id"]}')
                yield item
            rank = course_list[-1]['rank']
            url = f'https://ke.youdao.com/course3/api/content/course?tag={response.meta["id"]}&rank={rank}'
            # print(url)
            yield Request(url, meta={'season': response.meta['season'], 'id': response.meta['id']}, callback=self.parse1)
        except Exception as e:
            text = f'[youdao_tag]考研tags获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_tag]考研tags获取失败,error_msg:{e},res:{response.text}')

    def parse2(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                logger.error(f'[youdao_tag]获取Tag_id失败,res:{response.text}')
            try:
                course_list = dict_data['data']['courses']
            except:
                course_list = dict_data['data']['course']
            if not course_list:
                return
            for course in course_list:
                if course['categoryName'] == '四六级':
                    item = TagItem()
                    item['com'] = 'youdao'
                    item['url'] = f'https://ke.youdao.com/course/detail/{course["id"]}'
                    item['type'] = '四六级'
                    try:
                        item['course_id'] = str(course['id'])
                    except:
                        continue
                    if course['courseSalePrice'] == 0:
                        item['class_type'] = '免费好课'
                    else:
                        item['class_type'] = None
                    item['season'] = response.meta['season']
                    item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item['subject'] = None
                    item['sub_subject'] = None
                    # print(json.dumps(dict(item)))
                    logger.error(f'[youdao_tag]四六级tags获取成功, course_id:{course["id"]}')
                    yield item
            rank = course_list[-1]['rank']
            url = f'https://ke.youdao.com/course3/api/content/course?tag={response.meta["id"]}&rank={rank}'
            # print(url)
            yield Request(url, meta={'season': response.meta['season'], 'id': response.meta['id']},
                          callback=self.parse1)
        except Exception as e:
            text = f'[youdao_tag]四六级tags获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_tag]四六级tags获取失败,error_msg:{e},res:{response.text}')

