# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert, get_strp_time
from myspider.items import CourseItem, TagItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class FenbiSpider(scrapy.Spider):
    name = 'fenbi'
    allowed_domains = ['fenbi.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = f'http://ke.fenbi.com/win/v3/courses'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[fenbi]get course failed，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi]get course failed，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            category_list = dict_data['datas']
            if category_list:
                start = 0
                for category in category_list:
                    url = f'http://ke.fenbi.com/win/{category["prefix"]}/v3/content?start={start}&len=100'
                    yield Request(url, meta={'name': category['name'], 'prefix': category["prefix"], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[fenbi]get category failed，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi]get category failed，error_msg:{e}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['datas']
            if product_list:
                for product in product_list:
                    product = product['lectureSummary'] if product['lectureSummary'] else product['lectureSetSummary']
                    if product:
                        try:
                            item = self.parse_course_info(product)
                            yield item
                        except Exception as e:
                            text = f'[fenbi]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.error(f'[fenbi]获取课程详情失败，error_msg:{e}')
                        try:
                            item = self.parse_course_tag(product, response.meta['name'])
                            yield item
                        except Exception as e:
                            text = f'[fenbi]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.error(f'[fenbi]获取课程标签失败，error_msg:{e}')
                    # self.save_data(product, response.meta['name'])
            start = response.meta['start']
            start += 100
            if start < dict_data['total']:
                url = f'http://ke.fenbi.com/win/{response.meta["prefix"]}/v3/content?start={start}&len=100'
                yield Request(url, meta={'name': response.meta['name'], 'prefix': response.meta['prefix'], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[fenbi]获取课程id失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi]获取课程id失败，error_msg:{e}')

    def save_data(self, product, name):
        try:
            product = product['lectureSummary'] if product['lectureSummary'] else product['lectureSetSummary']
            if product:
                try:
                    item = self.parse_course_info(product)
                    yield item
                except Exception as e:
                    text = f'[fenbi]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[fenbi]获取课程详情失败，error_msg:{e}')
                try:
                    item = self.parse_course_tag(product, name)
                    yield item
                except Exception as e:
                    text = f'[fenbi]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[fenbi]获取课程标签失败，error_msg:{e}')
        except Exception as e:
            text = f'[fenbi]获取课程信息失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = str(product['id'])
            item['url'] = f'https://www.fenbi.com/spa/pwa/lecture/{product["id"]}/0'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['title'] = product['title']
        except:
            item['title'] = None
        try:
            item['start_time'] = get_strp_time(product['classStartTime']/1000)
        except:
            item['start_time'] = None
        try:
            item['end_time'] = get_strp_time(product['classEndTime']/1000)
        except:
            item['end_time'] = None
        try:
            item['sell'] = str(product['studentCount'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['origin_price']/100)
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['price']/100)
        except:
            item['current_price'] = None
        teacher = ''
        for temp in product['teachers']:
            teacher = teacher + temp['name'] + ','
        item['teacher'] = teacher
        try:
            item['course_hour'] = str(product['classHours'])
        except:
            item['course_hour'] = None
        item['course_service'] = None
        item['student'] = None
        item['course_format'] = None
        item['course_info'] = None
        item['com'] = 'fenbi'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, subject):
        item = TagItem()
        try:
            item['course_id'] = str(product['id'])
            item['url'] = f'https://www.fenbi.com/spa/pwa/lecture/{product["id"]}/0'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['subject'] = subject
        except:
            item['subject'] = None
        try:
            item['class_type'] = product['productType']['name']
        except:
            item['class_type'] = None
        item['season'] = None
        item['com'] = 'fenbi'
        item['type'] = None
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
