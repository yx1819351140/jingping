# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert
from myspider.items import CourseItem, TagItem
from myspider.settings import CATEGORYS, handler
from scrapy import Request

logger = logging.getLogger(__name__)


class XiaoguoSpider(scrapy.Spider):
    name = 'xiaoguo'
    allowed_domains = ['xiaoguo101.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            self.headers = {
                'XSC-CLIENT': 'PYM7F7by',
            }
            page = 1
            for category_id in CATEGORYS:
                url = f'https://h.xiaoguo101.com/api/courses/products/recommend?page={page}&categoryId={category_id}'
                yield Request(url=url, headers=self.headers, meta={'page': page, 'category_id': category_id, 'type': CATEGORYS[category_id]}, callback=self.parse)
        except Exception as e:
            text = f'[xiaoguo]访问首页失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue]访问首页失败，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            product_list = dict_data['data']['list']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_info(product)
                        yield item
                    except Exception as e:
                        text = f'[xiaoguo]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[xiaoguo]获取课程详情失败，error_msg:{e}')
                        continue
                    try:
                        item = self.parse_course_tag(product, response.meta['type'])
                        yield item
                    except Exception as e:
                        text = f'[xiaoguo]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[xiaoguo]获取课程标签失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = f'https://h.xiaoguo101.com/api/courses/products/recommend?page={page}&categoryId={response.meta["category_id"]}'
                yield Request(url=url, headers=self.headers, meta={'page': page, 'category_id': response.meta["category_id"], 'type': CATEGORYS[response.meta["category_id"]]}, callback=self.parse)
        except Exception as e:
            text = f'[xiaoguo]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[xiaoguo]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = product['id']
            item['url'] = f'https://pc.xiaoguo101.com/#/detail/i/{product["id"]}/index'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['title'] = product['name']
        except:
            item['title'] = None
        try:
            item['start_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(product['startTime']/1000))
        except:
            item['start_time'] = None
        try:
            item['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(product['endTime']/1000))
        except:
            item['end_time'] = None
        try:
            item['sell'] = str(product['purchaseNumber'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['originPrice'])
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['sellingPrice'])
        except:
            item['current_price'] = None
        try:
            teacher = ''
            for temp in product['teachers']:
                teacher = teacher + temp['name'] + ','
            item['teacher'] = teacher
        except:
            item['teacher'] = None
        try:
            item['course_hour'] = str(product['classHour'])
        except:
            item['course_hour'] = None
        item['student'] = None
        item['course_format'] = None
        item['course_service'] = None
        item['course_info'] = None
        item['com'] = 'xiaoguo'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, type):
        item = TagItem()
        try:
            item['course_id'] = product['id']
            item['url'] = f'https://pc.xiaoguo101.com/#/detail/i/{product["id"]}/index'
        except:
            item['course_id'] = None
            item['url'] = None
        item['subject'] = None
        item['class_type'] = None
        item['season'] = None
        item['com'] = 'xiaoguo'
        item['type'] = type
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
