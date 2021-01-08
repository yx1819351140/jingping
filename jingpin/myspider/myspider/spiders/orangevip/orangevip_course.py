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


class OrangevipSpider(scrapy.Spider):
    name = 'orangevip'
    allowed_domains = ['orangevip.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = 'https://www.orangevip.com/index'
            yield Request(url, callback=self.parse)
        except Exception as e:
            text = f'[orangevip]访问首页失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip]访问首页失败，error_msg:{e}')

    def parse(self, response):
        try:
            page = 1
            category_list = response.xpath('//a[@class="categoryItem"]/@href').extract()
            for category in category_list:
                url = f'https://www.orangevip.com{category}_p{page}'
                yield Request(url=url, meta={'page': page, 'category': category}, callback=self.parse1)
        except Exception as e:
            text = f'[orangevip]获取数据url失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip]获取数据url失败，error_msg:{e}')

    def parse1(self, response):
        try:
            json_data = re.search('window\.__NUXT__=(.*);</script>', response.text).group(1)
            dict_data = safe_json_loads(json_data)
            product_list = dict_data['data'][0]['currentCourseData']
            subject = dict_data['data'][0]['keyName']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_info(product)
                        yield item
                    except Exception as e:
                        text = f'[orangevip]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[orangevip]获取课程详情失败，error_msg:{e}')
                        continue
                    try:
                        item = self.parse_course_tag(product, subject)
                        yield item
                    except Exception as e:
                        text = f'[orangevip]获取课程标签失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[orangevip]获取课程标签失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = f'https://www.orangevip.com{response.meta["category"]}_p{page}'
                yield Request(url=url, meta={'page': page, 'category': response.meta["category"]}, callback=self.parse)
        except Exception as e:
            text = f'[orangevip]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip]获取课程信息失败，error_msg:{e}')

    def parse_course_info(self, product):
        item = CourseItem()
        try:
            item['course_id'] = str(product['productId'])
            item['url'] = f'https://www.orangevip.com/coursedetail/{str(product["productId"])}.html'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['title'] = product['productName']
        except:
            item['title'] = None
        try:
            item['start_time'] = product['startDate']
        except:
            item['start_time'] = None
        try:
            item['end_time'] = product['endDate']
        except:
            item['end_time'] = None
        try:
            item['sell'] = str(product['selledCount'])
        except:
            item['sell'] = None
        try:
            item['original_price'] = str(product['originaPrice'])
        except:
            item['original_price'] = None
        try:
            item['current_price'] = str(product['currentPrice'])
        except:
            item['current_price'] = None
        try:
            teacher = ''
            for temp in product['teacherList']:
                teacher = teacher + temp['teacherName'] + ','
            item['teacher'] = teacher
        except:
            item['teacher'] = None
        try:
            item['course_hour'] = str(product['courseHours'])
        except:
            item['course_hour'] = None
        try:
            item['course_format'] = product['classModel']
        except:
            item['course_format'] = None
        item['course_service'] = None
        item['student'] = None
        item['course_info'] = None
        item['com'] = 'orangevip'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item

    def parse_course_tag(self, product, subject):
        item = TagItem()
        try:
            item['course_id'] = str(product['productId'])
            item['url'] = f'https://www.orangevip.com/coursedetail/{str(product["productId"])}.html'
        except:
            item['course_id'] = None
            item['url'] = None
        try:
            item['type'] = product['tag']
        except:
            item['type'] = None
        item['class_type'] = None
        item['season'] = None
        item['com'] = 'orangevip'
        item['subject'] = subject
        item['sub_subject'] = None
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
