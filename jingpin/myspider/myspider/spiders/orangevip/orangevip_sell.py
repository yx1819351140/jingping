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


class OrangevipSellSpider(scrapy.Spider):
    name = 'orangevip_sell'
    allowed_domains = ['orangevip.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        try:
            url = 'https://www.orangevip.com/index'
            yield Request(url, callback=self.parse)
        except Exception as e:
            text = f'[orangevip_sell]访问首页失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip_sell]访问首页失败，error_msg:{e}')

    def parse(self, response):
        try:
            page = 1
            category_list = response.xpath('//a[@class="categoryItem"]/@href').extract()
            for category in category_list:
                url = f'https://www.orangevip.com{category}_p{page}'
                yield Request(url=url, meta={'page': page, 'category': category}, callback=self.parse1)
        except Exception as e:
            text = f'[orangevip_sell]获取数据url失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip_sell]获取数据url失败，error_msg:{e}')

    def parse1(self, response):
        try:
            json_data = re.search('window\.__NUXT__=(.*);</script>', response.text).group(1)
            dict_data = safe_json_loads(json_data)
            try:
                product_list = dict_data['data'][0]['currentCourseData']
            except:
                product_list = None
            if product_list:
                for product in product_list:
                    try:
                        item = self.parse_course_sell(product)
                        yield item
                    except Exception as e:
                        text = f'[orangevip_sell]获取实时销量失败，res:{product}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                        dingding_alert(text)
                        logger.error(f'[orangevip_sell]获取实时销量失败，error_msg:{e}')
                        continue
                page = response.meta['page'] + 1
                url = f'https://www.orangevip.com{response.meta["category"]}_p{page}'
                yield Request(url=url, meta={'page': page, 'category': response.meta["category"]}, callback=self.parse)
        except Exception as e:
            text = f'[orangevip_sell]获取课程信息失败，res:{response.text}, error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[orangevip_sell]获取课程信息失败，error_msg:{e}')

    def parse_course_sell(self, product):
        item = SellItem()
        try:
            item['course_id'] = str(product['productId'])
        except:
            item['course_id'] = None
        try:
            item['sell'] = str(product['selledCount'])
        except:
            item['sell'] = None
        item['com'] = 'orangevip'
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item


if __name__ == '__main__':
    pass
