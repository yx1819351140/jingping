# Scrapy settings for myspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from cloghandler import ConcurrentRotatingFileHandler

BOT_NAME = 'myspider'

SPIDER_MODULES = ['myspider.spiders', 'myspider.spiders.youdao', 'myspider.spiders.koolearn', 'myspider.spiders.genshuixue', 'myspider.spiders.xiaoguo', 'myspider.spiders.orangevip', 'myspider.spiders.shanbay', 'myspider.spiders.fenbi', 'myspider.spiders.offcn']
NEWSPIDER_MODULE = 'myspider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'myspider (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# HTTPS_PROXY_URL = '111.227.41.153:4241'

# HTTP_PROXY_URL = '182.84.101.227:4236'

PROXY_MAX_FAILED_NUM = 10

DOWNLOAD_TIMEOUT = 3

# 5-25min
# GET_HTTPS_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
# GET_HTTP_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='

# 3-6小时
#GET_HTTPS_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=11&time=3&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
#GET_HTTP_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=3&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='

# 6-12小时
GET_HTTPS_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=11&time=4&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
GET_HTTP_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=4&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
# 最低有效时长, 根据获取ip类型而定
EFF_DURATION = 360  #MIN
#EFF_DURATION = 180
# EFF_DURATION = 5  #MIN

HBASE_HOST = 'kc-bigdata-03.bj02'
HBASE_TABLE_PREFIX = 'competitor'
HBASE_TABLE_PREFIX_SEPARATOR = ':'
BATCH_SIZE = 500

UNLIB_COURSE_INFO_TABLE = 'course_info'
UNLIB_COURSE_SCREENSHOT_INFO_TABLE = 'course_screenshot'
UNLIB_COURSE_TAG_INFO_TABLE = 'course_tag'
UNLIB_COURSE_SELL_INFO_TABLE = 'course_sell'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'myspider.middlewares.MyspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'myspider.middlewares.MyspiderDownloaderMiddleware': 543,
    'myspider.middlewares.Proxy_Middleware': 544,
    'myspider.middlewares.Headers_Middleware': 545,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #'myspider.pipelines.MyspiderPipeline': 300,
   'myspider.pipelines.CourseHbasePipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [400, 404, 500]
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=e35889206781f49bd3f8d91b35a64aa655b3a741c99fb38c5dd029d65a5d5cef'
TELL_PHONE = ['13069362502']

SPIDER_CONFIG = [
    {'spider_name': 'koolearn', 'tigger': 'cron', 'hour': 2, 'minute': 0, 'second': 0},
    {'spider_name': 'koolearn_add_id', 'tigger': 'interval', 'seconds': 0},
    {'spider_name': 'koolearn_del_id', 'tigger': 'interval', 'seconds': 0},
    {'spider_name': 'koolearn_tag', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'koolearn_screenshot', 'tigger': 'cron', 'hour': 6, 'minute': 0, 'second': 0},
    {'spider_name': 'youdao', 'tigger': 'cron', 'hour': 2, 'minute': 0, 'second': 0},
    {'spider_name': 'youdao_add_id', 'tigger': 'interval', 'seconds': 0},
    {'spider_name': 'youdao_del_id', 'tigger': 'interval', 'seconds': 0},
    {'spider_name': 'youdao_tag', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'genshuixue', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'genshuixue_sell', 'tigger': 'interval', 'seconds': 60},
    {'spider_name': 'xiaoguo', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'xiaoguo_sell', 'tigger': 'interval', 'seconds': 60},
    {'spider_name': 'spark', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'spark_sell', 'tigger': 'interval', 'seconds': 60},
    {'spider_name': 'orange_vip', 'tigger': 'cron', 'hour': 4, 'minute': 0, 'second': 0},
    {'spider_name': 'orangevip_sell', 'tigger': 'interval', 'seconds': 60},
    {'spider_name': 'shanbay', 'tigger': 'cron', 'hour': 6, 'minute': 0, 'second': 0},
    {'spider_name': 'fenbi', 'tigger': 'cron', 'hour': 6, 'minute': 0, 'second': 0},
    {'spider_name': 'fenbi_sell', 'tigger': 'interval', 'seconds': 60},
    {'spider_name': 'offcn', 'tigger': 'cron', 'hour': 6, 'minute': 0, 'second': 0},
    {'spider_name': 'offcn_sell', 'tigger': 'interval', 'seconds': 0},
]

#LOG_LEVEL = 'WARNING'

#today = datetime.datetime.now()
#LOG_FILE = f'log/{today.year}{today.month}{today.day}.log'

SCREENSHOT_URLS = ['https://www.koolearn.com/ke/kaoyan2', 'https://cet4.koolearn.com/zhuanti/cet/', 'https://www.koolearn.com/ke/kaoyan']

SCREENSHOT_WIDTH = 2000
SCREENSHOT_HEIGHT = 1000
SCREENSHOT_PATH = './screenshot/'

TAGS = ['四六级', '考研']

REDIS_URI_ = 'r-2zewk8zid8qy6hj58k.redis.rds.aliyuncs.com'
REDIS_PASSWORD_ = 'GYqOtg2ovIDLk67Sb3'

# kinit
KINIT = 'kinit -k -t /data1/app/kcrd.keytab kcrd/kc@KC.COM'
# delay time after execute 'kinit'
KINIT_DELAY = 1

base_path = os.path.dirname(os.path.abspath(__file__))
to_day = datetime.datetime.now()
log_file = 'warning.log'
log_file_path = os.path.join(base_path, 'log', log_file)
LOG_FILE_PATH = log_file_path
LOGS_FILE = base_path + '/log'
LOG_LEVEL = logging.WARNING
# 日志保留天数
LOG_DELETE_PERIOD = 7

logging.basicConfig(level=LOG_LEVEL,
                    filename=LOG_FILE_PATH,
                    filemode='a',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

handler = ConcurrentRotatingFileHandler(LOG_FILE_PATH, maxBytes=20971520, backupCount=10)

CATEGORYS = {
    '5bcd762eed7b1363d785208c': '考研',
    '5bc1b0c1ed7b137c6bf5f888': '四六级',
}
