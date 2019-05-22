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

    def parse(self, response):
        for post in response.css('.hentry'):
            title = post.css(POST_TITLE)
            yield self.parse_post_info(post)
            yield scrapy.Request(title.attrib['href'], self.parse_post_links)

        older = response.css('.nav-previous a').get()
        if older:
            self.logger.info("yield scrapy.Request(older.attrib['href'])")

    def parse_post_info(self, post):
        il = BcDailyPostLoader(selector=post)
        il.add_css('title', POST_TITLE + TEXT_SEL)
        il.add_css('url', POST_TITLE + ATTR_SEL % 'href')
        il.add_css('published', POST_DATE + ATTR_SEL % 'title')
        il.add_css('content', POST_CONTENT + TEXT_SEL)
        il.add_css('tags', POST_TAGS + TEXT_SEL)
        il.add_css('author', POST_AUTHOR + ATTR_SEL % 'href')
        return il.load_item()

    def parse_post_links(self, response):
        to_dl = []
        for link in response.css('.entry-content *' + ATTR_SEL % 'href').getall():
            if '.bandcamp' in link:
                if '/album/' in link or 'daily.bandcamp.com' not in link:
                    to_dl.append(link)
        yield {'to_dl': to_dl}
