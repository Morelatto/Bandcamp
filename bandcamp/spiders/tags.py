# -*- coding: utf-8 -*-
import json
import scrapy

from bandcamp.items import BcTagPageRow, BcTagPageLoader

BANDCAMP = 'bandcamp.com'

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'

POST_TITLE = '.entry-title a'
POST_DATE = '.published'
POST_CONTENT = '.entry-content *'
POST_TAGS = '.tag-links a'
POST_AUTHOR = '.author a'

TO_SKIP = ['from the bandcamp daily']


class DailySpider(scrapy.Spider):
    name = 'tags'
    allowed_domains = [BANDCAMP]
    custom_settings = {'MONGODB_COLLECTION': 'tags'}

    def __init__(self, tag=None, all_tags=None, **kwargs):
        super().__init__(**kwargs)
        self.urls = [tag] if tag else json.loads(all_tags)

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request('https://' + BANDCAMP + url)

    def parse(self, response):
        loader = BcTagPageLoader(response=response)
        loader.add_css('genre', '.row .name span' + TEXT_SEL)
        loader.add_css('summary', '.description *' + TEXT_SEL)
        loader.add_css('related_tags', '.related-tags a' + TEXT_SEL)
        self.add_page_rows(loader)
        return loader.load_item()

    def add_page_rows(self, loader):
        for row in loader.selector.css('.carousel-wrapper'):
            title = row.css('.carousel-title' + TEXT_SEL).get().strip()
            if title not in TO_SKIP:
                to_dl = []
                for col in row.css('.col'):
                    artist = col.css('*[data-bind="text: artist"]' + TEXT_SEL).get()
                    album = col.css('*[data-bind="text: title"]' + TEXT_SEL).get()
                    to_dl.append((artist, album))
                loader.add_value('page_rows', BcTagPageRow(title=title, to_dl=to_dl))

    # TODO parse dig deeper
