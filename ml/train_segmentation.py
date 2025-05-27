import os
import json
import numpy as np
from PIL import Image, ImageDraw
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# Пути к данным
DATA_DIR = 'data/Br35H-Mask-RCNN'
IMG_DIR = os.path.join(DATA_DIR, 'TRAIN')
ANNOT_PATH = os.path.join(DATA_DIR, 'annotations_all.json')

IMG_SIZE = 256

# Трансформации
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

# Класс датасета для сегментации
class SegmentationDataset(Dataset):
    def __init__(self, img_dir, annot_path, transform=None):
        self.img_dir = img_dir
        self.transform = transform
        with open(annot_path, 'r') as f:
            self.annotations = json.load(f)
        self.img_files = [v['filename'] for v in self.annotations.values() if os.path.exists(os.path.join(img_dir, v['filename']))]

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_name = self.img_files[idx]
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path).convert('RGB')
        # Получаем полигоны для маски
        ann = [v for v in self.annotations.values() if v['filename'] == img_name][0]
        mask = Image.new('L', image.size, 0)
        for region in ann['regions']:
            if region['shape_attributes']['name'] == 'polygon':
                xy = list(zip(region['shape_attributes']['all_points_x'], region['shape_attributes']['all_points_y']))
                ImageDraw.Draw(mask).polygon(xy, outline=1, fill=1)
        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)
        mask = (mask > 0).float()
        return image, mask

# U-Net (упрощённая)
class UNet(nn.Module):
    def __init__(self):
        super().__init__()
        def CBR(in_ch, out_ch):
            return nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 3, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(inplace=True)
            )
        self.enc1 = CBR(3, 32)
        self.enc2 = CBR(32, 64)
        self.enc3 = CBR(64, 128)
        self.pool = nn.MaxPool2d(2)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.up1 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.dec2 = CBR(128, 64)
        self.dec1 = CBR(64, 32)
        self.final = nn.Conv2d(32, 1, 1)
    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        d2 = self.up2(e3)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)
        d1 = self.up1(d2)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)
        out = self.final(d1)
        return torch.sigmoid(out)

# Обучение
if __name__ == '__main__':
    dataset = SegmentationDataset(IMG_DIR, ANNOT_PATH, transform=transform)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = UNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCELoss()
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for images, masks in loader:
            images, masks = images.to(device), masks.to(device)
            preds = model(images)
            loss = criterion(preds, masks)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {total_loss/len(loader):.4f}")
    torch.save(model.state_dict(), 'ml/unet_brain_segmentation.pth')
    print('Модель сегментации сохранена в ml/unet_brain_segmentation.pth') 