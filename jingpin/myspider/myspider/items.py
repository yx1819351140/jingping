# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CourseItem(scrapy.Item):
    course_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    sell = scrapy.Field()
    original_price = scrapy.Field()
    current_price = scrapy.Field()
    teacher = scrapy.Field()
    student = scrapy.Field()
    course_hour = scrapy.Field()
    course_format = scrapy.Field()
    course_service = scrapy.Field()
    course_info = scrapy.Field()
    com = scrapy.Field()
    create_time = scrapy.Field()


class ScreenshotItem(scrapy.Item):
    com = scrapy.Field()
    type = scrapy.Field()
    url = scrapy.Field()
    create_time = scrapy.Field()


class SellItem(scrapy.Field):
    com = scrapy.Field()
    course_id = scrapy.Field()
    sell = scrapy.Field()
    create_time = scrapy.Field()


class TagItem(scrapy.Field):
    com = scrapy.Field()
    type = scrapy.Field()
    url = scrapy.Field()
    course_id = scrapy.Field()
    subject = scrapy.Field()
    sub_subject = scrapy.Field()
    season = scrapy.Field()
    class_type = scrapy.Field()
    create_time = scrapy.Field()

