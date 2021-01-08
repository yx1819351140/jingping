# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()))
import logging
import json
import hashlib
import datetime
import time
import requests
import redis
from myspider.settings import WEBHOOK, REDIS_URI_, REDIS_PASSWORD_, GET_HTTP_URL, GET_HTTPS_URL

logger = logging.getLogger(__name__)


def del_log():
    today = datetime.datetime.now()
    LOG_FILE = f'{today.year}{today.month}{today.day}.log'
    path = os.getcwd() + '/log/'
    for file_name in os.listdir(path):
        if file_name != LOG_FILE:
            os.remove(path + file_name)


def safe_json_loads(string):
    try:
        return json.loads(string)
    except:
        return {}


def get_end_time(start_time, end_time):
    try:
        if '天' in end_time:
            day = int(end_time.replace('天', ''))
            time_array = time.strptime(start_time + ' 0:0:0', '%Y-%m-%d %H:%M:%S')
            time_stamp = int(time.mktime(time_array))
            date_array = datetime.datetime.utcfromtimestamp(time_stamp)
            day_ago = date_array + datetime.timedelta(days=day)
            result = day_ago.strftime("%Y-%m-%d")
            return result
        else:
            return end_time
    except:
        return end_time


def get_strp_time(time_stamp):
    try:
        time_array = time.localtime(time_stamp)
        strp_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return strp_time
    except:
        return time_stamp


def write_start_urls():
    conn = redis.Redis(host=REDIS_URI_, password=REDIS_PASSWORD_)
    data_set = conn.smembers('koolearn_course_id')
    length = conn.llen('koolearn:urls')
    if not length: 
        for data in data_set:
            try:
                conn.lpush('koolearn:urls', f'http://study.koolearn.com/api/product/?productIds={data.decode()}')
            except:
                continue
    
    data_set = conn.smembers('youdao_course_id')
    length = conn.llen('youdao:urls')
    if not length:
        for data in data_set:
            try:
                conn.lpush('youdao:urls', f'https://ke.youdao.com/course/api/detail.json?courseId={data.decode()}')
            except:
                continue


def get_data(basic_course_type, exam_season_ids, squad_type_id, subject_info_id):
    basic_data_dict = {
        'basicCourseType': basic_course_type,
        'displayName': "",
        'examSeasonIds': exam_season_ids,
        # 'orderBy': "firstOnlineTime",
        'orderBy': "buyNumber",
        'pageNo': '1',
        'pageSize': '15',
        'squadtypeId': squad_type_id,
        'subjectInfoId': subject_info_id,
    }
    return basic_data_dict


def get_url(grade, page):
    timestamp = str(int(float(time.time()) * 1000))
    i = 'sign2109516695449774081.0.01c9366c797884134a3606c95d2ceba8e' + timestamp + 'sign'
    sign = hashlib.md5(str(i).encode('utf-8')).hexdigest()
    url = f'https://api2.sparke.cn/netcourse/search?grade={grade}&page={page}&step=15&pvalue=%7B%22appId%22:%22210951669544977408%22,%22v%22:%221.0.0%22,%22os%22:%22web%22,%22terminalType%22:%223%22,%22timestamp%22:{timestamp},%22terminalid%22:%221c9366c797884134a3606c95d2ceba8e%22,%22appSign%22:%22{sign}%22,%22token%22:%22%22,%22userId%22:%22%22,%22browserId%22:%22%22%7D'
    return url


def dingding_alert(text):
    data = {
        "msgtype": "text",
        "text": {
            "content": text
        },
        "at": {
            "atMobiles": [
                "13069362502",
            ],
            "isAtAll": False
        }
    }
    url = WEBHOOK
    headers = {
            'User-Agent': 'curl/7.71.1',
            'Accept': '*/*',
            'Referer': 'http://www.koolearn.com/',
            'Content-Type': 'application/json;charset=UTF-8',
            'Connection': 'keep-alive',
            'Vary': 'Accept-Encoding',
            'X-Cache': 'bypass'
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))


def check_proxy():
    conn = redis.Redis(host=REDIS_URI_, password=REDIS_PASSWORD_)
    # conn = redis.Redis(db=1)
    is_break = False
    cur_time = None
    fail_count = 2
    while True:
        for h in ['http', 'https']:
            length = conn.llen(f'{h}_proxy')
            if length < 3:
                proxy_list = conn.lrange(f'{h}_proxy', 0, -1)
                point = 0
                for i in proxy_list:
                    point += int(i.decode().split('_')[2])
                if point >= (length * 100):
                    if h == 'http':
                        proxy_url = GET_HTTP_URL
                    else:
                        proxy_url = GET_HTTPS_URL
                    proxy = requests.get(proxy_url).text.strip()
                    # print(proxy)
                    if 'code' in proxy:
                        if '再试' in proxy:
                            time.sleep(2.5)
                            proxy = requests.get(proxy_url).text.strip()
                            conn.rpush(f'{h}_proxy', f'{proxy}_{time.time()}_0')
                        elif '余额' in proxy:
                            text = f'[get_proxy]代理ip获取失败,error_msg:{proxy}\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.error(f'[get_proxy]代理ip获取失败,res:{proxy}')
                            is_break = True
                    else:
                        conn.rpush(f'{h}_proxy', f'{proxy}_{time.time()}_0')
            if length == 3:
                proxy_list = conn.lrange(f'{h}_proxy', 0, - 1)
                point = 0
                for i in proxy_list:
                    point += int(i.decode().split('_')[2])
                if point >= 300:
                    if not cur_time:
                        cur_time = time.time()
                        is_warning = False
                        for proxy in proxy_list:
                            try:
                                res = requests.get(f'{h}://www.baidu.com', proxies={h: f'{h}://{proxy.decode().split("_")[0]}'}, timeout=5)
                                if res.status_code == 200:
                                    is_warning = True
                            except:
                                pass
                        if not is_warning:
                            text = f'[get_proxy]所有ip第1次失效\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.warning(f'[get_proxy]所有ip第1次失效')
                    elif time.time() - cur_time > 60:
                        is_warning = False
                        for proxy in proxy_list:
                            try:
                                res = requests.get(f'{h}://www.baidu.com', proxies={h: f'{h}://{proxy.decode().split("_")[0]}'}, timeout=5)
                                if res.status_code == 200:
                                    is_warning = True
                            except:
                                pass
                        if not is_warning:
                            text = f'[get_proxy]所有ip第{fail_count}次失效\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.error(f'[get_proxy]所有ip第{fail_count}次失效')
                        else:
                            text = f'[get_proxy]ip池恢复\n{time.strftime("%Y-%m-%d %H:%M:%S")}'
                            dingding_alert(text)
                            logger.info(f'[get_proxy]ip池恢复')
                            fail_count = 0
                        cur_time = time.time()
                        fail_count += 1
        if is_break:
            break


if __name__ == '__main__':
    pass
    check_proxy()
