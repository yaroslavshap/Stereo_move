# даталоадер с площадки

from PIL import Image
import os
from torchvision import transforms
import torch.utils.data as data
import numpy as np
import torch
import kornia


# Класс - датасет для стереоизображений
class StereoDataset2(data.Dataset):
    def __init__(self, data_folder):
        # добавляю трансформацию
        self.size = (512, 256)

        # путь до папок с изображениями
        self.left_folder = os.path.join(data_folder, 'left')
        self.right_folder = os.path.join(data_folder, 'right')
        self.depth_folder = os.path.join(data_folder, 'depth')
        # self.depth_folder = os.path.join(data_folder, 'depth')

        # получаю списки изображений
        self.filenames1 = sorted(os.listdir(self.left_folder))
        self.filenames2 = sorted(os.listdir(self.right_folder))
        self.filenames3 = sorted(os.listdir(self.depth_folder))

    def __getitem__(self, idx):
        # загружаю левую, правую и лазер изображения
        left_path = os.path.join(self.left_folder, self.filenames1[idx])
        right_path = os.path.join(self.right_folder, self.filenames2[idx])
        depth_path = os.path.join(self.depth_folder, self.filenames3[idx])

        im_left = np.array(Image.open(left_path).resize(self.size, 1)) / 255
        im_right = np.array(Image.open(right_path).resize(self.size, 1)) / 255
        im_depth = np.array(Image.open(depth_path).resize(self.size, 1)).astype(float)

        # перевожу в тензоры
        # im_left = self.img_transforms(im_left)
        # im_right = self.img_transforms(im_right)
        # im_depth = self.img_transforms(im_depth)

        return {
            'image_l': kornia.image_to_tensor(im_left),
            'image_r': kornia.image_to_tensor(im_right),
            'image_lazer': kornia.image_to_tensor(im_depth)
        }

    def __len__(self):
        return len(self.filenames1)
