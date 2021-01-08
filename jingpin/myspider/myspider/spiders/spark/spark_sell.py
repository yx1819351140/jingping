# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert, get_url
from myspider.items import SellItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class SparkSellSpider(scrapy.Spider):
    name = 'spark_sell'
    allowed_domains = ['spark.cn']
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
                        item = self.parse_course_sell(product)
                        yield item
                    except Exception as e:
                        text = f'[spark]获取实时销量失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[spark]获取实时销量失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = get_url(response.meta['grade'], page)
                yield Request(url=url, meta={'page': page, 'grade': response.meta["grade"], 'type': self.grade_dict[response.meta["grade"]]}, callback=self.parse)
        except Exception as e:
            text = f'[spark]获取实时销量失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[spark]获取实时销量失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = product['key']
        except:
            item['course_id'] = None
        try:
            item['sell'] = str(product['buyers'])
        except:
            item['sell'] = None
        item['com'] = 'spark'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
