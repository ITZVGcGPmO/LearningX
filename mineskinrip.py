import os
import json
import urllib.request
from multiprocessing import Pool
from subprocess import check_output

def skinprocess(x):
    urllib.request.urlretrieve(x['url'], f'skins/{x["id"]}.png')
    open(f'dataset/sfw/{x["id"]}.png', 'wb').write(check_output(['php', 'render.php', f'{x["id"]}.png', 'front', 'true']))
for page in range(14,20+1):
    with Pool(processes=16) as threadpool:
        print(f'downloading page {page}')
        pgdt = json.loads(urllib.request.urlopen(f'https://api.mineskin.org/get/list/{page}?size=64').read().decode())
        threadpool.map(skinprocess, pgdt['skins'])
