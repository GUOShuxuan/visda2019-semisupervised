import torch
import torch.utils.data as data
from PIL import Image
import os
import random
import numpy as np
from lib.config import cfg


def default_loader(path):
    return Image.open(path).convert('RGB')


def make_dataset(root, list_path):
    images = []
    listtxt = open(list_path)
    for line in listtxt:
        data = line.strip().split(' ')
        path = os.path.join(root, data[0])
        try:
            label = int(data[1])
        except Exception:
            label = -1
        item = (path, label)
        images.append(item)
    return images


class ListLoader(data.Dataset):
    def __init__(self, root, list_path, transform=None, loader=default_loader):
        if isinstance(list_path, str):
            imgs = make_dataset(root, list_path)
            self.imgs = imgs
        elif isinstance(list_path, list):
            list_path = [[os.path.join(root, m[0]), m[1]] for m in list_path]
            self.imgs = list_path

        self.root = root
        self.transform = transform
        self.loader = loader

    def __getitem__(self, index):
        path, target = self.imgs[index]
        img = self.loader(path)

        if self.transform is not None:
            img = self.transform(img)
        return img, target

    def __len__(self):
        return len(self.imgs)
