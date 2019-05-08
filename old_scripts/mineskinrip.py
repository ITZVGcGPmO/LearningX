import os
import json
import urllib.request
from multiprocessing import Pool

def skinprocess(x):
    urllib.request.urlretrieve(x['url'], f'dataset/{page}/{x["id"]}.png')
for page in range(1,257):
    with Pool(processes=16) as threadpool:
        print(f'downloading page {page}')
        pgdt = json.loads(urllib.request.urlopen(f'https://api.mineskin.org/get/list/{page}?size=64').read().decode())
        os.makedirs(f'dataset/{page}')
        threadpool.map(skinprocess, pgdt['skins'])
        f = open(f'dataset/{page}/page.json', 'w')
        json.dump(pgdt, f)
        f.close()
