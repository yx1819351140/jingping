import requests
import os
#res = requests.get('https://daxue.koolearn.com', proxies={'https': 'https://114.99.5.19:4226'})
#res = requests.get('https://ke.youdao.com/course/api/detail.json?courseId=78748', proxies={'https': 'https://36.57.78.116:4248'})
#res = requests.get('https://www.baidu.com', proxies={'https': 'https://114.99.5.19:4226'}, verify=False)
#res = requests.get('http://ke.youdao.com/course/api/detail.json?courseId=78748', proxies={'http': 'http://115.59.244.159:4256'})
#res = requests.get('http://study.koolearn.com/api/product/?productIds=85598', headers={'Referer': 'http://www.koolearn.com/'}, proxies={'http': 'http://115.59.244.159:4256'})
#res = requests.get('https://daxue.koolearn.com')
res = requests.get('https://ke.youdao.com/course3/api/vertical2?tag=2248', proxies={'https': 'https://36.57.78.116:4248'})
print(res.text)
