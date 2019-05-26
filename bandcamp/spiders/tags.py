# -*- coding: utf-8 -*-
import json
import scrapy

from bandcamp.items import BcTagPageRow, BcTagPageLoader

BANDCAMP = 'bandcamp.com'

TEXT_SEL = '::text'

TAG_GENRE = '.row .name span' + TEXT_SEL
TAG_DESCRIPTION = '.description *' + TEXT_SEL
RELATED_TAGS = '.related-tags a' + TEXT_SEL
ALL_ROWS = '.carousel-wrapper'
ROW_TITLE = '.carousel-title' + TEXT_SEL
COL_OF_ROW = '.col'
ARTIST_NAME = '*[data-bind="text: artist"]' + TEXT_SEL
ALBUM_NAME = '*[data-bind="text: title"]' + TEXT_SEL

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
        loader.add_css('genre', TAG_GENRE)
        loader.add_css('summary', TAG_DESCRIPTION)
        loader.add_css('related_tags', RELATED_TAGS)
        self.add_page_rows(loader)
        return loader.load_item()

    def add_page_rows(self, loader):
        for row in loader.selector.css(ALL_ROWS):
            title = row.css(ROW_TITLE).get().strip()
            if title not in TO_SKIP:
                to_dl = []
                for col in row.css(COL_OF_ROW):
                    artist = col.css(ARTIST_NAME).get()
                    album = col.css(ALBUM_NAME).get()
                    to_dl.append((artist, album))
                loader.add_value('page_rows', BcTagPageRow(title=title, to_dl=to_dl))

    # TODO parse dig deeper
