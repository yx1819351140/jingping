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


class KoolearnSpider(scrapy.Spider):
    name = 'koolearn'
    allowed_domains = ['koolearn.com']
    logger.addHandler(handler)
    # start_urls = ['https://www.koolearn.com/']

    def start_requests(self):
        url = 'https://daxue.koolearn.com/'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'daxue.koolearn.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }
        yield Request(url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        try:
            product_id_list = []
            #url_list = response.xpath('//div[@class="p-class-wrap"]/ul/li/a/@href').extract()
            url_list = response.xpath('//*[@id="__next"]/div/div[4]/div[2]/a/@href').extract()
            for url in url_list:
                result = re.search('.*[0-9]_(.*).html', url)
                if result:
                    product_id_list.append(int(result.group(1)))
            if product_id_list:
                for i in range(max(product_id_list) + 10000):
                #for i in [89590]:
                    try:
                        yield Request(url=f'https://gnitem.koolearn.com/api/productDetail/common-by-productid?productId={i}&isPreView=1&pageType=2', meta={'product_id': i}, callback=self.parse1, dont_filter=True)
                    except:
                        continue
            else:
                text = f'[koolearn]主页获取最新id失败，err_msg: get_product_id failed\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[koolearn]主页获取最新id失败，res: {response.text}')
        except Exception as e:
            text = f'[koolearn]主页获取最新id失败，error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn]主页获取最新id失败，error_msg:{e}')

    def parse1(self, response):
        try:
            data = safe_json_loads(response.text)
            code = data['code']
            if code == 0:
                item = self.save_data(response.meta['product_id'], data)
                yield item
            elif code == 10005:
                for i in [2, 19, 20]:
                    url = f'https://m.koolearn.com/product/c_{i}_{response.meta["product_id"]}.html'
                    headers = {
                        'Host': 'm.koolearn.com',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv; Koolearn; kooup/4.13.2; B/160/30000504) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045410 Mobile Safari/537.36',
                        'Sec-Fetch-Mode': 'navigate',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'X-Requested-With': 'com.kooup.student',
                        'Sec-Fetch-Site': 'same-site',
                        'Referer': 'https://cet4.koolearn.com/zhuanti/cet_wap/?scene=appjgq',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    }
                    yield Request(url=url, headers=headers, meta={'course_id': response.meta["product_id"], 'i': i}, callback=self.save_data1, dont_filter=True)
            else:
                logger.info(f'[koolearn]课程数据获取失败，error_msg:{data["msg"]},error_id:{response.meta["product_id"]}')
        except Exception as e:
            text = f'[koolearn]课程详情接口请求异常,error_msg:{e},course_id:{response.meta["product_id"]}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn]课程详情接口请求异常，error_res:{response.text},error_msg:{e},error_id:{response.meta["product_id"]}')

    def save_data(self, product_id, data):
        item = CourseItem()
        try:
            course_id = data['data']['headVo']['productId']
        except:
            course_id = product_id
        try:
            title = data['data']['headVo']['productName']
        except:
            title = None
        try:
            end_time = data['data']['headVo']['expirationDate']
        except:
            end_time = None
        try:
            sell = data['data']['headVo']['saleCount']
        except:
            sell = None
        try:
            originalPrice = data['data']['headVo']['originalPrice']
        except:
            originalPrice = 0
        try:
            currentPrice = data['data']['headVo']['currentPrice']
        except:
            currentPrice = 0
        try:
            teacher = ''
            teacher_list = data['data']['headVo']['teacherList']
            for i in teacher_list:
                teacher = teacher + i + ','
        except:
            teacher = None
        try:
            course_hour = data['data']['headVo']['classHours']
        except:
            course_hour = None
        try:
            course_service = data['data']['headVo']['subTitle']
        except:
            course_service = None

        item['course_id'] = str(course_id)
        item['url'] = 'https://www.koolearn.com/guonei/product/c_2_{}.html'.format(product_id)
        item['title'] = title
        item['start_time'] = None
        item['end_time'] = end_time
        item['sell'] = str(sell)
        item['original_price'] = str(originalPrice)
        item['current_price'] = str(currentPrice)
        item['teacher'] = teacher
        item['student'] = None
        item['course_hour'] = course_hour
        item['course_format'] = None
        item['course_service'] = course_service
        item['course_info'] = None
        item['com'] = 'koolearn'
        item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        return item

    def save_data1(self, response):
        if '页面飞走了' in response.text:
            return
        try:
            title = response.xpath('//*[@class="title"]/text()').extract_first()
        except:
            title = None
        try:
            start_time = response.xpath('//*[contains(text(),"开课时间")]/text()').extract_first().replace('开课时间：', '').strip()
        except:
            start_time = None
        try:
            end_time = response.xpath('//*[contains(text(),"有效期")]/text()').extract_first().replace('课程', '').replace('有效期：', '').strip()
            if start_time:
                end_time = get_end_time(start_time, end_time)
        except:
            end_time = None
        try:
            original_price = None
            current_price = None
            price_list = response.xpath('//*[@class="money"]//text()').extract()
            for temp in price_list:
                if not temp.strip() or '¥' in temp:
                    continue
                current_price = temp
                break
            for temp in price_list[::-1]:
                if not temp.strip() or '¥' in temp:
                    continue
                original_price = temp
                break
        except:
            original_price = None
            current_price = None
        try:
            student = response.xpath('//li[contains(text(),"适合学员")]/text()').extract_first().replace('适合学员：', '')
        except:
            student = None
        # try:
        #     try:
        #         sell = response.xpath('//*[contains(text(),"已报人数")]/text()').extract_first().replace('已报人数：', '').replace('人', '')
        #     except:
        #         sell = response.xpath('//div[@class="status"]/span//text()').extract()[-3]
        #         if '人' in sell:
        #             sell = sell.replace('人', '')
        #         else:
        #             sell = None
        # except:
        #     sell = None
        # try:
        #     teacher = response.xpath('//li[contains(text(),"主讲")]/text()').extract_first().replace('主讲：', '').replace('主讲团队：', '').split('、')
        # except:
        #     teacher = self.get_teacher(response.meta["course_id"])
        # try:
        #     if not start_time:
        #         course_hour = response.xpath('//*[contains(text(),"课时")]/text()').extract_first().replace('课时：', '').replace('课时总量：', '')
        #     else:
        #         course_hour = response.xpath('//*[contains(text(),"课时")]/text()').extract()[1].replace('课时：', '').replace('课时总量：', '')
        # except:
        #     course_hour = None
        try:
            course_format = response.xpath('//li[contains(text(),"课程形式")]/text()').extract_first().replace('课程形式：', '')
        except:
            course_format = None
        try:
            course_service = response.xpath('//li[contains(text(),"课程服务")]/text()').extract_first().replace('课程服务：', '')
        except:
            course_service = None
        try:
            course_info = response.xpath('//li[contains(text(),"课程资料")]/text()').extract_first().replace('课程资料：', '').split('、')
        except:
            course_info = None
        try:
            sell, teacher, course_hour = self.get_data(response.meta["course_id"])
        except:
            sell = teacher = course_hour = None

        item = CourseItem()
        item['course_id'] = str(response.meta['course_id'])
        item['url'] = f'https://www.koolearn.com/product/c_{response.meta["i"]}_{response.meta["course_id"]}.html'
        item['title'] = title
        item['start_time'] = start_time
        item['end_time'] = end_time
        item['sell'] = str(sell)
        item['original_price'] = str(original_price)
        item['current_price'] = str(current_price)
        item['teacher'] = teacher
        item['student'] = student
        item['course_hour'] = course_hour
        item['course_format'] = course_format
        item['course_service'] = course_service
        item['course_info'] = course_info
        item['com'] = 'koolearn'
        item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print(json.dumps(dict(item)))
        yield item

    def get_data(self, product_id):
        headers = {
            'Host': 'study.koolearn.com',
            'User-Agent': 'curl/7.71.1',
            'Accept': '*/*',
            'Referer': 'http://www.koolearn.com/',
            'Content-Type': 'application/json;charset=UTF-8',
            'Connection': 'keep-alive',
            'Vary': 'Accept-Encoding',
            'X-Cache': 'bypass'
        }
        res = requests.get(f'http://study.koolearn.com/api/product/?productIds={product_id}', headers=headers)
        try:
            # print(res.text)
            dict_data = safe_json_loads(res.text)
            if not dict_data['data']:
                return None
            else:
                sell = dict_data['data'][0]['buyNumber']
                course_hour = dict_data['data'][0]['classHours']
                teacher = ''
                for temp in dict_data['data'][0]['teachers']:
                    try:
                        teacher = teacher + temp['teacherName'] + ','
                    except:
                        continue
                return sell, teacher, course_hour
        except Exception as e:
            text = f'[koolearn]销量数据获取失败,course_id:{product_id},error_msg:{e}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
            dingding_alert(text)
            logger.error(f'[koolearn]销量数据获取失败,course_id:{product_id},res:{res.text},error_msg:{e}')


if __name__ == '__main__':
    pass
