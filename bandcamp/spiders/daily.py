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
    allowed_domains = ['daily.bandcamp.com']
    start_urls = ['http://daily.bandcamp.com/?s=']

    def parse(self, response):
        for post in response.css('.hentry'):
            title = post.css(POST_TITLE)
            yield self.get_post_item(post)
            # yield scrapy.Request(title.attrib['href'], self.parse_music)

        older = response.css('.nav-previous a').get()
        if older:
            self.logger.info("yield scrapy.Request(older.attrib['href'])")

    def get_post_item(self, post):
        il = BcDailyPostLoader(selector=post)
        il.add_css('title', POST_TITLE + TEXT_SEL)
        il.add_css('url', POST_TITLE + ATTR_SEL % 'href')
        il.add_css('published', POST_DATE + ATTR_SEL % 'title')
        il.add_css('content', POST_CONTENT + TEXT_SEL)
        il.add_css('tags', POST_TAGS + TEXT_SEL)
        il.add_css('author', POST_AUTHOR + ATTR_SEL % 'href')
        return il.load_item()
