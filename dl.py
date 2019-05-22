import subprocess
from pymongo import MongoClient

# from scrapy import cmdline

# cmd = "scrapy crawl daily".split()
# cmdline.execute(cmd)

c = MongoClient()
db = c['bandcamp']
coll = db['daily']

DL_DIR = 'dls/'

for doc in coll.find({'to_dl': {'$exists': True}, 'dl': {'$ne': True}}):
    for to in doc['to_dl']:
        print('Downloading', to)
        res = subprocess.call(
            ["bandcamp-dl", "--base-dir=" + DL_DIR, "--embed-lyrics", "--embed-art", "--no-slugify", to])
        if not res:
            print(to, 'failed', res)
        else:
            res2 = coll.update_one(doc, {'$rename': {'to_dl': 'dl'}})
            print(res2.matched_count)
