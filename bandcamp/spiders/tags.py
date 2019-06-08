# -*- coding: utf-8 -*-
import scrapy

from bandcamp.items import BcTagPageLoader

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


class TagSpider(scrapy.Spider):
    name = 'tags'
    allowed_domains = [BANDCAMP]
    custom_settings = {
        'FEED_URI': 'tag_results.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def __init__(self, tags='', **kwargs):
        super().__init__(**kwargs)
        self.tags = tags.split(';')

    def start_requests(self):
        for tag in self.tags:
            yield scrapy.Request('https://{}/tag/{}'.format(BANDCAMP, tag))

    def parse(self, response):
        loader = BcTagPageLoader(response=response)
        loader.add_css('genre', TAG_GENRE)
        loader.add_css('summary', TAG_DESCRIPTION)
        loader.add_css('related_tags', RELATED_TAGS)
        self.add_all_releases(loader)
        return loader.load_item()

    def add_all_releases(self, loader):
        for col in loader.selector.css('.col.item'):
            artist = col.css(ARTIST_NAME)
            album = col.css(ALBUM_NAME)
            if artist and album:
                loader.add_value('all_releases', {
                    'artist': artist.get(),
                    'album': album.get()
                })
