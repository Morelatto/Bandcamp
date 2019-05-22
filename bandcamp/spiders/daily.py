# -*- coding: utf-8 -*-

import scrapy
from bandcamp.items import BcDailyPostLoader

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'

POST_TITLE = '.entry-title a'
POST_DATE = '.published'
POST_CONTENT = '.entry-content *'
POST_TAGS = '.tag-links a'
POST_AUTHOR = '.author a'


class DailySpider(scrapy.Spider):
    name = 'daily'
    allowed_domains = ['bandcamp.com']
    start_urls = ['http://daily.bandcamp.com/?s=']
    custom_settings = {'MONGODB_COLLECTION': 'daily'}

    def parse(self, response):
        for post in response.css('.hentry'):
            link = post.css(POST_TITLE).attrib['href']
            loader = BcDailyPostLoader(selector=post)
            self.add_post_info(loader)
            yield scrapy.Request(link, self.parse_post_links, meta={'loader': loader})

        older = response.css('.nav-previous a')
        if older:
            yield scrapy.Request(older.attrib['href'])

    def add_post_info(self, loader):
        loader.add_css('url', POST_TITLE + ATTR_SEL % 'href')
        loader.add_css('title', POST_TITLE + TEXT_SEL)
        loader.add_css('published', POST_DATE + ATTR_SEL % 'title')
        loader.add_css('content', POST_CONTENT + TEXT_SEL)
        loader.add_css('tags', POST_TAGS + TEXT_SEL)
        loader.add_css('author', POST_AUTHOR + ATTR_SEL % 'href')

    def parse_post_links(self, response):
        to_dl = []
        for link in response.css('.entry-content *' + ATTR_SEL % 'href').getall():
            if '.bandcamp' in link:
                if '/album/' in link or 'daily.bandcamp.com' not in link:
                    to_dl.append(link)
        loader = response.meta['loader']
        loader.add_value('to_dl', to_dl)
        return loader.load_item()
