"""Usage:
  tags.py [<tag>]
  tags.py -h | --help | --version
"""
import json
import requests

from docopt import docopt
from parsel import Selector
from scrapy import cmdline

TAGS_URL = 'https://www.bandcamp.com/tags'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}

cmd = ["scrapy", "crawl", "tags", "-a"]


def get_all_tags():
    all_cats, i = [], 1
    r = requests.get(TAGS_URL, headers=headers)
    if r.status_code == 200:
        sel = Selector(text=r.text)
        for cat in sel.css('#tags_cloud a'):
            name, link = cat.css('::text').get(), cat.attrib['href']
            all_cats.append((name, link))
            print(i, name)
            i += 1
    return all_cats


def main():
    tags, tag_url = get_all_tags(), None
    cmd.append('all_tags=' + json.dumps([t[1] for t in tags]))
    if not args['<tag>']:
        # TODO parse 1-5
        n = input('# ')
        if n:
            tag_url = tags[int(n) - 1][1]
    else:
        for name, url in tags:
            if args['<tag>'].lower() == name:
                tag_url = url

    if not tag_url:
        print('Tag not found', args['<tag>'])
        return

    cmd.append('-a')
    cmd.append('tag=' + tag_url)

    cmdline.execute(cmd)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main()
