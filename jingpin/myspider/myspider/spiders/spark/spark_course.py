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


class SparkSpider(scrapy.Spider):
    name = 'spark'
    allowed_domains = ['sparke.cn']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            page = 1
            self.grade_dict = {'1': '四六级', '2': '考研英语'}
            for grade in self.grade_dict:
                url = get_url(grade, page)
                yield Request(url=url, meta={'page': page, 'grade': grade, 'type': self.grade_dict[grade]}, callback=self.parse)
        except Exception as e:
            text = f'[spark]访问首页失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[spark]访问首页失败，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            product_list = dict_data['results']['list']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_info(product)
                        yield item
                    except Exception as e:
                        text = f'[spark]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[spark]获取课程详情失败，error_msg:{e}')
                        continue
                    try:
                        item = self.parse_course_tag(product, response.meta['type'])
                        yield item
                    except Exception as e:
                        text = f'[spark]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[spark]获取课程标签失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = get_url(response.meta['grade'], page)
                yield Request(url=url, meta={'page': page, 'grade': response.meta["grade"], 'type': self.grade_dict[response.meta["grade"]]}, callback=self.parse)
        except Exception as e:
            text = f'[spark]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[spark]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = product['key']
            item['url'] = f'https://www.sparke.cn/network/networkDetails?key={product["key"]}'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['title'] = product['title']
        except:
            item['title'] = None
        try:
            live_time = product['liveTime']
            try:
                item['start_time'] = live_time[3:13]
            except:
                item['start_time'] = None
            try:
                if len(live_time) == 19:
                    item['end_time'] = live_time[3:8] + live_time[14:]
                else:
                    item['end_time'] = live_time[-10:]
            except:
                item['end_time'] = None
        except:
            item['start_time'] = None
            item['end_time'] = None
        try:
            item['sell'] = str(product['buyers'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['price'])
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['disprice'])
        except:
            item['current_price'] = None
        try:
            item['teacher'] = product['teacher']
        except:
            item['teacher'] = None
        try:
            item['course_hour'] = str(product['period'])
        except:
            item['course_hour'] = None
        try:
            item['course_service'] = product['sellingPoint']
        except:
            item['course_service'] = None
        item['student'] = None
        item['course_format'] = None
        item['course_info'] = None
        item['com'] = 'spark'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, type):
        item = TagItem()
        try:
            item['course_id'] = product['key']
            item['url'] = f'https://www.sparke.cn/network/networkDetails?key={product["key"]}'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['subject'] = product['netSubjectName']
        except:
            item['subject'] = None
        item['class_type'] = None
        item['season'] = None
        item['com'] = 'spark'
        item['type'] = type
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
