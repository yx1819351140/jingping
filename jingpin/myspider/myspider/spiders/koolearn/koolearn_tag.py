# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import time
import json
import sys
import os
from scrapy.cmdline import execute
from myspider.utils import safe_json_loads, get_data, dingding_alert
from myspider.items import TagItem
from scrapy import Request
from datetime import datetime
from myspider.settings import TAGS, handler

logger = logging.getLogger(__name__)


class KoolearnTagSpider(scrapy.Spider):
    name = 'koolearn_tag'
    allowed_domains = ['koolearn.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
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
                                data = get_data(type_dict[class_type][0], season_dict[season], type_dict[class_type][1], subject_dict[subject])
                                yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data, 'subject': subject, 'season': season, 'class_type': class_type}, callback=self.parse1)
                            else:
                                for sub_subject in subject_dict[subject].keys():
                                    data = get_data(type_dict[class_type][0], season_dict[season], type_dict[class_type][1], subject_dict[subject][sub_subject])
                                    yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data, 'subject': subject, 'sub_subject': sub_subject, 'season': season, 'class_type': class_type}, callback=self.parse1)
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
                course_id = product.get('productId', '')
                course_url = 'https:' + product.get('productUrl', '')
                item = TagItem()
                item['com'] = 'koolearn'
                item['course_id'] = str(course_id)
                item['url'] = course_url
                item['subject'] = response.meta['subject']
                try:
                    item['sub_subject'] = response.meta['sub_subject']
                except:
                    item['sub_subject'] = None
                item['season'] = response.meta['season']
                item['class_type'] = response.meta['class_type']
                item['type'] = '考研'
                item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # print(json.dumps(dict(item)))
                logger.info(f'[koolearn_tag]考研tags获取成功, course_id:{course_id}')
                yield item
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
                    yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data, 'subject': response.meta['subject'], 'sub_subject': response.meta['sub_subject'], 'season': response.meta['season'], 'class_type': response.meta['class_type']}, callback=self.parse1)
                except:
                    yield Request(url, method='POST', headers=headers, body=json.dumps(data), meta={'data': data, 'subject': response.meta['subject'], 'season': response.meta['season'], 'class_type': response.meta['class_type']}, callback=self.parse1)
        except Exception as e:
            text = f'[koolearn_tag]考研tags获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_tag]考研tags获取失败, err_msg:{e}, res:{response.text}')

    def parse2(self, response):
        result = re.search('data: \[\{.*\}\);', response.text)
        try:
            if result:
                dict_data = safe_json_loads('{"data"' + result.group()[4:-2])
                class_dict = dict()
                for data in dict_data['data']:
                    if data['parent'] == '0':
                        class_dict[data['id']] = data['text']
                    elif data['parent'] == 1819:
                        continue
                    else:
                        if not data['content']:
                            continue
                        for course in data['content']:
                            item = TagItem()
                            if data['parent'] in ['1817', '1818']:
                                item['subject'] = class_dict[str(data['parent'])]
                                item['class_type'] = None
                            else:
                                item['class_type'] = class_dict[str(data['parent'])]
                                item['subject'] = None
                            if '【' in course['alias']:
                                item['season'] = re.search('【(.*)】', course['alias']).group(1)
                            else:
                                item['season'] = None
                            item['com'] = 'koolearn'
                            item['type'] = '四六级'
                            item['course_id'] = str(course['p_id'])
                            item['url'] = course['title_url']
                            item['sub_subject'] = None
                            item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # print(json.dumps(dict(item)))
                            logger.info(f'[koolearn_tag]四六级tags获取成功, course_id:{course["p_id"]}')
                            yield item
            else:
                text = f'[koolearn_tag]四六级tags获取失败, err_msg:获取页面内json数据失败\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[koolearn_tag]四六级tags获取失败, res:{response.text}')
        except Exception as e:
            text = f'[koolearn_tag]四六级tags获取失败, err_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_tag]四六级tags获取失败, err_msg:{e}, res:{response.text}')


if __name__ == '__main__':
    pass

