import os
from shutil import copyfile
cnt = 0
for folder in ['nsfw', 'normal']:
    for filename in os.listdir(folder):
        splitdir = 'dataset_split'
        split_into = os.listdir(splitdir)
        cnt = (cnt + 1) % 3
        # print(f'{folder}/{filename}', f'{splitdir}/{split_into[cnt%len(split_into)]}/{folder}/{filename}')
        try:
            os.makedirs(f'{splitdir}/{split_into[cnt%len(split_into)]}/{folder}')
        except FileExistsError:
            pass
        copyfile(f'{folder}/{filename}', f'{splitdir}/{split_into[cnt%len(split_into)]}/{folder}/{filename}')