# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from myspider.settings import SCREENSHOT_URLS, SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT, SCREENSHOT_PATH
from myspider.items import ScreenshotItem
from myspider.utils import dingding_alert
import os
import time
import re
import logging
import scrapy
from scrapy import Request
# logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class KoolearnScreenshot(scrapy.Spider):
    name = 'koolearn_screenshot'
    allowed_domains = ['koolearn.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {}
    }

    def start_requests(self):
        url = 'https://www.koolearn.com/'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.koolearn.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }
        yield Request(url, headers=headers, callback=self.parse_data)

    def parse_data(self, response):
        for url in SCREENSHOT_URLS:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            #chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"')
            driver = webdriver.Chrome(options=chrome_options)
            try:
                driver.get(url)
                driver.set_window_size(SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT)
                # driver.maximize_window()
                try:
                    driver.find_element_by_xpath('//div[@class="close hunxinClose"]').click()
                except:
                    pass
                if 'cet' in url:
                    #type = driver.find_element_by_xpath('//a[@class="i_name fl"]').text
                    type = 'cet'
                else:
                    type = re.search('https://www.koolearn.com/ke/(.*)', url).group(1)
                file_name = type + time.strftime('%Y%m%d')
                driver.save_screenshot(SCREENSHOT_PATH + file_name + '.png')
                driver.quit()
                #os.system("ps aux | grep chrome |  awk '{print $2}' | xargs kill -9")
                item = self.save_data(type, url)
                yield item
                logger.info(f'{file_name}快照截取完成！')
            except Exception as e:
                driver.quit()
                text = f'[koolearn_screenshot]快照截取失败，error_msg:{e}, url:{url}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                dingding_alert(text)
                logger.error(f'[koolearn_screenshot]快照截取失败，error_msg:{e}')
                continue

    def save_data(self, type, url):
        item = ScreenshotItem()
        item['com'] = 'koolearn'
        item['type'] = type
        item['url'] = url
        item['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return item


if __name__ == '__main__':
    pass


