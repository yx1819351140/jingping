# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert, get_url
from myspider.items import CourseItem, TagItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class ShanbaySpider(scrapy.Spider):
    name = 'shanbay'
    allowed_domains = ['shanbay.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            self.category_dict = {'brfpia': '四六级考研', 'ugjmp': '阅读', 'juuxc': '听力口语'}
            for category in self.category_dict:
                url = f'https://apiv3.shanbay.com/wordsutils/course_tab/azs?tab_id={category}'
                yield Request(url=url, meta={'category': self.category_dict[category]}, callback=self.parse)
        except Exception as e:
            text = f'[shanbay]get course failed，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[shanbay]get course failed，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['objects'][0]['azs']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_info(product)
                        yield item
                    except Exception as e:
                        text = f'[shanbay]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[shanbay]获取课程详情失败，error_msg:{e}')
                        continue
                    try:
                        item = self.parse_course_tag(product, response.meta['category'])
                        yield item
                    except Exception as e:
                        text = f'[shanbay]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[shanbay]获取课程标签失败，error_msg:{e}')
                        continue
        except Exception as e:
            text = f'[shanbay]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[shanbay]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = product['id']
        except:
            item['course_id'] = None
        try:
            item['url'] = product['next_url']
        except:
            item['url'] = None
        try:
            item['title'] = product['title']
        except:
            item['title'] = None
        try:
            item['original_price'] = str(product['origin_price']/100)
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['price']/100)
        except:
            item['current_price'] = None
        item['start_time'] = None
        item['end_time'] = None
        item['sell'] = None
        item['teacher'] = None
        item['course_hour'] = None
        item['course_service'] = None
        item['student'] = None
        item['course_format'] = None
        item['course_info'] = None
        item['com'] = 'shanbay'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, subject):
        item = TagItem()
        try:
            item['course_id'] = product['id']
        except:
            item['course_id'] = None
        try:
            item['url'] = product['next_url']
        except:
            item['url'] = None
        try:
            item['subject'] = subject
        except:
            item['subject'] = None
        item['class_type'] = None
        item['season'] = None
        item['com'] = 'shanbay'
        item['type'] = None
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass

