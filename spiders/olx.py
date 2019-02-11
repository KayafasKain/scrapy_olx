import scrapy
import re
import json
from ..items import OlxItem
import datetime



class OlxSpider(scrapy.Spider):
    name = 'olx'
    start_urls = ['https://www.olx.ua/zapchasti-dlya-transporta/']
    profile_template_url = 'https://m.olx.ua/api/v1/users/'
    offers_template_url = 'https://m.olx.ua/api/v1/offers/'
    phone_url = 'https://www.olx.ua/ajax/misc/contact/phone/'

    def parse(self, response): # parsing manin page
        pages_for_scrap = 5
        current_page = 0
        max_pages = int(response.xpath('//a[contains(@data-cy, "page-link-last")]/span/text()').extract_first())
        if max_pages < pages_for_scrap:
            pages_for_scrap = max_pages
        href = response.request.url
        while(current_page < pages_for_scrap):
            current_page += 1
            print(current_page)
            yield scrapy.Request(href + '?page=' + str(current_page), callback=self.parse_page)



    def parse_page(self, response):
        for href in response.xpath('//a[contains(@class, "detailsLink")]/@href').extract():
            yield scrapy.Request(href, callback=self.parse_item, meta={'href': re.findall(r'(^[A-z:\/.0-9-]+)', href)[0],
                                                                       'phone_id': re.findall(r'-ID([0-9A-z]+)', href)[0]})


    def parse_item(self, response):
        href = response.meta.get('href')
        phone_id = response.meta.get('phone_id')
        item = OlxItem()
        item['title'] = self.parse_title(response)
        item['item_id'] = re.findall(r"[0-9]+", self.parse_item_id(response))
        phone_token = re.findall("var phoneToken = '(.*?)'", response.body.decode())[0]
        if phone_token:
            yield scrapy.Request(self.phone_url + phone_id + '/?pt=' + phone_token, callback=self.parse_user_phone, meta={'item': item, 'phone_id': phone_id}, headers={
                'Host': 'www.olx.ua',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': href,
            })
        else:
            yield

    def parse_user_id(self, response):
        item = response.meta.get('item')
        pt = response.meta.get('pt')
        jsonresponse = json.loads(response.body_as_unicode())
        item['user_id'] = jsonresponse['data']['user']['id']
        print(jsonresponse)
        yield item
        # yield scrapy.Request(self.profile_template_url + str(item['user_id']), callback=self.parse_user_phone, meta={'item': item}, headers={'authorization': 'Bearer ' + pt})

    def parse_user_phone(self, response):
        item = response.meta.get('item')
        jsonresponse = json.loads(response.body_as_unicode())
        item['user_phone'] = jsonresponse['value']

        yield item

    def parse_title(self, response):
        return response.selector.xpath(
            '//div[contains(@class, "offer-titlebox")]/h1/text()'
            ).extract_first()

    def parse_item_id(self, response):
        return response.selector.xpath(
            '//div[contains(@class, "offer-titlebox__details")]/em/small'
            ).extract_first()

