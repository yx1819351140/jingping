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


class GenshuixueSellSpider(scrapy.Spider):
    name = 'genshuixue_sell'
    allowed_domains = ['genshuixue.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = 'https://sapi.genshuixue.com/sapi/viewLogic/homepage/channelPublicClazzs?version=4.5.1&dsp=app&size=3&channelId=9'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[genshuixue_sell]获取公开课id失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue_sell]获取公开课id失败，error_msg:{e}')

    def parse(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            product_list = dict_data['data']['items']
            for product in product_list:
                try:
                    item = self.parse_course_sell(product)
                    yield item
                except Exception as e:
                    text = f'[genshuixue_sell]获取课程信息失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                    dingding_alert(text)
                    logger.error(f'[genshuixue_sell]获取课程信息失败，error_msg:{e}')
                    continue
        except Exception as e:
            text = f'[genshuixue_sell]获取课程销量失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[genshuixue_sell]获取课程销量失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = product['clazzNumber']
        except:
            item['course_id'] = None
        try:
            item['sell'] = str(product['studentCount'])
        except:
            item['sell'] = None
        item['com'] = 'genshuixue'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
