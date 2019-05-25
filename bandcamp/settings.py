# -*- coding: utf-8 -*-

BOT_NAME = 'bandcamp'

SPIDER_MODULES = ['bandcamp.spiders']
NEWSPIDER_MODULE = 'bandcamp.spiders'

USER_AGENT = \
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
AUTOTHROTTLE_DEBUG = True


TELNETCONSOLE_ENABLED = False
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

ITEM_PIPELINES = {
    'scrapy_mongodb.MongoDBPipeline': 300,
}

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'bandcamp'
MONGODB_ADD_TIMESTAMP = True
