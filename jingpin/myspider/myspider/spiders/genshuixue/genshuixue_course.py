# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert
from myspider.items import CourseItem, TagItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class GenshuixueSpider(scrapy.Spider):
    name = 'genshuixue'
    allowed_domains = ['genshuixue.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = 'https://sapi.genshuixue.com/sapi/viewLogic/homepage/channelHaokeClazzs?dsp=app&version=4.5.1&channelId=9'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[genshuixue]获取好课推荐失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue]获取好课推荐失败，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            product_list = dict_data['data']['items']
            for product in product_list:
                try:
                    item = self.parse_course_info(product)
                    yield item
                except Exception as e:
                    text = f'[genshuixue]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[genshuixue]获取课程详情失败，error_msg:{e}')
                    continue
                try:
                    item = self.parse_course_tag(product)
                    yield item
                except Exception as e:
                    text = f'[genshuixue]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[genshuixue]获取课程标签失败，error_msg:{e}')
                    continue
            url = 'https://sapi.genshuixue.com/sapi/viewLogic/homepage/channelPublicClazzs?version=4.5.1&dsp=app&size=3&channelId=9'
            yield Request(url=url, callback=self.parse1)
        except Exception as e:
            text = f'[genshuixue]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue]获取课程信息失败，error_msg:{e}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            product_list = dict_data['data']['items']
            for product in product_list:
                try:
                    item = self.parse_course_info(product)
                    yield item
                except Exception as e:
                    text = f'[genshuixue]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[genshuixue]获取课程详情失败，error_msg:{e}')
                    continue
                try:
                    item = self.parse_course_tag(product)
                    yield item
                except Exception as e:
                    text = f'[genshuixue]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[genshuixue]获取课程标签失败，error_msg:{e}')
                    continue
        except Exception as e:
            text = f'[genshuixue]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = product['clazzNumber']
        except:
            item['course_id'] = None
        try:
            item['url'] = product['clazzDetailSchema']
        except:
            item['url'] = None
        try:
            item['title'] = product['clazzName']
        except:
            item['title'] = None
        start_end = product.get('arrangement', None)
        if start_end:
            try:
                item['start_time'] = str(start_end.split('-')[0])
                item['end_time'] = str(start_end.split('-')[1])
            except:
                item['start_time'] = None
                item['end_time'] = None
        else:
            item['start_time'] = None
            item['end_time'] = None
        try:
            item['sell'] = str(product['studentCount'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['discount']['originPrice']/100)
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['discount']['price']/100)
        except:
            item['current_price'] = None
        try:
            teacher = ''
            for temp in product['masterTeachers']:
                teacher = teacher + temp['name'] + ','
            item['teacher'] = teacher
        except:
            item['teacher'] = None
        item['student'] = None
        item['course_hour'] = None
        item['course_format'] = None
        item['course_service'] = None
        item['course_info'] = None
        item['com'] = 'genshuixue'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product):
        item = TagItem()
        try:
            item['url'] = product['clazzDetailSchema']
        except:
            item['url'] = None
        try:
            item['course_id'] = product['clazzNumber']
        except:
            item['course_id'] = None
        try:
            item['subject'] = product['masterSubject']['name']
        except:
            item['subject'] = None
        try:
            item['class_type'] = product['category']
        except:
            item['class_type'] = None
        item['season'] = None
        item['com'] = 'genshuixue'
        item['type'] = '考研'
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
