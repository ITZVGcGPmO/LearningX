from os import listdir, rename
from os.path import isfile, join, isdir
import json
pages = []
for p in listdir('dataset'):
    if isdir(f'dataset/{p}'):
        for i in listdir(f'dataset/{p}'):
            
            # print(i)
            if i.endswith('.png'):
                rename(f'dataset/{p}/{i}', f'dataset/skins/{i}')
            if i.endswith('.json'):
                with open(f'dataset/{p}/{i}') as json_data:
                    skins = json.load(json_data)['skins']
                    print(skins)
                    pages = pages + skins

json.dump(pages, open(f'dataset/pages.json', 'w'))
