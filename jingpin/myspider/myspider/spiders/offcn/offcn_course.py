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


class OffcnSpider(scrapy.Spider):
    name = 'offcn'
    allowed_domains = ['offcn.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = f'http://19.offcn.com/list/'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[offcn]get course failed，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn]get course failed，error_msg:{e}')

    def parse(self, response):
        try:
            category_list = response.xpath('//div[@class="zg19new_nav"]/ul/li//a/@href').getall()
            category_list1 = response.xpath('//div[@class="zg19new_nav"]/ul/li//a/text()').getall()
            if category_list:
                start = 1
                for i in range(1, len(category_list)):
                # for i in range(1, 2):
                    if 'list' in category_list[i]:
                        url = f'http://19.offcn.com{category_list[i]}?page={start}'
                        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
                        yield Request(url, headers=self.headers, meta={'category': category_list[i], 'name': category_list1[i], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[offcn]get category failed，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn]get category failed，error_msg:{e}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['data']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_info(product)
                        yield item
                    except Exception as e:
                        text = f'[offcn]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[offcn]获取课程详情失败，error_msg:{e}')
                    try:
                        item = self.parse_course_tag(product, response.meta['name'])
                        yield item
                    except Exception as e:
                        text = f'[offcn]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[offcn]获取课程标签失败，error_msg:{e}')
                start = response.meta['start']
                start += 1
                url = f'http://19.offcn.com{response.meta["category"]}?page={start}'
                yield Request(url, headers=self.headers, meta={'name': response.meta['name'], 'category': response.meta['category'], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[offcn]获取课程id失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn]获取课程id失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = str(product['id'])
            item['url'] = f'http://19.offcn.com/class-{product["id"]}/'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['title'] = product['title']
        except:
            item['title'] = None
        try:
            item['start_time'] = product['start_time'].replace('开课时间：', '').replace('.', '-') + ' 00:00:00'
        except:
            item['start_time'] = None
        try:
            item['end_time'] = product['course_validity'] + '23:59:59'
        except:
            item['end_time'] = None
        try:
            item['sell'] = str(product['num'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['original_price'])
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['price'])
        except:
            item['current_price'] = None
        item['teacher'] = None
        try:
            item['course_hour'] = str(product['lessonnum'])
        except:
            item['course_hour'] = None
        item['course_service'] = None
        item['student'] = None
        item['course_format'] = None
        item['course_info'] = None
        item['com'] = 'offcn'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, name):
        item = TagItem()
        try:
            item['course_id'] = str(product['id'])
            item['url'] = f'http://19.offcn.com/class-{product["id"]}/'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['type'] = name
        except:
            item['type'] = None
        item['subject'] = None
        item['class_type'] = None
        item['season'] = None
        item['com'] = 'offcn'
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
