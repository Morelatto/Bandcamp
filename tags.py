"""Script to download music collections from bandcamp.com/tags

Usage:
  tags.py [<tag>]...
  tags.py -h | --help | --version

Arguments:
  [<tag>]...    Optional tag name from all tags list.

Options:
  -h, --help    Show this help message.
  --version     Show version.
"""
import dl
import os
import requests

from bandcamp.spiders.tags import TagSpider
from docopt import docopt
from parsel import Selector
from scrapy.crawler import CrawlerProcess

# Only works when spider is called
LOG_LEVEL = 'INFO'

TAGS_URL = 'https://www.bandcamp.com/tags'
TAG_RESULTS_FILE = 'tag_results.json'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


def get_all_tags():
    all_cats, i = [], 1
    r = requests.get(TAGS_URL, headers=headers)
    if r.status_code == 200:
        sel = Selector(text=r.text)
        for cat in sel.css('#tags_cloud a'):
            name, link = cat.css('::text').get(), cat.attrib['href'][5:]
            all_cats.append((name, link))
            print(i, name)
            i += 1
    return all_cats


def execute(tags_urls):
    process = CrawlerProcess({
        'LOG_LEVEL': LOG_LEVEL
    })

    process.crawl(TagSpider, tags=';'.join(tags_urls))
    process.start()
    process.stop()


def main():
    if os.path.isfile(TAG_RESULTS_FILE):
        res = input('Tag results file found, use it?')
        if res in ('y', 'yes', ''):
            dl.tags(TAG_RESULTS_FILE)
            return
        else:
            os.remove(TAG_RESULTS_FILE)

    all_tags, args_tag, tag_urls = get_all_tags(), args['<tag>'], []
    if not args_tag:
        n = input('# ')
        if n:
            for i in n.split(','):
                tag_urls.append(all_tags[int(i) - 1][1])
    else:
        for name, url in all_tags:
            for tag in args_tag:
                if tag.lower() == name:
                    tag_urls.append(url)
                    args_tag.remove(tag)

    if not tag_urls:
        print('Tag not found', args_tag)
        return

    execute(tag_urls)
    dl.tags(TAG_RESULTS_FILE)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.2')
    main()
