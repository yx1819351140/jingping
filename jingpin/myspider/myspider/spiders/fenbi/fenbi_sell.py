# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert
from myspider.items import SellItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class FenbiSellSpider(scrapy.Spider):
    name = 'fenbi_sell'
    allowed_domains = ['fenbi.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = f'http://ke.fenbi.com/win/v3/courses'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[fenbi_sell]get course failed，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenfenbi_sell]get course failed，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            category_list = dict_data['datas']
            if category_list:
                start = 0
                for category in category_list:
                    url = f'https://ke.fenbi.com/win/{category["prefix"]}/v3/content?start={start}&len=100'
                    yield Request(url, meta={'prefix': category["prefix"], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[fenbi_sell]get category failed，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi_sell]get category failed，error_msg:{e}')

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
                            item = self.parse_course_sell(product)
                            yield item
                        except Exception as e:
                            text = f'[fenbi]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.error(f'[fenbi]获取课程详情失败，error_msg:{e}')
            start = response.meta['start']
            start += 100
            if start < dict_data['total']:
                url = f'https://ke.fenbi.com/win/{response.meta["prefix"]}/v3/content?start={start}&len=100'
                yield Request(url, meta={'prefix': response.meta['prefix'], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[fenbi_sell]获取课程id失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[fenbi_sell]获取课程id失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = str(product['id'])
        except:
            item['course_id'] = None
        try:
            item['sell'] = str(product['studentCount'])
        except:
            item['sell'] = None
        item['com'] = 'fenbi'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
