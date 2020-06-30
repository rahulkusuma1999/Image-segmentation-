# -*- coding: utf-8 -*-
"""Image segmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HL8hXTih-PTJl9347P7TaN7FG6iLZbhk
"""

# Commented out IPython magic to ensure Python compatibility.
# %reload_ext autoreload
# %autoreload 2
# %matplotlib inline

from fastai.vision import *
from fastai.callbacks.hooks import *
from fastai.utils.mem import *

path=untar_data(URLs.CAMVID)
path.ls()

path_lbl=path/'labels'
path_img=path/'images'

fnames=get_image_files(path_img)  #returns images in the file provided
fnames[:3]  # to get first three

lbl_names=get_image_files(path_lbl)  #returns labels

lbl_names[1:4]

"""Show image"""

img_file=fnames[0]

img=open_image(img_file)
img.show(figsize=(7,7))

get_y_fn=lambda x:path_lbl/f'{x.stem}_P{x.suffix}'  # to get the file label

mask=open_mask(get_y_fn(img_file))

mask.show(figsize=(7,7),alpha=1)  # segmented image

src_size=np.array(mask.shape[1:])

src_size,mask.data

codes=np.loadtxt(path/'codes.txt',dtype=str)  #items
codes



"""DATASETS"""

size=src_size//2
free=gpu_mem_get_used_no_cache() # the max size of bs depends on the available GPU RAM
if free >8200 :bs=8
else: bs=4
print(bs)

src=(SegmentationItemList.from_folder(path_img)
      .split_by_fname_file('../valid.txt')
      .label_from_func(get_y_fn,classes=codes))

data=(src.transform(get_transforms(),size=size,tfm_y=True)
       .databunch(bs=bs)
       .normalize(imagenet_stats))

data.show_batch(2,figsize=(7,7))  #show segmented image

data.show_batch(2, figsize=(10,7), ds_type=DatasetType.Valid)

name2id = {v:k for k,v in enumerate(codes)}
void_code = name2id['Void']

def acc_camvid(input, target):
    target = target.squeeze(1)
    mask = target != void_code
    return (input.argmax(dim=1)[mask]==target[mask]).float().mean()

metric=acc_camvid

wd= 1e-2  #weight decay

learn=unet_learner(data,models.resnet34,metrics=metric,wd=wd)

learn.lr_find()

learn.recorder.plot()

lr=3e-3

learn.fit_one_cycle(10,slice(lr),pct_start=0.9)

learn.save('stage-1')

learn.load('stage-1');

learn.show_results(rows=3, figsize=(8,9))

