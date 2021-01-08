import requests
url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=11&time=3&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
res = requests.get(url)
print(res.text)

