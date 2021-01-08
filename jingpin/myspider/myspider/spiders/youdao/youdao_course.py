# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import requests
import json
import time
from myspider.utils import safe_json_loads, get_end_time, dingding_alert
from myspider.settings import handler
from myspider.items import CourseItem
from scrapy import Request
from datetime import datetime

logger = logging.getLogger(__name__)


class YoudaoSpider(scrapy.Spider):
    name = 'youdao'
    allowed_domains = ['youdao.com']
    logger.addHandler(handler)
    # start_urls = ['https://ke.youdao.com/']

    def start_requests(self):
        url = 'https://ke.youdao.com/'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'ke.youdao.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': None,
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }
        yield Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            product_id_list = []
            url_list = response.xpath('//*[contains(text(), "热门课程")]/following-sibling::div[1]/a/@href').extract()
            for url in url_list:
                result = re.search('https:\/\/ke\.youdao\.com\/course\/detail\/([0-9]*)\?.*', url)
                if result:
                    product_id_list.append(int(result.group(1)))
            if product_id_list:
                for i in range(max(product_id_list) + 10000):
                # for i in ['73668']:
                    try:
                        yield Request(
                            url=f'https://ke.youdao.com/course/detail/{i}', headers=self.headers, meta={'product_id': i}, callback=self.parse1, dont_filter=True)
                    except:
                        continue
            else:
                text = f'[youdao]主页获取最新id失败，err_msg: get_product_id failed\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[youdao]主页获取最新id失败，res:{response.text}')
        except Exception as e:
            text = f'[youdao]主页获取最新id失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[youdao]主页获取最新id失败，error_msg:{e}')

    def parse1(self, response):
        if '课程不存在' in response.text:
            logger.info(f'[youdao]课程获取失败，该课程不存在，course_id:{response.meta["product_id"]}')
            return
        try:
            title = response.xpath('//*[@class="info info-without-video"]/h1/text()').extract_first()
        except:
            title = None
        try:
            start_time = response.xpath('//*[contains(text(),"开课时间")]/text()').extract_first().replace('开课时间：', '').strip()
        except:
            start_time = None
        try:
            end_time = response.xpath('//*[contains(text(),"有效期")]/text()').extract_first().replace('有效期至：', '').strip()
            if start_time:
                end_time = get_end_time(start_time, end_time)
        except:
            end_time = None
        try:
            sell = response.xpath('//*[@class="course-status"]/em/text()').extract_first()
        except:
            sell = None
        try:
            current_price = response.xpath('//*[@class="price"]/text()').extract_first().strip()
        except:
            current_price = None
        try:
            original_price = response.xpath('//*[@class="market-price"]/text()').extract_first().replace('¥', '').strip()
        except:
            original_price = current_price
        try:
            teacher = response.xpath('//*[contains(text(),"主讲")]/text()').extract_first().replace('主讲老师：', '')
        except:
            teacher = None
        try:
            course_hour = response.xpath('//*[contains(text(),"课时数量")]/text()').extract_first().replace('课时数量：', '')
        except:
            course_hour = None

        item = CourseItem()
        item['course_id'] = str(response.meta['product_id'])
        item['url'] = f'https://ke.youdao.com/course/detail/{response.meta["product_id"]}'
        item['title'] = title
        item['start_time'] = start_time
        item['end_time'] = end_time
        item['sell'] = str(sell)
        item['original_price'] = str(original_price)
        item['current_price'] = str(current_price)
        item['teacher'] = teacher
        item['student'] = None
        item['course_hour'] = course_hour
        item['course_format'] = None
        item['course_service'] = None
        item['course_info'] = None
        item['com'] = 'youdao'
        item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        with open('youdao_course.json', 'a') as f:
            f.write(json.dumps(dict(item))+'\n')
        yield item
