# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class OlxItem(scrapy.Item):
    title = scrapy.Field()
    item_id = scrapy.Field()
    user_id = scrapy.Field()
    user_phone = scrapy.Field()


