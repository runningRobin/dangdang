# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    comments = scrapy.Field()
    time = scrapy.Field()
    price = scrapy.Field()
    discount = scrapy.Field()
    category_one = scrapy.Field()
    category_two = scrapy.Field()
