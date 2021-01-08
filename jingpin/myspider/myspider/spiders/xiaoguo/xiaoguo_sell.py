# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert
from myspider.items import SellItem
from myspider.settings import CATEGORYS, handler
from scrapy import Request

logger = logging.getLogger(__name__)


class XiaoguoSellSpider(scrapy.Spider):
    name = 'xiaoguo_sell'
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
                        item = self.parse_course_sell(product)
                        yield item
                    except Exception as e:
                        text = f'[xiaoguo]获取课程详情失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[xiaoguo]获取课程详情失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = f'https://h.xiaoguo101.com/api/courses/products/recommend?page={page}&categoryId={response.meta["category_id"]}'
                yield Request(url=url, headers=self.headers, meta={'page': page, 'category_id': response.meta["category_id"], 'type': CATEGORYS[response.meta["category_id"]]}, callback=self.parse)
        except Exception as e:
            text = f'[xiaoguo]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[xiaoguo]获取课程信息失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = product['id']
        except:
            item['course_id'] = None
        item['com'] = 'xiaoguo'
        item['sell'] = str(product['purchaseNumber'])
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
