# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.getcwd()))
import time
import logging
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from settings import SPIDER_CONFIG
from utils import write_start_urls, del_log


logger = logging.getLogger(__name__)

sched = BlockingScheduler()


def start_scrapy(spider):
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['scrapy', 'crawl', spider])


def create_job():
    for spider in SPIDER_CONFIG:
        if spider['tigger'] == 'interval':
            seconds = spider['seconds']
            sched.add_job(start_scrapy, spider['tigger'], seconds=seconds, args=[spider["spider_name"],])
        elif spider['tigger'] == 'cron':
            hour = spider.get('hour', None)
            minute = spider.get('minute', None)
            second = spider.get('second', None)
            sched.add_job(start_scrapy, spider['tigger'], hour=hour, minute=minute, second=second, args=[spider["spider_name"],])
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass


def add_job(func, tigger, **kwargs):
    sched.add_job(func, tigger, **kwargs)
    sched.start()


if __name__ == '__main__':
    pass
    create_job()
    #add_job(start_scrapy, 'cron', hour=2, minute=0, second=0)
    #add_job(start_scrapy, 'interval', seconds=0)
    #add_job(write_start_urls, 'interval', seconds=0)
