# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import NotConfigured

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import random
import logging
import redis
import json
from retrying import retry
import requests
import time
from dingtalkchatbot.chatbot import DingtalkChatbot
from myspider.utils import dingding_alert
from twisted.internet.error import ConnectionRefusedError, TimeoutError

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class MyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Headers_Middleware:

    def process_request(self, request, spider):
        pass
        # url = request.url
        # if 'study.koolearn.com' in url:
        #     request.headers['Referer'] = 'http://www.koolearn.com/'


class Proxy_Middleware1:

    logger = logging.getLogger('Proxy_Middleware')

    def __init__(self, settings):
        self.settings = settings
        self.xiaoding = DingtalkChatbot(webhook=settings.get('WEBHOOK'))
        self.body_num = 0
        self.status_num = 0
        self.max_status_num = 50
        self.max_failed = settings.get('PROXY_MAX_FAILED_NUM')
        # self.redis = redis.Redis(host=settings.get('REDIS_URI_'), password=settings.get('REDIS_PASSWORD_'))
        self.redis = redis.Redis(db=1)
        self.eff_duration = settings.get('EFF_DURATION') * 60
        self.no_answer_id = open('./json_file/no_answer_id.txt', 'a', encoding='utf-8')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        try:
            proxy_index, https_proxy = self.get_proxys('https')
            # time.sleep(2.5)
            proxy_index, http_proxy = self.get_proxys('http')
            if 'https' in request.url:
                proxy = https_proxy
                request.meta['proxy'] = 'https://' + proxy
                request.meta['proxy_index'] = proxy_index
            else:
                proxy = http_proxy
                request.meta['proxy'] = 'http://' + proxy
                request.meta['proxy_index'] = proxy_index
            # print('http_proxy: ', http_proxy)
            # print('https_proxy: ', https_proxy)
            cur_proxy = request.meta.get('proxy')
            self.get_proxy_policy(cur_proxy, proxy_index, request)
        except Exception as e:
            spider.logger.error('代理错误：{}'.format(e))

    def process_response(self, request, response, spider):
        spider.logger.info(
            'crawed [{}] succeed，length [{}], id [{}]'.format(response.url, len(response.body), request.meta.get('id')))
        cur_proxy = request.meta.get('proxy')
        proxy_index = request.meta.get('proxy_index')
        spider.logger.info(f'https_proxys: {cur_proxy}')

        if response.status == 200:
            # self.set_proxys_status_num_zero(cur_proxy, proxy_index)
            self.status_num = 0

        # 判断是否被对方禁封
        if response.status > 400:
            # 给相应的ip失败次数 +1
            # self.set_proxys_status_num(cur_proxy, proxy_index)
            self.status_num += 1
            self.logger.warning(f'cur_proxy : {cur_proxy} request error, status: {response.status}')

            request = self.get_proxy_policy(cur_proxy, proxy_index, request)
            if request:
                return request
        # 状态码正常的时候，正常返回
        return response

    def process_exception(self, request, exception, spider):
        cur_proxy = request.meta.get('proxy')   # 取出当前代理
        proxy_index = request.meta.get('proxy_index')
        self.logger.warning(f'exception:{type(exception)}')

        if cur_proxy and isinstance(exception, (ConnectionRefusedError, TimeoutError)):
            self.logger.warning(f"exception :{exception}; cur_proxy: {cur_proxy}")
            # self.set_proxys_status_num(cur_proxy, proxy_index)
            self.status_num += 1

        request = self.get_proxy_policy(cur_proxy, proxy_index, request)
        if request:
            return request

    @retry(stop_max_attempt_number=3)
    def get_proxys(self, h):
        if h == 'https':
            proxy_url = self.settings.get('GET_HTTPS_URL')
        else:
            proxy_url = self.settings.get('GET_HTTP_URL')
        try:
            proxy_index = random.randint(0, 2)
            proxy_point = self.redis.lindex(f'{h}_proxy', proxy_index)
            if proxy_point:
                proxy = proxy_point.decode().split('_')[0]
                if self.check_duration(h, proxy_index):
                    self.redis.lrem(f'{h}_proxy', 1, proxy_point)
                    proxy = self._get_proxys(proxy_url)
                    self.redis.lpush(f'{h}_proxy', f'{proxy}_{time.time()}_0')
                    proxy_index = 0
            else:
                proxy = self._get_proxys(proxy_url)
                self.redis.lpush(f'{h}_proxy', f'{proxy}_{time.time()}_0')
                proxy_index = 0
            self.logger.info(f'Get proxy successful!! proxy: {proxy}')
            return proxy_index, proxy
        except Exception as e:
            self.xiaoding.send_text(msg=f'获取代理ip异常：【{e}】', at_mobiles=self.settings.get('TELL_PHONE'))
            self.logger.error(f'get proxy error: {e}, proxy_url: {proxy_url}')
            raise

    def _get_proxys(self, proxy_url):
        try:
            proxy = requests.get(proxy_url).text.strip()
            if 'code' in proxy:
                time.sleep(2.5)
                proxy = requests.get(proxy_url).text.strip()
            return proxy
        except Exception as e:
            self.xiaoding.send_text(msg=f'获取代理ip异常：【{e}】', at_mobiles=self.settings.get('TELL_PHONE'))
            self.logger.error(f'get proxy error: {e}, proxy_url: {proxy_url}')
            raise

    def set_proxys_status_num(self, cur_proxy, proxy_index):
        if cur_proxy:
            if 'https' in cur_proxy:
                proxy = cur_proxy.replace('https://', '')
                point = int(self.redis.lindex('https_proxy', proxy_index).decode().split('_')[2]) + 1
                get_time = self.redis.lindex('https_proxy', proxy_index).decode().split('_')[1]
                self.redis.lset('https_proxy', proxy_index, f'{proxy}_{get_time}_{point}')
            else:
                proxy = cur_proxy.replace('http://', '')
                point = int(self.redis.lindex('http_proxy', proxy_index).decode().split('_')[2]) + 1
                get_time = self.redis.lindex('http_proxy', proxy_index).decode().split('_')[1]
                self.redis.lset('http_proxy', proxy_index, f'{proxy}_{get_time}_{point}')

    def set_proxys_status_num_zero(self, cur_proxy, proxy_index):
        if cur_proxy:
            if 'https' in cur_proxy:
                proxy = cur_proxy.replace('https://', '')
                get_time = self.redis.lindex('https_proxy', proxy_index).decode().split('_')[1]
                self.redis.lset('https_proxy', proxy_index, f'{proxy}_{get_time}_0')
            else:
                proxy = cur_proxy.replace('http://', '')
                get_time = self.redis.lindex('http_proxy', proxy_index).decode().split('_')[1]
                self.redis.lset('http_proxy', proxy_index, f'{proxy}_{get_time}_0')

    def check_duration(self, cur_proxy, proxy_index):
        if 'https' in cur_proxy:
            return time.time() - float(self.redis.lindex('https_proxy', proxy_index).decode().split('_')[1]) > self.eff_duration
        else:
            return time.time() - float(self.redis.lindex('http_proxy', proxy_index).decode().split('_')[1]) > self.eff_duration

    def get_proxy_policy(self, cur_proxy, proxy_index, request):
        if 'https' in cur_proxy:
            proxy = cur_proxy.replace('https://', '')
            #  时效已到就删除此代理
            if self.check_duration(cur_proxy, proxy_index):
                new_proxy = self._get_proxys(self.settings.get('GET_HTTPS_URL'))
                self.redis.lrem('https_proxy', 0, self.redis.lindex('https_proxy', proxy_index))
                self.redis.lpush('https_proxy', f'{new_proxy}_{time.time()}_0')
                self.logger.info(f'del proxy {proxy}')
            # 如果池子里面的代理ip少于两个,并且失败次数达到最大请求次数，就往其中新增一个
            if ((self.redis.llen('https_proxy') < 2) and (self.status_num > self.max_status_num)) or self.redis.llen('https_proxy') == 0:
                new_proxy = self._get_proxys(self.settings.get('GET_HTTPS_URL'))
                self.redis.lpush('https_proxy', f'{new_proxy}_{time.time()}_0')
                self.status_num = 0
                del request.meta['proxy']
                return request
        else:
            proxy = cur_proxy.replace('http://', '')
            # 时效已到就删除此代理
            if self.check_duration(cur_proxy, proxy_index):
                new_proxy = self._get_proxys(self.settings.get('GET_HTTP_URL'))
                self.redis.lrem('http_proxy', 0, self.redis.lindex('http_proxy', proxy_index))
                self.redis.lpush('http_proxy', f'{new_proxy}_{time.time()}_0')
                self.logger.info(f'del proxy {proxy}')
            # 如果池子里面的代理ip少于两个,并且失败次数达到最大请求次数，就往其中新增一个
            if ((self.redis.llen('http_proxy') < 3) and (self.status_num > self.max_status_num)) or self.redis.llen('http_proxy') == 0:
                new_proxy = self._get_proxys(self.settings.get('GET_HTTP_URL'))
                self.redis.lpush('http_proxy', f'{new_proxy}_{time.time()}_0')
                self.status_num = 0
                del request.meta['proxy']
                return request


class Proxy_Middleware:

    logger = logging.getLogger('Proxy_Middleware')

    def __init__(self, settings):
        self.settings = settings
        self.xiaoding = DingtalkChatbot(webhook=settings.get('WEBHOOK'))
        self.max_failed = settings.get('PROXY_MAX_FAILED_NUM')
        self.redis = redis.Redis(host=settings.get('REDIS_URI_'), password=settings.get('REDIS_PASSWORD_'))
        #self.redis = redis.Redis(db=1)
        self.eff_duration = settings.get('EFF_DURATION') * 60
        self.no_answer_id = open('./json_file/no_answer_id.txt', 'a', encoding='utf-8')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        try:
            https_proxy = self.get_proxys('https')
            # time.sleep(2.5)
            http_proxy = self.get_proxys('http')
            if 'https' in request.url:
                proxy = https_proxy
                request.meta['proxy'] = 'https://' + proxy
            else:
                proxy = http_proxy
                request.meta['proxy'] = 'http://' + proxy
            # print('http_proxy: ', http_proxy)
            # print('https_proxy: ', https_proxy)
        except Exception as e:
            spider.logger.error('代理错误：{}'.format(e))

    def process_response(self, request, response, spider):
        spider.logger.info(
            'crawed [{}] succeed，length [{}], id [{}]'.format(response.url, len(response.body), request.meta.get('id')))
        cur_proxy = request.meta.get('proxy')
        spider.logger.info(f'https_proxys: {cur_proxy}')

        if response.status == 200:
            self.set_proxys_status_num_zero(cur_proxy)

        # 判断是否被对方禁封
        if response.status > 400:
            # 给相应的ip失败次数 +1
            self.set_proxys_status_num(cur_proxy)
            self.logger.warning(f'cur_proxy : {cur_proxy} request error, status: {response.status}')

            del request.meta['proxy']
            return request
        # 状态码正常的时候，正常返回
        return response

    def process_exception(self, request, exception, spider):
        cur_proxy = request.meta.get('proxy')  # 取出当前代理
        self.logger.warning(f'exception:{type(exception)}')

        if cur_proxy and isinstance(exception, (ConnectionRefusedError, TimeoutError)):
            self.logger.warning(f"exception :{exception}; cur_proxy: {cur_proxy}")
            self.set_proxys_status_num(cur_proxy)

        del request.meta['proxy']
        return request

    @retry(stop_max_attempt_number=3)
    def get_proxys(self, h):
        try:
            while True:
                proxy_point_list = self.redis.lrange(f'{h}_proxy', 0, -1)
                if proxy_point_list:
                    proxy_point = random.choice(proxy_point_list)
                    proxy_index = proxy_point_list.index(proxy_point)
                    if proxy_point:
                        proxy = proxy_point.decode().split('_')[0]
                        if self.check_duration(h, proxy_index):
                            self.redis.lrem(f'{h}_proxy', 1, proxy_point)
                            time.sleep(3)
                        else:
                            self.logger.info(f'Get proxy successful!! proxy: {proxy}')
                            return proxy
        except Exception as e:
            self.xiaoding.send_text(msg=f'获取代理ip异常：【{e}】', at_mobiles=self.settings.get('TELL_PHONE'))
            self.logger.error(f'get proxy error: {e}')
            raise

    def set_proxys_status_num(self, cur_proxy):
        if cur_proxy:
            if 'https' in cur_proxy:
                proxy = cur_proxy.replace('https://', '')
                for i in range(len(self.redis.lrange('https_proxy', 0, -1))):
                    if proxy in self.redis.lrange('https_proxy', 0, -1)[i].decode():
                        try:
                            point = int(self.redis.lindex('https_proxy', i).decode().split('_')[2])
                            if point <= 99:
                                point += 1
                            get_time = self.redis.lindex('https_proxy', i).decode().split('_')[1]
                            self.redis.lset('https_proxy', i, f'{proxy}_{get_time}_{point}')
                            break
                        except:
                            continue
            else:
                proxy = cur_proxy.replace('http://', '')
                for i in range(len(self.redis.lrange('http_proxy', 0, -1))):
                    if proxy in self.redis.lrange('http_proxy', 0, -1)[i].decode():
                        try:
                            point = int(self.redis.lindex('http_proxy', i).decode().split('_')[2])
                            if point <= 99:
                                point += 1
                            get_time = self.redis.lindex('http_proxy', i).decode().split('_')[1]
                            self.redis.lset('http_proxy', i, f'{proxy}_{get_time}_{point}')
                            break
                        except:
                            continue

    def set_proxys_status_num_zero(self, cur_proxy):
        if cur_proxy:
            if 'https' in cur_proxy:
                proxy = cur_proxy.replace('https://', '')
                for i in range(len(self.redis.lrange('https_proxy', 0, -1))):
                    if proxy in self.redis.lrange('https_proxy', 0, -1)[i].decode():
                        try:
                            self.redis.lset('https_proxy', i, f'{proxy}_{self.redis.lindex("https_proxy", i).decode().split("_")[1]}_0')
                            break
                        except:
                            continue
            else:
                proxy = cur_proxy.replace('http://', '')
                for i in range(len(self.redis.lrange('http_proxy', 0, -1))):
                    if proxy in self.redis.lrange('http_proxy', 0, -1)[i].decode():
                        try:
                            self.redis.lset('http_proxy', i, f'{proxy}_{self.redis.lindex("http_proxy", i).decode().split("_")[1]}_0')
                            break
                        except:
                            continue

    def check_duration(self, cur_proxy, proxy_index):
        if 'https' in cur_proxy:
            return time.time() - float(self.redis.lindex('https_proxy', proxy_index).decode().split('_')[1]) > self.eff_duration
        else:
            return time.time() - float(self.redis.lindex('http_proxy', proxy_index).decode().split('_')[1]) > self.eff_duration
