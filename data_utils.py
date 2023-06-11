import torch
import torchvision
from torch.utils.data import random_split

from torchvision.datasets import ImageFolder
import torchvision.transforms as transforms

def get_transforms_from_config(config: dict):
    ts = []

    size = config.get('resize', False)
    if size:
        resize_value = config.get('resize_value', (size, size))
        # print(f'using resize {resize_value}')
        ts.append(transforms.Resize(resize_value))

    hor_flip = config.get('random_horizontal_flip', False)
    if hor_flip:
        ts.append(transforms.RandomHorizontalFlip())

    rand_rot = config.get('random_rotation', False)
    if rand_rot:
        ts.append(transforms.RandomRotation(degrees=rand_rot))

    color_jitter = config.get('color_jitter', False)
    if color_jitter:
        ratio = color_jitter
        ts.append(transforms.ColorJitter(brightness=ratio, contrast=ratio, saturation=ratio, hue=ratio))

    to_tensor = config.get('to_tensor', False)
    if to_tensor:
        ts.append(transforms.ToTensor())
    
    return transforms.Compose(ts)

# dataset = ImageFolder(data_dir, transform=transformations)
# print(f"dataset size: {len(dataset)}")