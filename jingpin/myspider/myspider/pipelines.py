# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from hashlib import md5
import os
import time
from itemadapter import ItemAdapter
import logging
import happybase
from happybase_kerberos_patch import KerberosConnection, KerberosConnectionPool
from scrapy.utils.python import to_bytes
from myspider.settings import HBASE_TABLE_PREFIX, HBASE_TABLE_PREFIX_SEPARATOR, HBASE_HOST, handler

from myspider.items import CourseItem, ScreenshotItem, SellItem, TagItem


class MyspiderPipeline:
    def process_item(self, item, spider):
        return item


class CourseHbasePipeline:
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    unlib_course_info_table_list = []
    unlib_course_screenshot_info_table_list = []
    unlib_course_tag_info_table_list = []
    unlib_course_sell_info_table_list = []

    def __init__(self, settings):
        os.system(settings.get('KINIT'))
        time.sleep(settings.get('KINIT_DELAY'))
        # connection database
        # self.connect = KerberosConnection(settings.get('HBASE_HOST'), protocol='compact', use_kerberos=True, table_prefix=settings.get('HBASE_TABLE_PREFIX'), table_prefix_separator=settings.get('HBASE_TABLE_PREFIX_SEPARATOR'), sasl_service_name='hbase')
        # self.connect = happybase.Connection(host=settings.get('HBASE_HOST'), table_prefix=settings.get('HBASE_TABLE_PREFIX'), table_prefix_separator=settings.get('HBASE_TABLE_PREFIX_SEPARATOR'))
        # self.pool = KerberosConnectionPool(size=3, host=settings.get('HBASE_HOST'), table_prefix=settings.get('HBASE_TABLE_PREFIX'), table_prefix_separator=settings.get('HBASE_TABLE_PREFIX_SEPARATOR'), protocol='compact', use_kerberos=True)
        self.logger.info("Database linked successfully!")
        # self.tables = set(self.connect.tables())
        self.batch_size = settings.get('BATCH_SIZE')
        self.unlib_course_info_table_ = to_bytes(settings.get('UNLIB_COURSE_INFO_TABLE'))
        # if self.unlib_course_info_table_ not in self.tables:
        #     schema = {
        #         'info': dict(max_versions=3)
        #     }
        #     self.connect.create_table(self.unlib_course_info_table_, schema)
        #     self.logger.info('create table : {} successful'.format(self.unlib_course_info_table_))
        # self.unlib_course_info_table = self.connect.table(self.unlib_course_info_table_)
        #
        self.unlib_course_screenshot_info_table_ = to_bytes(settings.get('UNLIB_COURSE_SCREENSHOT_INFO_TABLE'))
        # if self.unlib_course_screenshot_info_table_ not in self.tables:
        #     schema = {
        #         'info': dict(max_versions=3)
        #     }
        #     self.connect.create_table(self.unlib_course_screenshot_info_table_, schema)
        #     self.logger.info('create table : {} successful'.format(self.unlib_course_screenshot_info_table_))
        # self.unlib_course_screenshot_info_table = self.connect.table(self.unlib_course_screenshot_info_table_)
        #
        self.unlib_course_tag_info_table_ = to_bytes(settings.get('UNLIB_COURSE_TAG_INFO_TABLE'))
        # if self.unlib_course_tag_info_table_ not in self.tables:
        #     schema = {
        #         'info': dict(max_versions=3)
        #     }
        #     self.connect.create_table(self.unlib_course_tag_info_table_, schema)
        #     self.logger.info('create table : {} successful'.format(self.unlib_course_tag_info_table_))
        # self.unlib_course_tag_info_table = self.connect.table(self.unlib_course_tag_info_table_)
        #

        #self.unlib_course_sell_info_table_ = to_bytes(settings.get('UNLIB_COURSE_SELL_INFO_TABLE'))
        # if self.unlib_course_sell_info_table_ not in self.tables:
        #     schema = {
        #         'info': dict(max_versions=3)
        #     }
        #     self.connect.create_table(self.unlib_course_sell_info_table_, schema)
        #     self.logger.info('create table : {} successful'.format(self.unlib_course_sell_info_table_))
        # self.unlib_course_sell_info_table = self.connect.table(self.unlib_course_sell_info_table_)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):
        pass
        # redis_host = spider.settings.get('REDIS_HOST')
        # redis_port = spider.settings.get('REDIS_PORT')
        # redis_pwd = spider.settings.get('REDIS_PARAMS')
        # graduate_k = spider.settings.get('GRADUATE_START_URL')[0]
        # graduate_v = spider.settings.get('GRADUATE_START_URL')[1]
        # self.redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_pwd['password'])
        # self.logger.info('REDIS: redis database linked successfully!')
        # fp = request_fingerprint(graduate_v)
        # self.redis_conn.srem(spider.name + ":dupefilter", fp)
        # self.redis_conn.sadd(graduate_k, *graduate_v)


    def process_item(self, item, spider):
        if isinstance(item, CourseItem):
            row_key = time.strftime('%Y%m%d') + '_' + self.to_md5(item)
            item_data = {'info:' + k: v for k, v in item.items()}
            self.batch_send(self.unlib_course_info_table_list, self.unlib_course_info_table_,
                            row_key,
                            item_data, self.batch_size)
            # self.logger.info('SpecialtyItem save - row_key: {}, item_data: {}'.format(row_key, item_data))

        if isinstance(item, ScreenshotItem):
            row_key = time.strftime('%Y%m%d') + '_' + self.to_md5(item)
            item_data = {'info:' + k: v for k, v in item.items()}
            self.batch_send(self.unlib_course_screenshot_info_table_list, self.unlib_course_screenshot_info_table_, row_key,
                            item_data,
                            self.batch_size)
            # self.logger.info('NewPublishItem save - row_key: {}, item_data: {}'.format(row_key, item_data))

        if isinstance(item, TagItem):
            row_key = time.strftime('%Y%m%d') + '_' + self.to_md5(item)
            item_data = {'info:' + k: v for k, v in item.items()}
            self.batch_send(self.unlib_course_tag_info_table_list, self.unlib_course_tag_info_table_, row_key, item_data,
                            self.batch_size)
            # self.logger.info('AdjustInfoItem save - row_key: {}, item_data: {}'.format(row_key, item_data))

        if isinstance(item, SellItem):
            row_key = time.strftime('%Y%m%d') + '_' + self.to_md5(item)
            item_data = {'info:' + k: v for k, v in item.items()}
            tab_name = f'course_sell_{time.strftime("%Y%m%d")}'
            self.batch_send(self.unlib_course_sell_info_table_list, tab_name, row_key, item_data,
                            self.batch_size)
            # self.logger.info('ScoreItem save - row_key: {}, item_data: {}'.format(row_key, item_data))

    @staticmethod
    def to_md5(items):
        return md5(str(dict(items)).encode('utf8')).hexdigest()

    def batch_send(self, li, tab_name, row_key, item_data, batch_size):
        li.append((row_key, item_data))
        #print(len(li))
        if len(li) >= batch_size:
            try:
                connection = KerberosConnection(HBASE_HOST, protocol='compact', use_kerberos=True, table_prefix=HBASE_TABLE_PREFIX, table_prefix_separator=HBASE_TABLE_PREFIX_SEPARATOR, sasl_service_name='hbase')
                tab = connection.table(tab_name)
                batch = tab.batch()
                for r_k, i_d in li:
                    batch.put(r_k, i_d)
                batch.send()
                connection.close()
            except Exception as e:
                connection = KerberosConnection(HBASE_HOST, protocol='compact', use_kerberos=True,
                                                table_prefix=HBASE_TABLE_PREFIX,
                                                table_prefix_separator=HBASE_TABLE_PREFIX_SEPARATOR,
                                                sasl_service_name='hbase')
                schema = {
                    'info': dict(max_versions=3)
                }
                connection.create_table(tab_name, schema)
                tab = connection.table(tab_name)
                batch = tab.batch()
                for r_k, i_d in li:
                    batch.put(r_k, i_d)
                batch.send()
                connection.close()
            finally:
                del li[:]

    def batch_send_(self, tab_name, li):
        connection = KerberosConnection(HBASE_HOST, protocol='compact', use_kerberos=True, table_prefix=HBASE_TABLE_PREFIX, table_prefix_separator=HBASE_TABLE_PREFIX_SEPARATOR, sasl_service_name='hbase')
        tab = connection.table(tab_name)
        batch = tab.batch()
        for r_k, i_d in li:
            batch.put(r_k, i_d)
        batch.send()
        connection.close()

    def close_spider(self, spider):
        if self.unlib_course_info_table_list:
            self.batch_send_(self.unlib_course_info_table_, self.unlib_course_info_table_list)
        if self.unlib_course_screenshot_info_table_list:
            self.batch_send_(self.unlib_course_screenshot_info_table_, self.unlib_course_screenshot_info_table_list)
        if self.unlib_course_tag_info_table_list:
            self.batch_send_(self.unlib_course_tag_info_table_, self.unlib_course_tag_info_table_list)
        if self.unlib_course_sell_info_table_list:
            tb_name = f'course_sell_{time.strftime("%Y%m%d")}'
            self.batch_send_(tb_name, self.unlib_course_sell_info_table_list)

        # 关闭连接

        # self.redis_conn.close()
        # self.connect.close()

