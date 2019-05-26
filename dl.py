import multiprocessing
import os
import pymongo

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader
from slugify import slugify

DL_DIR = 'dls/'
THREADS = 8
DEFAULT_TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'

bandcamp = Bandcamp()


def bc_dl(args):
    base_dir, url = args
    try:
        album = bandcamp.parse(url, lyrics=True)
        bandcamp_downloader = BandcampDownloader(DEFAULT_TEMPLATE, base_dir, False, True, False, True, False, False,
                                                 url)
        print('Downloading', url)
        bandcamp_downloader.start(album)
        return url
    except Exception as e:  # FIXME AttributeError
        print('Failed', url, e)


def get(urls, base_dir=DL_DIR):
    return pool.map(bc_dl, [(base_dir, url) for url in urls])


def get_album_url(artist, album):
    return "http://{}.bandcamp.com/album/{}".format(slugify(artist), slugify(album))


def daily():
    posts = db['daily'].find({'to_dl': {'$exists': True}, 'dl': {'$ne': True}}).sort('published', -1)
    for p in posts:
        # TODO check if download success and update_one(doc, {'$rename': {'to_dl': 'dl'}})
        res = get(p['to_dl'])
        print('Updating on db', res)
        db['daily'].update_many({'to_dl': {'$in': res}}, {'$rename': {'to_dl': 'dl'}})


def tags():
    genres = db['tags'].find({'page_rows.to_dl': {'$exists': True}, 'dl': {'$ne': True}})[:1]
    for g in genres:
        for row in g['page_rows']:
            dl_dir = os.path.join(DL_DIR, g['genre'], row['title'])
            os.makedirs(dl_dir, exist_ok=True)
            get([get_album_url(to[0], to[1]) for to in row['to_dl']], dl_dir)


if __name__ == '__main__':
    c = pymongo.MongoClient()
    db = c['bandcamp']
    pool = multiprocessing.Pool(processes=THREADS)

    os.makedirs(DL_DIR, exist_ok=True)
    daily()
