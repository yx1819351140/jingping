# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import json
import time
from myspider.utils import safe_json_loads, dingding_alert
from myspider.items import SellItem
from myspider.settings import REDIS_URI_, REDIS_PASSWORD_, handler
from scrapy import Request
from datetime import datetime
import redis
from scrapy_redis.spiders import RedisSpider

logger = logging.getLogger(__name__)


class KoolearnSellSpider(RedisSpider):
    name = 'koolearn_sell'
    allowed_domains = ['koolearn.com']
    logger.addHandler(handler)
    redis_key = 'koolearn:urls'
    # start_urls = ['https://www.koolearn.com/']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http://www.koolearn.com/'
        },
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'SCHEDULER_PERSIST': True,
        'REDIS_HOST': REDIS_URI_,
        'REDIS_PORT': 6379,
        'REDIS_PARAMS': {
            'password': REDIS_PASSWORD_
        },
        # 'REDIS_URL': 'redis://127.0.0.1:6379/1',
        'MYEXT_ENABLED': True,
        'IDLE_NUMBER': 180,
    }


    def parse(self, response):
        try:
            # print(res.text)
            dict_data = safe_json_loads(response.text)
            if not dict_data['data']:
                return None
            else:
                sell = dict_data['data'][0]['buyNumber']
                course_id = dict_data['data'][0]['productId']

                item = SellItem()
                item['com'] = 'koolearn'
                item['course_id'] = str(course_id)
                item['sell'] = str(sell)
                item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # print(json.dumps(dict(item)))
                yield item
        except Exception as e:
            text = f'[koolearn_sell]销量数据获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn_sell]销量数据获取失败,res:{response.text},error_msg:{e}')

