import os
import cv2
import torch
import numpy as np
from typing import List, Tuple
from src.io.io import read_rgb
from torch.utils.data import Dataset


class RoadDataset(Dataset):
    
    def __init__(self, data_dir, classes: List[str], train=True, transform=None, test_mode=False):
        
        data_dir = os.path.join(data_dir, "train" if train else "val")
        self.images = [os.path.join(data_dir, img, img) for img in os.listdir(data_dir) if img != ".DS_Store"]
        if test_mode:
            print("[ALERT] Using dataset in test mode, reducing number of images to 32.")
            self.images = self.images[:32]
        
        if classes is None:
            print("Plase specify at least one class among crack, lane and pothole.}")
            quit()
        self.classes = classes
        # convert str names to class values on masks        
        self.transform = transform
        
    def __getitem__(self, i) -> Tuple[torch.Tensor, torch.Tensor]:
        
        # getting image
        image = read_rgb(f"{self.images[i]}_RAW.jpg")
    
        # creating masks
        masks = [cv2.imread(f"{self.images[i]}_{c.upper()}.png") for c in self.classes]
        for i, mask in enumerate(masks):
            mask = mask == 255
            masks[i] = mask[..., 0]
        mask = np.stack(masks, axis=-1).astype('float')
        
        # apply augmentations
        if self.transform:
            sample = self.transform(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']
        
        # casting to Torch.Tensor
        image = torch.from_numpy(image.transpose(2, 0, 1))
        mask = torch.from_numpy(mask.transpose(2, 0, 1)).long()
        
        return image, mask
        
    def __len__(self):
        return len(self.images)
        