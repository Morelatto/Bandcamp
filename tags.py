"""Usage:
  tags.py [<tag>]
  tags.py -h | --help | --version
"""
import json

from docopt import docopt
from scrapy import cmdline

TAGS_FILE = 'tags.txt'

cmd = ["scrapy", "crawl", "tags", "-a"]


def get_tags_on_file():
    tags = []
    with open(TAGS_FILE) as f:
        i = 1
        for tag in f.readlines():
            name, url = tag.split(',')
            tags.append((name, url.strip()))
            print(i, name)
            i += 1
    return tags


def main():
    tags = get_tags_on_file()
    cmd.append('all_tags=' + json.dumps([t[1] for t in tags]))
    if not args['<tag>']:
        # TODO parse 1-5
        n = input('# ')
        if n:
            tag_url = tags[int(n)][1]
    else:
        for name, url in tags:
            if args['<tag>'].lower() == name:
                tag_url = url
    cmd.append('-a')
    cmd.append('tag=' + tag_url)

    cmdline.execute(cmd)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main()
