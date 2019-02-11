# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import asyncio
import motor.motor_asyncio
from scrapy.utils.serialize import ScrapyJSONEncoder
_encoder = ScrapyJSONEncoder()
MONGO_CLIENT = motor.motor_asyncio.AsyncIOMotorClient('mongodb://Pony228:Pony228@ds253783.mlab.com:53783/olx_scrap')

class OlxPipeline(object):
    db = MONGO_CLIENT

    async def insert_item(self, item):
        await self.db.olx_scrap.lol.insert_one(item)

    def process_item(self, item, spider):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.insert_item(dict(item)))
        return item
