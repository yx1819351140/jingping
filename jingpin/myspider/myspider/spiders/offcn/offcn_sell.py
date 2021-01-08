# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert, get_strp_time
from myspider.items import SellItem
from myspider.settings import handler
from scrapy import Request

logger = logging.getLogger(__name__)


class OffcnSellSpider(scrapy.Spider):
    name = 'offcn_sell'
    allowed_domains = ['offcn.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = f'http://19.offcn.com/list/'
            yield Request(url=url, callback=self.parse)
        except Exception as e:
            text = f'[offcn_sell]get course failed，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn_sell]get course failed，error_msg:{e}')

    def parse(self, response):
        try:
            category_list = response.xpath('//div[@class="zg19new_nav"]/ul/li//a/@href').getall()
            if category_list:
                start = 1
                for i in range(1, len(category_list)):
                #for i in range(1, 2):
                    if 'list' in category_list[i]:
                        url = f'http://19.offcn.com{category_list[i]}?page={start}'
                        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
                        yield Request(url, headers=self.headers, meta={'category': category_list[i], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[offcn_sell]get category failed，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn_sell]get category failed，error_msg:{e}')

    def parse1(self, response):
        try:
            dict_data = safe_json_loads(response.text)
            if not dict_data:
                return
            product_list = dict_data['data']
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_sell(product)
                        yield item
                    except Exception as e:
                        text = f'[offcn_sell]获取课程销量失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[offcn_sell]获取课程销量失败，error_msg:{e}')
                start = response.meta['start']
                start += 1
                url = f'http://19.offcn.com{response.meta["category"]}?page={start}'
                yield Request(url, headers=self.headers, meta={'category': response.meta['category'], 'start': start}, callback=self.parse1)
        except Exception as e:
            text = f'[offcn_sell]获取课程id失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[offcn_sell]获取课程id失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = str(product['id'])
        except:
            item['course_id'] = None
        try:
            item['sell'] = str(product['num'])
        except:
            item['sell'] = None
        item['com'] = 'offcn'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        #print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
