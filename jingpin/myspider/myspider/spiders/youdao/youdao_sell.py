# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import json
import time
from myspider.utils import safe_json_loads, get_end_time, dingding_alert
from myspider.items import SellItem
from myspider.settings import REDIS_URI_, REDIS_PASSWORD_, handler
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
import redis

logger = logging.getLogger(__name__)


class YoudaoSellSpider(RedisSpider):
    name = 'youdao_sell'
    allowed_domains = ['youdao.com']
    redis_key = 'youdao:urls'
    logger.addHandler(handler)
    # start_urls = ['https://ke.youdao.com/']
    custom_settings = {
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
        dict_data = safe_json_loads(response.text)
        try:
            try:
                sell = dict_data['userNum']
            except:
                sell = None
            try:
                course_id = dict_data['itemId']
            except:
                return


            item = SellItem()
            item['com'] = 'youdao'
            item['course_id'] = str(course_id)
            item['sell'] = str(sell)
            item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(json.dumps(dict(item)))
            yield item
        except Exception as e:
            text = f'[youdao_sell]销量数据获取失败,error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao_sell]销量数据获取失败,res:{response.text},error_msg:{e}')


