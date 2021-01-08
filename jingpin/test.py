from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"')
driver = webdriver.Chrome(options=chrome_options)
#url = 'https://cet4.koolearn.com/zhuanti/cet/'
url = 'https://www.koolearn.com/ke/kaoyan2'
driver.get(url)
driver.set_window_size(2000, 1000)
driver.save_screenshot('kaoyan2.png')
# driver.maximize_window()
#try:
#    driver.find_element_by_xpath('//div[@class="close hunxinClose"]').click()
#except:
#    pass
#if 'cet' in url:
#    type = driver.find_element_by_xpath('//a[@class="i_name fl"]').text
#else:
#    type = re.search('https://www.koolearn.com/ke/(.*)', url).group(1)
#print(type)
