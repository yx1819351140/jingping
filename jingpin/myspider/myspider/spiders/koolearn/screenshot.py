# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import logging

logger = logging.getLogger(__name__)

SCREENSHOT_URLS = ['https://www.koolearn.com/ke/kaoyan2', 'https://cet4.koolearn.com/zhuanti/cet/', 'https://www.koolearn.com/ke/kaoyan']
SCREENSHOT_WIDTH = 2000
SCREENSHOT_HEIGHT = 1000
SCREENSHOT_PATH = './screenshot/'


def get_data():
    for url in SCREENSHOT_URLS:
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            driver.set_window_size(SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT)
            # driver.maximize_window()
            try:
                driver.find_element_by_xpath('//div[@class="close hunxinClose"]').click()
            except:
                pass
            if 'cet' in url:
                type = driver.find_element_by_xpath('//a[@class="i_name fl"]').text
            else:
                type = driver.find_element_by_xpath('//a[@class="fl tab cur"]').text
            file_name = type + time.strftime('%Y%m%d')
            driver.save_screenshot(SCREENSHOT_PATH + file_name + '.png')
            driver.quit()
            logger.info(f'{file_name}快照截取完成！')
        except Exception as e:
            logger.error(f'[koolearn_screenshot]快照截取失败，error_msg:{e}')
            continue


if __name__ == '__main__':
    get_data()

